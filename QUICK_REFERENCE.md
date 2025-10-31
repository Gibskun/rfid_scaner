# 🚀 QUICK START - Interactive RFID System

## Start System
```bash
python main.py
```

## What Happens
- ✅ Terminal scanner starts (with interactive prompts)
- ✅ Web dashboard starts (http://localhost:5000)
- ✅ Database connects (PostgreSQL)
- ✅ Begins scanning for tags

---

## When Tag Detected

### Registered Tag (in database)
```
✅ Tag: E2 00 AA BB CC DD EE FF 11 22 33 44 (Laptop Dell XPS)
📏 Distance: NEAR (RSSI: -45 dBm)
💾 Database: ✅ REGISTERED
```
**Action**: None needed, continues scanning

### Unregistered Tag (NOT in database)
```
============================================================
⚠️  UNREGISTERED TAG DETECTED!
   Tag ID: E2 00 10 70 E0 10 01 97 1D 32 43 21
============================================================

👉 (W)rite this tag or (S)kip? [W/S]:
```
**Scanning pauses automatically** - waiting for your choice

---

## Your Options

### Option 1: Skip (Press S)
```
[W/S]: S
⏭️  Skipping tag...
▶️  Resuming scanning...
```
- Tag is ignored
- Scanning continues
- Won't ask again (this session)

### Option 2: Write (Press W)
```
[W/S]: W

📝 Enter new EPC for this tag
   Format: 12 hex bytes with spaces
   New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44

🏷️  Enter item name: Laptop Dell XPS 15

📋 Summary:
   Old Tag: E2 00 10 70 E0 10 01 97 1D 32 43 21
   New EPC: E2 00 AA BB CC DD EE FF 11 22 33 44
   Item: Laptop Dell XPS 15

✅ Confirm write? [Y/N]: Y

📝 Writing tag...
✅ Tag written successfully!
✅ Database updated
🎉 Tag successfully written and registered!

▶️  Resuming scanning...
```

---

## EPC Format Examples

### ✅ Correct Format
```
E2 00 AA BB CC DD EE FF 11 22 33 44  (12 bytes, spaces)
E2 00 12 34 56 78 90 AB CD EF 11 22  (12 bytes, spaces)
AA BB CC DD EE FF 11 22 33 44 55 66  (12 bytes, spaces)
```

### ❌ Incorrect Format
```
E200AABBCCDDEEFF112233          (no spaces)
E2 00 AA BB CC DD                (only 6 bytes)
E2 00 AA BB CC DD EE FF 11 22 33 44 55 66  (14 bytes)
XY ZZ AA BB CC DD EE FF 11 22 33 44  (invalid hex)
```

---

## Web Dashboard

**URL**: http://localhost:5000

**Features**:
- 📊 Real-time tag statistics
- 🏷️ Active tags list
- 📈 Detection history
- 🔍 Search database
- 💾 View all registered tags

---

## Database Management

### View Status
```bash
python check_database_status.py
```

### Clear All Data
```bash
python clear_database.py
```
**Warning**: This deletes all tags and detection history!

---

## Stop System
Press **Ctrl+C** in terminal

System will:
- ✅ Stop scanner gracefully
- ✅ Close database connections
- ✅ Stop web server
- ✅ Clean up threads

---

## Troubleshooting

### Problem: "Reader not connected"
**Solution**: 
1. Check USB cable
2. Verify COM port in `main.py` (default: COM5)
3. Close other apps using the reader

### Problem: "Database connection failed"
**Solution**:
1. Start PostgreSQL service
2. Check credentials (postgres/123)
3. Verify database exists: rfid_system

### Problem: "Tag write failed"
**Solution**:
1. Move tag closer (< 50cm)
2. Ensure tag is writable
3. Check access password (default: 00000000)

### Problem: Prompt doesn't appear
**Solution**:
1. Tag might be registered - check web dashboard
2. Tag might have been prompted already this session
3. Restart scanner: Ctrl+C then `python main.py`

---

## Tips

### 1. Tag Positioning
- Keep tag **within 50cm** when writing
- Don't move tag during write operation
- Avoid metal surfaces nearby

### 2. Item Naming
- Be descriptive: "Laptop Dell XPS 15"
- Include model numbers if needed
- Keep it concise (< 50 chars)

### 3. EPC Planning
- Use a consistent pattern
- First 2 bytes often: E2 00 (common prefix)
- Last 10 bytes: your custom ID
- Example pattern: E2 00 [AA BB CC DD EE FF 11 22 33 44]

### 4. Session Management
- Each unregistered tag prompts **once per session**
- Restart scanner to prompt same tag again
- Use Skip (S) for temporary tags

---

## That's It! 🎉

**Single command**: `python main.py`
**Interactive prompts**: Automatic
**Database saving**: Automatic
**Web dashboard**: Automatic

Everything just works!
