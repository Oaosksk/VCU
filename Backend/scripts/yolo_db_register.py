"""Register YOLOv8 model file in database"""
import hashlib
from pathlib import Path
from scripts.config import YOLO_PATH
from scripts.db_utils import get_db_connection


def calculate_md5(file_path):
    """Calculate MD5 checksum of file"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def register_yolo_model(file_path, model_version="v8s", notes=None):
    """Register YOLOv8 model in database"""
    
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"YOLOv8 model file not found: {file_path}")
    
    print(f"Registering YOLOv8 model: {file_path}")
    print("Calculating MD5 checksum...")
    
    # Calculate checksum
    checksum = calculate_md5(file_path)
    
    # Get file info
    file_name = file_path.name
    file_path_str = str(file_path.absolute()).replace('\\', '/')
    
    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if already registered
        cursor.execute("""
            SELECT yolo_id, checksum_md5 FROM yolo_model_registry 
            WHERE file_path = %s
        """, (file_path_str,))
        
        existing = cursor.fetchone()
        
        if existing:
            yolo_id, old_checksum = existing
            if old_checksum == checksum:
                print(f"✅ Model already registered (ID: {yolo_id}) - checksum matches")
                return yolo_id
            else:
                print(f"⚠️  Model file changed - updating checksum")
                cursor.execute("""
                    UPDATE yolo_model_registry 
                    SET checksum_md5 = %s, model_version = %s, notes = %s
                    WHERE yolo_id = %s
                """, (checksum, model_version, notes, yolo_id))
                conn.commit()
                print(f"✅ Model updated (ID: {yolo_id})")
                return yolo_id
        
        # Insert new record
        cursor.execute("""
            INSERT INTO yolo_model_registry 
            (file_name, file_path, checksum_md5, model_version, framework_version, notes, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (file_name, file_path_str, checksum, model_version, 'ultralytics', notes, True))
        
        yolo_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ YOLOv8 model registered successfully (ID: {yolo_id})")
        print(f"   File: {file_name}")
        print(f"   Path: {file_path_str}")
        print(f"   MD5:  {checksum}")
        
        return yolo_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error registering model: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_yolo_model(file_path):
    """Verify YOLOv8 model file against database checksum"""
    
    file_path = Path(file_path)
    file_path_str = str(file_path.absolute()).replace('\\', '/')
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"YOLOv8 model file not found: {file_path}")
    
    # Get stored checksum
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT checksum_md5, model_version, is_active 
            FROM yolo_model_registry 
            WHERE file_path = %s
        """, (file_path_str,))
        
        record = cursor.fetchone()
        
        if not record:
            print(f"⚠️  Model not registered in database")
            return False
        
        if not record['is_active']:
            print(f"⚠️  Model is marked as inactive")
            return False
        
        # Calculate current checksum
        current_checksum = calculate_md5(file_path)
        stored_checksum = record['checksum_md5']
        
        if current_checksum == stored_checksum:
            print(f"✅ Model integrity verified (MD5 matches)")
            return True
        else:
            print(f"❌ Model integrity check FAILED")
            print(f"   Expected: {stored_checksum}")
            print(f"   Got:      {current_checksum}")
            return False
        
    finally:
        cursor.close()
        conn.close()


def main():
    """Register YOLOv8 model from config"""
    print("="*60)
    print("YOLOv8 Model Registration")
    print("="*60)
    
    try:
        yolo_id = register_yolo_model(
            file_path=YOLO_PATH,
            model_version="v8s",
            notes="YOLOv8s model for vehicle detection in accident analysis"
        )
        
        print("\n" + "="*60)
        print("Verifying model integrity...")
        print("="*60)
        
        verify_yolo_model(YOLO_PATH)
        
        print("\n✅ Registration complete!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Expected path: {YOLO_PATH}")
        print("   Please update YOLO_PATH in config.py or place the model file at the expected location")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
