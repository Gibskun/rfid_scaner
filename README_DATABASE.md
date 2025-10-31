# RFID Database & Tag Writing System

## 🎯 Overview

This RFID system now includes **PostgreSQL database integration** and **tag writing/rewriting capabilities**. You can detect tags, store them in a database with item information, and rewrite tags with new data.

## 📋 Features

### ✅ What's New
- **PostgreSQL Database Integration** - Store all detected tags
- **Tag Writing/Rewriting** - Write new EPC data to tags
- **Item Name Tracking** - Associate item names with tags
- **Write Date Tracking** - Track when tags were written
- **Database Search** - Search tags by ID or item name
- **Web API** - RESTful API for tag management
- **Interactive Tag Writer** - Easy-to-use command-line tool

### 💾 Database Schema

The system automatically creates the following tables:

#### `rfid_tags` Table
- `id` - Primary key
- `tag_id` - Unique tag identifier (hex string)
- `tag_data` - Raw tag bytes
- `item_name` - Name of the item
- `write_date` - When the tag was written
- `unwrite_date` - Reserved for future use
- `first_detected` - First detection timestamp
- `last_detected` - Most recent detection
- `detection_count` - Total number of detections
- `is_written` - Whether tag has been rewritten
- `notes` - Additional notes
- `created_at` - Record creation time
- `updated_at` - Record update time

#### `tag_detection_history` Table
- `id` - Primary key
- `tag_id` - Tag identifier
- `detected_at` - Detection timestamp
- `signal_strength` - Signal strength estimate
- `notes` - Additional notes

## 🔧 Database Configuration

The system is pre-configured with these settings:

```python
Host: localhost
Port: 5432
Username: postgres
Password: 123
Database: rfid_system
```

**To change these settings**, edit the `database.py` file:
```python
def get_database() -> RFIDDatabase:
    return RFIDDatabase(
        host='localhost',      # Change this
        port=5432,             # Change this
        username='postgres',   # Change this
        password='123',        # Change this
        database='rfid_system' # Change this
    )
```

## 🚀 Installation

### 1. Install PostgreSQL

**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer
3. Set password to `123` (or update `database.py` with your password)
4. Use default port `5432`

**Verify Installation:**
```powershell
psql --version
```

### 2. Install Python Requirements

```powershell
pip install -r requirements.txt
```

This installs:
- `psycopg2-binary` - PostgreSQL adapter
- `pyserial` - Serial communication
- `flask` & `flask-socketio` - Web interface
- Other dependencies

### 3. Database Auto-Setup

The database and tables are **automatically created** when you first run the system. No manual setup required!

## 📖 Usage

### Option 1: Interactive Tag Writer (Recommended for Tag Writing)

```powershell
python tag_writer.py
```

This opens an interactive menu:

```
🏷️  RFID Tag Writer - Interactive Mode
============================================================
Options:
1. 📡 Scan for tags
2. ✍️  Write/Rewrite a tag
3. 📊 View database statistics
4. 🔍 Search database
5. 🚪 Exit
============================================================
```

**Example Workflow:**
1. Select option 1 to scan for tags
2. Place a tag near the reader
3. Select option 2 to write a tag
4. Enter new EPC (e.g., `E2 00 12 34 56 78 90 AB CD EF 01 23`)
5. Enter item name (e.g., `Laptop Charger`)
6. Confirm and write!

### Option 2: Main System (Scanning + Database)

```powershell
python main.py
```

This runs:
- **Terminal Scanner** - Real-time tag detection
- **Web Interface** - Dashboard at http://localhost:5000
- **Database Integration** - Auto-saves all detected tags

### Option 3: Web Interface Only

```powershell
python web_interface.py
```

Access at: http://localhost:5000

**API Endpoints:**
- `GET /api/status` - Current scanning status
- `GET /api/database/stats` - Database statistics
- `GET /api/database/tags?limit=100&offset=0` - Get all tags
- `GET /api/database/search?q=laptop` - Search tags
- `GET /api/tag/<tag_id>` - Get specific tag info

## 🏷️ Tag Writing Examples

### Example 1: Simple Tag Rewrite

```python
from tag_writer import TagWriter

writer = TagWriter(port="COM5")
writer.connect()

# Scan for tags
tags = writer.scan_for_tags()

# Write the first detected tag
if tags:
    old_epc = tags[0]
    new_epc = "E2001234567890ABCDEF0123"
    item_name = "Conference Badge - John Doe"
    
    writer.write_tag(old_epc, new_epc, item_name)
```

### Example 2: Programmatic Tag Writing

```python
from main import FastRFIDScanner

scanner = FastRFIDScanner(port="COM5")
scanner.connect()

# Write a tag
old_tag_hex = "E2 00 00 00 00 00 00 00 00 00 00 01"
new_epc_hex = "E2 00 AB CD EF 12 34 56 78 90 AB CD"
item_name = "Inventory Item #12345"

scanner.write_tag(old_tag_hex, new_epc_hex, item_name)
```

### Example 3: Using Database Directly

