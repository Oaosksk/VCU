"""Database utility functions for ML model storage"""
import mysql.connector
import hashlib
import json
import pickle
from pathlib import Path
from scripts.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CHUNK_SIZE


def get_db_connection():
    """Create MySQL database connection"""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def save_model_to_db(model_path, model_name, model_version, model_type, architecture, 
                     training_config, training_history, evaluation, dataset_info, 
                     label_mappings, feature_defs, env_info, preprocessing_objs=None):
    """Save complete trained model to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert model registry
        cursor.execute("""
            INSERT INTO models (model_name, model_version, model_type, description, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (model_name, model_version, model_type, f"Trained {model_type} model", True))
        model_id = cursor.lastrowid
        
        # 2. Save model file (chunked)
        with open(model_path, 'rb') as f:
            file_data = f.read()
        file_hash = hashlib.md5(file_data).hexdigest()
        chunks = [file_data[i:i+CHUNK_SIZE] for i in range(0, len(file_data), CHUNK_SIZE)]
        total_chunks = len(chunks)
        
        for idx, chunk in enumerate(chunks):
            cursor.execute("""
                INSERT INTO model_files (model_id, chunk_index, chunk_data, chunk_size, total_chunks, file_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (model_id, idx, chunk, len(chunk), total_chunks, file_hash))
        
        # 3. Save architecture
        cursor.execute("""
            INSERT INTO model_architecture (model_id, input_size, hidden_size, num_layers, output_size, dropout_rate, architecture_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (model_id, architecture['input_size'], architecture['hidden_size'], 
              architecture['num_layers'], architecture['output_size'], 
              architecture.get('dropout_rate'), json.dumps(architecture)))
        
        # 4. Save training config
        cursor.execute("""
            INSERT INTO training_config (model_id, optimizer, learning_rate, batch_size, epochs, loss_function, config_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (model_id, training_config['optimizer'], training_config['learning_rate'],
              training_config['batch_size'], training_config['epochs'],
              training_config.get('loss_function', 'BCELoss'), json.dumps(training_config)))
        
        # 5. Save training metrics
        for epoch_data in training_history:
            cursor.execute("""
                INSERT INTO training_metrics (model_id, epoch, train_loss, train_accuracy, val_loss, val_accuracy)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (model_id, epoch_data['epoch'], epoch_data['train_loss'],
                  epoch_data.get('train_accuracy'), epoch_data.get('val_loss'),
                  epoch_data.get('val_accuracy')))
        
        # 6. Save evaluation
        cursor.execute("""
            INSERT INTO model_evaluation (model_id, test_accuracy, test_loss, precision_score, recall_score, f1_score, confusion_matrix, evaluation_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (model_id, evaluation['test_accuracy'], evaluation.get('test_loss'),
              evaluation.get('precision'), evaluation.get('recall'), evaluation.get('f1'),
              json.dumps(evaluation.get('confusion_matrix')), json.dumps(evaluation)))
        
        # 7. Save dataset info
        cursor.execute("""
            INSERT INTO dataset_info (model_id, total_samples, train_samples, test_samples, num_classes, class_distribution, dataset_path, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (model_id, dataset_info['total_samples'], dataset_info['train_samples'],
              dataset_info['test_samples'], dataset_info['num_classes'],
              json.dumps(dataset_info.get('class_distribution')),
              dataset_info.get('dataset_path'), dataset_info.get('notes')))
        
        # 8. Save label mappings
        for class_idx, class_label in label_mappings.items():
            cursor.execute("""
                INSERT INTO label_mappings (model_id, class_index, class_label)
                VALUES (%s, %s, %s)
            """, (model_id, class_idx, class_label))
        
        # 9. Save feature definitions
        for feat in feature_defs:
            cursor.execute("""
                INSERT INTO feature_definitions (model_id, feature_name, feature_index, feature_type, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (model_id, feat['name'], feat['index'], feat.get('type'), feat.get('description')))
        
        # 10. Save preprocessing objects
        if preprocessing_objs:
            for obj_name, obj_data in preprocessing_objs.items():
                pickled = pickle.dumps(obj_data)
                cursor.execute("""
                    INSERT INTO preprocessing_objects (model_id, object_name, object_type, object_data)
                    VALUES (%s, %s, %s, %s)
                """, (model_id, obj_name, type(obj_data).__name__, pickled))
        
        # 11. Save environment snapshot
        cursor.execute("""
            INSERT INTO environment_snapshot (model_id, python_version, os_platform, cpu_info, gpu_info, cuda_version, pytorch_version, packages_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (model_id, env_info['python_version'], env_info['os_platform'],
              env_info.get('cpu_info'), env_info.get('gpu_info'),
              env_info.get('cuda_version'), env_info.get('pytorch_version'),
              json.dumps(env_info.get('packages', []))))
        
        conn.commit()
        print(f"✅ Model saved to database with ID: {model_id}")
        return model_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error saving model to database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def load_model_from_db(model_name, model_version):
    """Load complete model from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Get model ID
        cursor.execute("""
            SELECT model_id FROM models 
            WHERE model_name = %s AND model_version = %s AND is_active = TRUE
        """, (model_name, model_version))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Model {model_name} v{model_version} not found")
        model_id = result['model_id']
        
        # 2. Load model file chunks
        cursor.execute("""
            SELECT chunk_index, chunk_data, total_chunks, file_hash
            FROM model_files WHERE model_id = %s ORDER BY chunk_index
        """, (model_id,))
        chunks = cursor.fetchall()
        file_data = b''.join([c['chunk_data'] for c in chunks])
        
        # 3. Load architecture
        cursor.execute("SELECT * FROM model_architecture WHERE model_id = %s", (model_id,))
        architecture = cursor.fetchone()
        
        # 4. Load label mappings
        cursor.execute("SELECT class_index, class_label FROM label_mappings WHERE model_id = %s", (model_id,))
        labels = {row['class_index']: row['class_label'] for row in cursor.fetchall()}
        
        # 5. Load preprocessing objects
        cursor.execute("SELECT object_name, object_data FROM preprocessing_objects WHERE model_id = %s", (model_id,))
        preprocess_objs = {row['object_name']: pickle.loads(row['object_data']) for row in cursor.fetchall()}
        
        return {
            'model_id': model_id,
            'model_data': file_data,
            'architecture': architecture,
            'labels': labels,
            'preprocessing': preprocess_objs
        }
        
    finally:
        cursor.close()
        conn.close()


def log_inference(model_id, input_data, prediction, confidence, inference_time_ms):
    """Log inference result to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO inference_logs (model_id, input_data, prediction, confidence, inference_time_ms)
            VALUES (%s, %s, %s, %s, %s)
        """, (model_id, json.dumps(input_data), prediction, confidence, inference_time_ms))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
