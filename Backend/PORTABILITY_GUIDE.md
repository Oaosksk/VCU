# ML Model Database - Portability Guide

## 📦 EXPORT FROM TRAINING PC

### Step 1: Export Database
```bash
cd Backend
mysqldump -u root ml_model_store > ml_model_store_export.sql
```

### Step 2: Copy Required Files
Copy these files to USB/cloud:
- `ml_model_store_export.sql` (database export)
- `weights/yolov8s.pt` (YOLOv8 model file)
- `scripts/config.py` (configuration)
- `scripts/db_utils.py` (database utilities)
- `scripts/inference_from_db.py` (inference script)
- `pyproject.toml` (dependencies)

---

## 💻 IMPORT ON LOW-END PC

### Prerequisites
- XAMPP installed (MySQL running)
- Python 3.11 installed
- uv package manager installed: `pip install uv`

### Step 1: Setup Project Structure
```bash
mkdir accident-detection
cd accident-detection
mkdir Backend
cd Backend
mkdir scripts weights
```

### Step 2: Copy Files
Place files in correct locations:
```
Backend/
├── ml_model_store_export.sql
├── pyproject.toml
├── yolov8s.pt              # Place at Backend root
└── scripts/
    ├── config.py
    ├── db_utils.py
    └── inference_from_db.py
```

### Step 3: Import Database
```bash
mysql -u root < ml_model_store_export.sql
```

Verify:
```bash
mysql -u root -e "SHOW DATABASES;"
mysql -u root -e "USE ml_model_store; SHOW TABLES;"
```

### Step 4: Install Dependencies
```bash
cd Backend
uv sync
```

### Step 5: Update Config (if needed)
Edit `scripts/config.py`:
- `DB_HOST` - Usually "localhost"
- `DB_USER` - Usually "root"
- `DB_PASSWORD` - Your MySQL password
- `YOLO_PATH` - Should be "./yolov8s.pt" (relative path, file at Backend root)

### Step 6: Run Inference
```bash
uv run scripts/inference_from_db.py
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Database imported: `mysql -u root -e "USE ml_model_store; SELECT COUNT(*) FROM models;"`
- [ ] YOLOv8 file exists: `ls weights/yolov8s.pt`
- [ ] Dependencies installed: `uv sync` completes without errors
- [ ] Config updated: Check `scripts/config.py` paths
- [ ] Inference works: `uv run scripts/inference_from_db.py` runs successfully

---

## 🔧 TROUBLESHOOTING

### Error: "Database connection failed"
- Check XAMPP MySQL is running
- Verify credentials in `config.py`
- Test: `mysql -u root -e "SELECT 1;"`

### Error: "Model not found in database"
- Check: `mysql -u root -e "USE ml_model_store; SELECT * FROM models;"`
- Verify model_name and model_version in inference script

### Error: "YOLOv8 file not found"
- Check path in `config.py`
- Verify file exists: `ls yolov8s.pt` (should be at Backend root)
- Update YOLO_PATH to: `"./yolov8s.pt"`

### Error: "No module named 'mysql.connector'"
- Run: `uv sync`
- Verify: `uv pip list | grep mysql`

---

## 📝 NOTES

- **No GPU required** - Model runs on CPU automatically
- **No retraining needed** - Model weights stored in database
- **Portable** - Works on any PC with XAMPP + Python 3.11
- **Self-contained** - Only external file is yolov8s.pt