```python
from database import get_database

db = get_database()

# Get tag info
tag_info = db.get_tag_info("E2 00 12 34 56 78 90 AB CD EF 01 23")
print(f"Item: {tag_info['item_name']}")
print(f"Written: {tag_info['is_written']}")

# Search tags
results = db.search_tags("laptop")
for tag in results:
    print(f"{tag['tag_id']}: {tag['item_name']}")

# Get statistics
stats = db.get_statistics()
print(f"Total tags: {stats['total_tags']}")
print(f"Written tags: {stats['written_tags']}")
```

## 📊 Database Queries

### View All Tags
```sql
SELECT tag_id, item_name, write_date, detection_count 
FROM rfid_tags 
ORDER BY last_detected DESC;
```

### Find Unwritten Tags
```sql
SELECT tag_id, first_detected 
FROM rfid_tags 
WHERE is_written = FALSE;
```

### Search by Item Name
```sql
SELECT * FROM rfid_tags 
WHERE item_name ILIKE '%laptop%';
```

### Recent Detections
```sql
SELECT tag_id, detected_at 
FROM tag_detection_history 
WHERE detected_at > NOW() - INTERVAL '1 hour'
ORDER BY detected_at DESC;
```

## 🔍 Troubleshooting

### Database Connection Failed
```
❌ Database connection failed: could not connect to server
```

**Solutions:**
1. Ensure PostgreSQL is running:
   ```powershell
   # Check if PostgreSQL service is running
   Get-Service -Name postgresql*
   ```

2. Verify credentials in `database.py`

3. Test connection:
   ```powershell
   psql -U postgres -h localhost -p 5432
   ```

### Tag Write Failed
```
❌ Tag write failed with status: 0x05
```

**Common causes:**
- Tag is locked (requires access password)
- Tag is out of range
- Incorrect EPC format (must be word-aligned)
- Reader power too low

**Solutions:**
1. Ensure tag is close to reader
2. Check EPC format (even number of bytes)
3. Increase reader power in code:
   ```python
   scanner.reader.set_power(30)  # Max power
   ```

### Database Tables Not Created
```
❌ Table 'rfid_tags' does not exist
```

**Solution:**
The tables should be created automatically. If not, run:
```python
from database import get_database
db = get_database()
# Tables are created in __init__
```

## 📁 File Structure

```
Reader/
├── database.py           # PostgreSQL database manager ⭐ NEW
├── tag_writer.py         # Interactive tag writing tool ⭐ NEW
├── main.py               # Updated with database integration
├── reader.py             # Updated with write_epc() method
├── web_interface.py      # Updated with database API endpoints
├── command.py            # RFID command builder
├── response.py           # RFID response parser
├── transport.py          # Serial/TCP communication
├── shared_data.py        # Shared data between processes
├── requirements.txt      # Updated with psycopg2-binary
└── README_DATABASE.md    # This file
```

## 🎓 Advanced Features

### Batch Tag Writing
```python
from tag_writer import TagWriter

writer = TagWriter()
writer.connect()

# List of tags to write
tags_to_write = [
    ("E2 00 00 00 00 01", "E2 00 AB CD 00 01", "Item A"),
    ("E2 00 00 00 00 02", "E2 00 AB CD 00 02", "Item B"),
    ("E2 00 00 00 00 03", "E2 00 AB CD 00 03", "Item C"),
]

for old_epc, new_epc, item_name in tags_to_write:
    print(f"\nWriting: {item_name}")
    writer.write_tag(bytes.fromhex(old_epc.replace(' ', '')), new_epc, item_name)
    time.sleep(1)  # Delay between writes
```

### Export Tags to CSV
```python
import csv
from database import get_database

db = get_database()
tags = db.get_all_tags(limit=1000)

with open('tags_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['tag_id', 'item_name', 'write_date', 'detection_count'])
    writer.writeheader()
    writer.writerows(tags)

print("✅ Exported to tags_export.csv")
```

## 🔐 Security Notes

1. **Default Password**: The system uses `password='123'` for PostgreSQL. **Change this in production!**

2. **Tag Access Passwords**: Currently uses default (all zeros). For locked tags, modify:
   ```python
   access_password = bytes.fromhex('12345678')  # Your 4-byte password
   writer.write_tag(old_epc, new_epc, item_name, access_password)
   ```

3. **Network Access**: Web interface binds to `0.0.0.0` (all interfaces). For production, use `127.0.0.1` (localhost only).

## 📞 Support

For issues or questions:
1. Check this README
2. Review error messages carefully
3. Check PostgreSQL logs
4. Verify tag compatibility with your reader

## 🎉 Summary

You now have a complete RFID system with:
- ✅ Real-time tag detection
- ✅ PostgreSQL database storage
- ✅ Tag writing/rewriting capability
- ✅ Web dashboard
- ✅ RESTful API
- ✅ Interactive CLI tool
- ✅ Comprehensive tracking

**Next Steps:**
1. Install PostgreSQL
2. Run `pip install -r requirements.txt`
3. Start with `python tag_writer.py`
4. Write your first tag!

Happy tagging! 🏷️
