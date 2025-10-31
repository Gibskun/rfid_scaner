# 🎯 NEW WORKFLOW - Tag Registration System

## 📋 Overview

The system has been updated to **prevent automatic database saves**. Now:

✅ **Tags are ONLY saved to database AFTER being written/programmed**  
✅ **User must provide item name during tag writing**  
✅ **Unregistered tags trigger clear warnings**  
✅ **Interactive prompts guide the registration process**

---

## 🔄 New Workflow

### Step 1: Clear the Database

Before starting with the new system, clear the existing database:

```powershell
python clear_database.py
```

Type `YES` to confirm. This removes all existing tags.

### Step 2: Choose Your Scanner Mode

You now have **TWO scanning modes**:

#### Option A: Interactive Scanner (RECOMMENDED for new tags)
```powershell
python interactive_scanner.py
```

**What it does:**
- 📡 Scans continuously for tags
- 🔍 Checks if tag is in database
- ✅ Known tags: Shows item name
- ⚠️ Unknown tags: **PAUSES and prompts you to write the tag**
- 📝 Guides you through:
  1. Entering new EPC
  2. Entering item name
  3. Writing the tag
  4. Saving to database

**When to use:** When you have new/blank tags to register

#### Option B: Regular Scanner (for monitoring registered tags)
```powershell
python main.py
```

**What it does:**
- 📡 Scans continuously for tags
- 💾 Shows database info for registered tags
- ⚠️ **Warns about unregistered tags** but DOES NOT save them
- 🌐 Runs web interface for monitoring

**When to use:** When you just want to monitor already-registered tags

---

## 📝 Complete Tag Registration Process

### Using Interactive Scanner (Easiest)

**1. Start the interactive scanner:**
```powershell
python interactive_scanner.py
```

**2. Place a new tag near the reader**

The system detects it and shows:
```
======================================================================
🏷️  UNREGISTERED TAG DETECTED!
======================================================================
📌 Tag ID: E2 00 00 00 00 00 00 00 00 00 00 01
📊 Length: 12 bytes

⚠️  This tag is NOT in the database and needs to be registered.

──────────────────────────────────────────────────────────────────────
Choose an option:
  [W] Write/Program this tag with new EPC and item name
  [S] Skip this tag (it will not be saved to database)
  [C] Continue scanning without prompting for this tag
──────────────────────────────────────────────────────────────────────

Your choice (W/S/C):
```

**3. Press `W` to write the tag**

**4. Enter new EPC:**
```
1️⃣  Enter NEW EPC for this tag:
   Format: Hex bytes (with or without spaces)
   Example: E2 00 12 34 56 78 90 AB CD EF 01 23
   or: E200123456789ABCDEF0123
   Current EPC: E2 00 00 00 00 00 00 00 00 00 00 01

   New EPC: E2 00 12 34 56 78 90 AB CD EF 01 23
```

**5. Enter item name:**
```
2️⃣  Enter item name/description:
   Example: Laptop Charger - Dell XPS

   Item name: Conference Badge - John Smith
```

**6. Confirm:**
```
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
CONFIRM TAG WRITE
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
Current Tag ID: E2 00 00 00 00 00 00 00 00 00 00 01
New EPC:        E2 00 12 34 56 78 90 AB CD EF 01 23
Item Name:      Conference Badge - John Smith

⚠️  This will PERMANENTLY reprogram the RFID tag!

Proceed with writing? (YES/no):
```

**7. Type `YES` and press Enter**

**8. System writes the tag and saves to database:**
```
📝 Writing tag...
✅ Tag written successfully!
✅ Tag saved to database

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
TAG REGISTRATION COMPLETE!
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
✅ Tag ID: E2 00 00 00 00 00 00 00 00 00 00 01
✅ New EPC: E2 00 12 34 56 78 90 AB CD EF 01 23
✅ Item: Conference Badge - John Smith
✅ Saved to database
======================================================================
```

**9. Continue scanning** - the scanner resumes automatically

---

## 🎓 What Happens Now vs Before

### ❌ OLD Behavior (Before Fix):
1. Tag detected → **Immediately saved to database**
2. No item name
3. No user interaction
4. Database fills with unidentified tags

