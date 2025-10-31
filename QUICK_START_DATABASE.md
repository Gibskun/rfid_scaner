# 🚀 Quick Start - Database & Tag Writing

## Step-by-Step Setup (5 Minutes)

### 1️⃣ Install PostgreSQL

**Download and Install:**
- Go to: https://www.postgresql.org/download/windows/
- Download the installer (Windows x86-64)
- Run the installer with these settings:
  - Password: `123` (or remember to change it in `database.py`)
  - Port: `5432`
  - Install all components

### 2️⃣ Install Python Dependencies

Open PowerShell in the project folder:

```powershell
pip install -r requirements.txt
```

Wait for installation to complete. This installs:
- `psycopg2-binary` (PostgreSQL driver)
- Other required packages

### 3️⃣ Test the System

**Option A: Interactive Tag Writer (Best for beginners)**

```powershell
python tag_writer.py
```

You'll see:
```
🏷️  RFID Tag Writer - Interactive Mode
Enter COM port (default: COM5):
```

Press Enter to use COM5, or type your port (e.g., `COM3`)

**Option B: Full System (Scanner + Web + Database)**

```powershell
python main.py
```

### 4️⃣ Write Your First Tag

Using the tag writer:

1. **Scan for tags** (Option 1)
   - Place a tag near the reader
   - You'll see the detected tag ID

2. **Write a tag** (Option 2)
   - Follow the prompts
   - Enter new EPC: `E200123456789ABCDEF0123`
   - Enter item name: `Test Item`
   - Confirm with `yes`

3. **View statistics** (Option 3)
   - See total tags, written tags, etc.

## 🎯 Common Tasks

### Check Database Connection

```powershell
python -c "from database import get_database; db = get_database(); print('✅ Connected!')"
```

### View Database Statistics

```powershell
python -c "from database import get_database; db = get_database(); print(db.get_statistics())"
```

### Search for a Tag

```python
from database import get_database

db = get_database()
results = db.search_tags("Test")  # Search by tag ID or item name
for tag in results:
    print(f"{tag['item_name']}: {tag['tag_id'][:30]}...")
```

### List All Tags

```python
from database import get_database

db = get_database()
tags = db.get_all_tags(limit=10)
for tag in tags:
    status = "✅ Written" if tag['is_written'] else "⏳ Not written"
    print(f"{tag['item_name'] or 'No name'}: {status}")
```

## ❓ FAQ

**Q: What if I get "Database connection failed"?**

A: Check that PostgreSQL is running:
```powershell
Get-Service -Name postgresql*
```

If it's stopped, start it:
```powershell
Start-Service postgresql-x64-15  # Or your version
```

**Q: Can I use a different password?**

A: Yes! Edit `database.py` at the bottom:
```python
def get_database() -> RFIDDatabase:
    return RFIDDatabase(
        host='localhost',
        port=5432,
        username='postgres',
        password='YOUR_PASSWORD_HERE',  # Change this
        database='rfid_system'
    )
```

**Q: How do I reset the database?**

A: Connect to PostgreSQL and drop the database:
```powershell
psql -U postgres
DROP DATABASE rfid_system;
\q
```

Next time you run the program, it will be recreated automatically.

**Q: Can I see the database tables?**

A: Yes! Use pgAdmin (installed with PostgreSQL) or connect via command line:
```powershell
psql -U postgres -d rfid_system
\dt  # List tables
SELECT * FROM rfid_tags LIMIT 10;  # View tags
\q
```

**Q: What happens to the "unwrite_date" field?**

A: It's reserved for future functionality. Currently, only tag writing is implemented. The unwrite feature will be added in a future update.

## 🎓 Next Steps

1. ✅ Install PostgreSQL
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Test with `python tag_writer.py`
4. ✅ Write your first tag
5. 📖 Read `README_DATABASE.md` for advanced features
6. 🌐 Try the web interface at http://localhost:5000

## 🔧 Configuration Reference

### Database Config (in `database.py`)
```python
Host: localhost      # Change for remote database
Port: 5432          # Default PostgreSQL port
Username: postgres  # Database user
Password: 123       # ⚠️ CHANGE THIS IN PRODUCTION!
Database: rfid_system  # Database name (auto-created)
```

### Reader Config (in scripts)
```python
Port: COM5          # Change to your reader's COM port
Baud Rate: 57600    # Standard for most RFID readers
```

## 📊 What Gets Stored?

For each detected tag:
- 🔖 **Tag ID** - Full hex identifier
- 📦 **Item Name** - What the tag is attached to
- ✍️ **Write Date** - When the tag was programmed
- 📅 **First/Last Detected** - Detection timestamps
- 🔢 **Detection Count** - How many times seen
- ✅ **Write Status** - Whether it's been reprogrammed

## 🎉 You're Ready!

The system is now fully integrated with:
- PostgreSQL database
- Tag writing capability
- Web interface with database API
- Interactive command-line tool

Start scanning and writing tags! 🏷️
