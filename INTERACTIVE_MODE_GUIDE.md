# Interactive Tag Writing Guide

## 🎯 Overview
`main.py` now includes **built-in interactive prompts** for writing unregistered RFID tags. No need for separate scripts!

## ✨ Features
- **Automatic Detection**: When an unregistered tag is detected, scanning pauses automatically
- **Interactive Prompts**: System prompts you to write or skip the tag
- **Database Integration**: Written tags are automatically saved to PostgreSQL
- **Seamless Resumption**: After handling the tag, scanning resumes automatically

---

## 🚀 Quick Start

### 1. Start the System
```bash
python main.py
```

This single command starts:
- ✅ Terminal RFID scanner with interactive prompts
- ✅ Web dashboard on http://localhost:5000
- ✅ PostgreSQL database connection
- ✅ Real-time tag detection

---

## 📋 Interactive Workflow

### When Unregistered Tag is Detected:

```
============================================================
⚠️  UNREGISTERED TAG DETECTED!
   Tag ID: E2 00 10 70 E0 10 01 97 1D 32 43 21
============================================================

👉 (W)rite this tag or (S)kip? [W/S]: 
```

### Option 1: Write the Tag (Press W)

1. **Enter New EPC** (12 hex bytes with spaces):
   ```
   📝 Enter new EPC for this tag
      Format: 12 hex bytes with spaces (e.g., 'E2 00 12 34 56 78 90 12 34 56 78 90')
      New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
   ```

2. **Enter Item Name**:
   ```
   🏷️  Enter item name: Laptop Dell XPS 15
   ```

3. **Confirm Writing**:
   ```
   📋 Summary:
      Old Tag: E2 00 10 70 E0 10 01 97 1D 32 43 21
      New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
      Item: Laptop Dell XPS 15
   
   ✅ Confirm write? [Y/N]: Y
   ```

4. **Result**:
   ```
   📝 Writing tag...
      Old EPC: E2 00 10 70 E0 10 01 97 1D 32 43 21
      New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
      Item: Laptop Dell XPS 15
   ✅ Tag written successfully!
   ✅ Database updated for tag: Laptop Dell XPS 15
   
   🎉 Tag successfully written and registered!
   
   ▶️  Resuming scanning...
   ```

### Option 2: Skip the Tag (Press S)

```
👉 (W)rite this tag or (S)kip? [W/S]: S
⏭️  Skipping tag...

▶️  Resuming scanning...
```

---

## 🔄 Automatic Behavior

### Scanning Pause/Resume
- **Pauses**: When unregistered tag detected and prompt appears
- **Resumes**: Automatically after writing, skipping, or canceling

### Tag Memory
- Each unregistered tag is **prompted only once per session**
- If you skip a tag, it won't prompt again until you restart the scanner
- This prevents annoying repeated prompts for the same tag

---

## 💾 Database Integration

### What Gets Saved
When you write a tag:
- ✅ **Old Tag ID**: Original EPC code
- ✅ **New EPC**: The rewritten EPC code
- ✅ **Item Name**: User-provided description
- ✅ **Write Date**: Automatic timestamp
- ✅ **Detection Count**: Starts tracking detections

### Database Fields
```sql
tag_id            VARCHAR(50)  -- Old tag ID (original EPC)
item_name         VARCHAR(255) -- Item description
write_date        TIMESTAMP    -- When tag was written
unwrite_date      TIMESTAMP    -- NULL (can be set later)
detection_count   INTEGER      -- Number of times detected
last_seen         TIMESTAMP    -- Most recent detection
is_written        BOOLEAN      -- TRUE (tag has been written)
```

---

## 🌐 Web Dashboard

Access real-time data at: **http://localhost:5000**

### Features
- 📊 Live tag statistics
- 🏷️ Active tags list with RSSI
- 📈 Detection history
- 🔍 Database search
- 📋 Tag details lookup

---

## ⚙️ Technical Details

### Modified Components

#### 1. FastRFIDScanner Class
- Added `pause_scanning` flag
- Added `pending_write_tag` attribute
- New method: `prompt_write_tag_interactive(tag_hex)`

#### 2. Scanning Loop
- Checks `pause_scanning` flag before each scan
- Pauses when flag is `True`
- Resumes when flag is `False`

#### 3. Tag Processing
- Detects unregistered tags via database lookup
- Calls interactive prompt instead of showing warning
- Tracks prompted tags to avoid duplicates

---

## 🐛 Troubleshooting

### Issue: Tag Write Failed
**Symptoms**: "❌ Tag write failed with status: 0x__"

**Solutions**:
1. Ensure tag is within range (< 50cm recommended)
2. Verify tag is writable (not locked)
3. Check access password (default: 00000000)

### Issue: Database Not Updating
**Symptoms**: Tag written but not appearing in database

**Solutions**:
1. Check PostgreSQL is running:
   ```bash
   # Windows: Check services
   Get-Service postgresql*
   ```