### ✅ NEW Behavior (After Fix):
1. Tag detected → **Check if in database**
2. If **NOT in database** → **Prompt user to write it**
3. User enters **new EPC** and **item name**
4. Tag is **written/programmed**
5. **Only then** is it saved to database
6. Database contains **only properly registered tags**

---

## 🛠️ Available Tools

### 1. Interactive Scanner (NEW)
```powershell
python interactive_scanner.py
```
- Auto-prompts for unregistered tags
- Pauses scanning during write
- Guides through entire process
- Best for registering new tags

### 2. Tag Writer (Standalone)
```powershell
python tag_writer.py
```
- Manual tag writing
- Search and manage existing tags
- View database statistics
- Best for one-off tag updates

### 3. Regular Scanner
```powershell
python main.py
```
- Continuous scanning
- Web interface
- Shows warnings for unregistered tags
- Does NOT auto-save to database
- Best for monitoring registered tags

### 4. Clear Database
```powershell
python clear_database.py
```
- Removes all tags from database
- Resets ID sequences
- Use before starting fresh

### 5. Test Database
```powershell
python test_database.py
```
- Verify database connection
- Test CRUD operations
- Check table structure

---

## 📊 Database States

### Scenario 1: Tag in Database
```
Tag detected → Check database → FOUND
                                  ↓
                            Show item name
                            Continue scanning
```

### Scenario 2: Tag NOT in Database (Interactive Mode)
```
Tag detected → Check database → NOT FOUND
                                  ↓
                            Pause scanning
                                  ↓
                            Prompt user: Write/Skip/Continue
                                  ↓
                        [User chooses Write]
                                  ↓
                        Enter new EPC + item name
                                  ↓
                            Write to tag
                                  ↓
                        Save to database
                                  ↓
                        Resume scanning
```

### Scenario 3: Tag NOT in Database (Regular Mode)
```
Tag detected → Check database → NOT FOUND
                                  ↓
                        Show WARNING message
                        "Tag not in database"
                        "Use interactive_scanner.py to register"
                                  ↓
                        Continue scanning
                        (Tag is NOT saved)
```

---

## 🎯 Quick Reference

| Task | Command | Description |
|------|---------|-------------|
| Register new tags | `python interactive_scanner.py` | Auto-prompts for writing |
| Monitor tags | `python main.py` | Scanning + web dashboard |
| Write specific tag | `python tag_writer.py` | Manual tag management |
| Clear database | `python clear_database.py` | Remove all tags |
| Test system | `python test_database.py` | Verify database works |

---

## ⚠️ Important Notes

1. **Tags are NEVER auto-saved** - only after writing
2. **Item name is REQUIRED** - must be entered during write
3. **Write date is automatically recorded** - when tag is written
4. **Unwrite date is reserved** - for future functionality
5. **Database must be cleared** - before using new workflow

---

## 🚀 Getting Started

**Step-by-step for first use:**

```powershell
# 1. Clear existing database
python clear_database.py
# Type: YES

# 2. Start interactive scanner
python interactive_scanner.py
# Press Enter for COM5

# 3. Place a tag near reader
# System will prompt: Write/Skip/Continue

# 4. Press: W

# 5. Enter new EPC (example):
E2 00 AB CD 12 34 56 78 90 EF AB CD

# 6. Enter item name (example):
Laptop - HP EliteBook

# 7. Confirm:
YES

# 8. Tag is written and saved!
# Continue with next tag...
```

---

## 🎉 Benefits of New System

✅ **No junk data** - database only contains registered tags  
✅ **Meaningful names** - every tag has an item description  
✅ **User control** - decide which tags to register  
✅ **Proper tracking** - know when each tag was written  
✅ **Clean workflow** - guided process for registration  
✅ **Flexible modes** - interactive or monitoring-only  

---

## 📞 Need Help?

**If tag write fails:**
- Ensure tag is close to reader
- Check tag is not locked
- Verify EPC format (even number of bytes)
- Try increasing reader power

**If database errors:**
- Run `python test_database.py`
- Check PostgreSQL is running
- Verify connection settings

**If scanning issues:**
- Check COM port is correct
- Ensure reader is connected
- Try different baud rate

---

**You're ready to use the new tag registration system! 🏷️**
