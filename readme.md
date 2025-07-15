# RealmPortal

A powerful Python tool for migrating World of Warcraft interface configurations between different realms, characters, and accounts. Easily transfer your addon settings, UI layouts, and configurations without losing your carefully crafted setup.

## 🌟 Features

- **Complete Migration**: Migrates both folder structure and file contents
- **Selective Updates**: Choose what to migrate (realm, character, account, or any combination)
- **Safety First**: Creates backups and offers dry-run mode
- **Safe Copy Mode**: Create migrated copies while leaving originals untouched
- **Smart Processing**: Only processes relevant files and folders
- **Cross-Platform**: Works on Windows, Mac, and Linux
- **Detailed Logging**: Comprehensive logs of all changes made

## 📋 What It Migrates

### Folder Structure
- Account folders (e.g., `OLDACCOUNT` → `NEWACCOUNT`)
- Realm folders (e.g., `Stormrage` → `Area-52`)
- Character folders (e.g., `MyWarrior` → `NewWarrior`)

### File Contents
Updates references in these file types:
- `.lua` files (addon saved variables)
- `.txt` files (configuration files)
- `.wtf` files (WoW settings)

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- World of Warcraft installation with WTF folder

### Installation
1. Download `RealmPortal.py`
2. No additional packages required - uses only Python standard library

### Basic Usage

**1. First, scan your WTF folder:**
```bash
python RealmPortal.py "C:\Path\To\Your\WTF" --scan
```

**2. Preview your migration (recommended):**
```bash
python RealmPortal.py "C:\Path\To\Your\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --old-char "MyWarrior" --new-char "NewWarrior" \
  --dry-run
```

**3. Create a safe migrated copy:**
```bash
python RealmPortal.py "C:\Path\To\Your\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --old-char "MyWarrior" --new-char "NewWarrior" \
  --create-copy
```

## 📖 Detailed Usage

### Command Line Options

```
python RealmPortal.py <WTF_PATH> [OPTIONS]
```

#### Required Arguments
- `WTF_PATH` - Path to your WTF folder

#### Migration Parameters
- `--old-realm TEXT` - Source realm name (required for migration)
- `--new-realm TEXT` - Target realm name (required for migration)
- `--old-char TEXT` - Source character name (optional)
- `--new-char TEXT` - Target character name (optional)
- `--old-account TEXT` - Source account name (optional)
- `--new-account TEXT` - Target account name (optional)

#### Safety & Behavior Options
- `--scan` - Show existing realms, characters, and accounts
- `--dry-run` - Preview changes without making them
- `--create-copy` - Create migrated copy, leave original untouched
- `--no-backup` - Skip creating backup (not recommended)

### Finding Your WTF Folder

**Windows:**
```
D:\World of Warcraft\WTF
```

**Mac:**
```
/Applications/World of Warcraft/WTF
```

**Linux:**
```
~/.wine/drive_d/World of Warcraft/WTF
```

## 💡 Usage Examples

### Realm Transfer
Move all characters from one realm to another:
```bash
python RealmPortal.py "C:\WoW\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --create-copy
```

### Character Rename
Rename a character while changing realms:
```bash
python RealmPortal.py "C:\WoW\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --old-char "Oldname" --new-char "Newname" \
  --create-copy
```

### Account Migration
Complete migration including account change:
```bash
python RealmPortal.py "C:\WoW\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --old-char "Warrior" --new-char "Paladin" \
  --old-account "WOW1" --new-account "WOW2" \
  --create-copy
```

### Preview Changes
Always test first with dry-run:
```bash
python RealmPortal.py "C:\WoW\WTF" \
  --old-realm "Stormrage" --new-realm "Area-52" \
  --dry-run
```

## 🛡️ Safety Features

### Automatic Backups
- Creates timestamped backups before making changes
- Backup format: `WTF_backup_YYYYMMDD_HHMMSS`
- Disable with `--no-backup` (not recommended)

### Copy Mode (Recommended)
- Use `--create-copy` to leave original WTF folder untouched
- Creates: `WTF_migrated_[migration_details]_[timestamp]`
- Test the migrated copy before using it

### Dry Run Mode
- Use `--dry-run` to preview all changes
- Shows exactly what would be modified
- No files or folders are actually changed

## 📁 File Structure

The tool handles the standard WoW WTF structure:
```
WTF/
├── Config.wtf                    # Global WoW settings
├── Account/
│   └── ACCOUNTNAME/
│       ├── SavedVariables/       # Account-wide addon data
│       └── REALMNAME/
│           └── CHARACTERNAME/
│               ├── SavedVariables/    # Character-specific addon data
│               └── AddOns/           # Character-specific addon settings
```

## 🔧 Troubleshooting

### Common Issues

**"WTF folder not found"**
- Check your WTF path is correct
- Use quotes around paths with spaces
- Ensure you're pointing to the WTF folder, not the WoW folder

**"Target directory already exists"**
- Tool will merge directories when possible
- Check logs for details on what was merged
- Use `--create-copy` to avoid conflicts

**"Permission denied"**
- Close World of Warcraft before running
- Run command prompt as administrator (Windows)
- Check file permissions

### Logging
- All operations are logged to `wow_ui_migration.log`
- Check this file for detailed information about what was changed
- Logs are appended, so you can see history of all migrations

## ⚠️ Important Notes

### Before Using
1. **Close World of Warcraft** before running the tool
2. **Test with `--dry-run`** first to preview changes
3. **Use `--create-copy`** for safest operation
4. **Backup your WTF folder** manually if you're concerned

### What Gets Updated
- The tool uses word boundary matching to avoid partial replacements
- Only updates exact matches of your specified names
- Processes configuration files, not game assets
- Updates both folder names and file contents

### Character-Specific Behavior
- When migrating specific accounts, only that account's data is processed
- Other accounts in the same WTF folder remain untouched
- Global settings in `Config.wtf` are still updated for realm changes

## 🤝 Contributing

Found a bug or want to add a feature?
1. Check existing issues
2. Create a detailed bug report or feature request
3. Include your WoW version, OS, and Python version
4. Provide sample WTF structure if relevant

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🙏 Acknowledgments

- Inspired by [Oppahansi's WoWCopyUI](https://github.com/oppahansi/WoWCopyUI)

---

**Disclaimer:** This tool modifies game configuration files. While it includes safety features, always backup important data. Use at your own risk. Not affiliated with Blizzard Entertainment.