2. Verify connection settings in `database.py`:
   - Host: localhost
   - Port: 5432
   - User: postgres
   - Password: 123
   - Database: rfid_system

### Issue: Scanning Doesn't Resume
**Symptoms**: Stuck after writing/skipping tag

**Solutions**:
1. Press Ctrl+C to stop
2. Restart with `python main.py`
3. Check for errors in terminal output

---

## 📝 Example Session

```bash
C:\RFID Config\Reader> python main.py

🔌 Connecting to RFID Reader...
✅ Connected to reader on COM5
✅ Database connected successfully!
✅ Tables verified/created

Starting threads:
1. Terminal Scanner
2. Web Interface

Press Ctrl+C to stop all threads

🖥️  TERMINAL SCANNER
========================================
🚀 Starting fast continuous scanning...
📡 Optimized for quick detection and distance tracking
⏹️  Press Ctrl+C to stop

[Scan #1] Found 0 tags

[Scan #2] Found 1 tags
📌 NEW TAG DETECTED!
🏷️  Tag: E2 00 10 70 E0 10 01 97 1D 32 43 21
📏 Distance: NEAR (RSSI: -45 dBm) 📍
🔍 First seen: 14:23:45
💾 Database: ⚠️  NEW TAG - Not in database!
   This tag needs to be written and registered.

============================================================
⚠️  UNREGISTERED TAG DETECTED!
   Tag ID: E2 00 10 70 E0 10 01 97 1D 32 43 21
============================================================

👉 (W)rite this tag or (S)kip? [W/S]: W

📝 Enter new EPC for this tag
   Format: 12 hex bytes with spaces (e.g., 'E2 00 12 34 56 78 90 12 34 56 78 90')
   New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44

🏷️  Enter item name: Test Laptop

📋 Summary:
   Old Tag: E2 00 10 70 E0 10 01 97 1D 32 43 21
   New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
   Item: Test Laptop

✅ Confirm write? [Y/N]: Y

📝 Writing tag...
   Old EPC: E2 00 10 70 E0 10 01 97 1D 32 43 21
   New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
   Item: Test Laptop
✅ Tag written successfully!
✅ Database updated for tag: Test Laptop

🎉 Tag successfully written and registered!

▶️  Resuming scanning...

[Scan #3] Found 1 tags
🏷️  Tag: E2 00 AA BB CC DD EE FF 11 22 33 44 ✅ (Test Laptop)
📏 Distance: NEAR (RSSI: -43 dBm) 📍
🔍 First seen: 14:24:12
💾 Database: ✅ REGISTERED - Item: Test Laptop

[Scan #4] Found 0 tags
```

---

## 🎓 Best Practices

### 1. EPC Format
- Always use **12 hex bytes** (24 hex characters)
- Use spaces between bytes for readability
- Example: `E2 00 AA BB CC DD EE FF 11 22 33 44`

### 2. Item Naming
- Be descriptive but concise
- Include model numbers if applicable
- Examples:
  - ✅ "Laptop Dell XPS 15"
  - ✅ "Monitor LG 27inch #1234"
  - ❌ "Thing" (too vague)
  - ❌ "Dell XPS 15 9570 Intel Core i7-8750H 16GB RAM 512GB SSD Silver" (too long)

### 3. Tag Positioning
- Keep tag **within 50cm** of reader during write
- Ensure stable position (don't move tag during write)
- Avoid metal surfaces nearby

### 4. Database Maintenance
- Regularly check database status:
  ```bash
  python check_database_status.py
  ```
- Clear old test data when needed:
  ```bash
  python clear_database.py
  ```

---

## 📚 Related Files

- `main.py` - Main scanner with interactive prompts
- `database.py` - PostgreSQL database manager
- `reader.py` - RFID reader communication with write_epc()
- `web_interface.py` - Flask dashboard
- `clear_database.py` - Database reset utility
- `check_database_status.py` - Database status viewer

---

## 🔐 Security Notes

### Access Password
- Default: `00000000` (8 zeros)
- Change in `reader.py` if your tags use different password
- Located in `write_epc()` method:
  ```python
  access_password = b'\x00\x00\x00\x00'  # Change if needed
  ```

### Database Credentials
- Configured in `database.py`
- Change for production:
  ```python
  'host': 'localhost',
  'port': 5432,
  'user': 'postgres',
  'password': '123',  # Change this!
  'database': 'rfid_system'
  ```

---

## 🎉 Success!

You now have a **fully interactive RFID tag management system** with:
- ✅ Single-command operation (`python main.py`)
- ✅ Automatic unregistered tag detection
- ✅ Interactive write prompts
- ✅ PostgreSQL database integration
- ✅ Real-time web dashboard
- ✅ Seamless scanning pause/resume

**No separate scripts needed!** Everything works from `main.py`.
