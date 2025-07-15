#!/usr/bin/env python3
"""
RealmPortal
A tool to migrate WoW interface configurations between different realms and characters.
"""

import os
import shutil
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import time

class WoWUIMigrator:
    def __init__(self, wtf_path: str, dry_run: bool = False):
        self.wtf_path = Path(wtf_path)
        self.dry_run = dry_run
        self.changes_made = []
        self.working_path = self.wtf_path  # This will be updated when we create a copy
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wow_ui_migration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # File extensions that typically contain WoW configuration data
        self.config_extensions = {
            '.lua', '.txt', '.toc', '.xml', '.wtf'
        }
    
    def create_migration_copy(self, old_realm: str, new_realm: str, 
                             old_char: str = None, new_char: str = None) -> str:
        """Create a copy of the WTF folder for migration, leaving original untouched."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Build descriptive name for the copy
        copy_name_parts = [f"{old_realm}_to_{new_realm}"]
        if old_char and new_char:
            copy_name_parts.append(f"{old_char}_to_{new_char}")
        copy_name_parts.append(timestamp)
        
        copy_name = "_".join(copy_name_parts)
        copy_path = self.wtf_path.parent / f"WTF_migrated_{copy_name}"
        
        if not self.dry_run:
            self.logger.info(f"Creating migration copy at: {copy_path}")
            shutil.copytree(self.wtf_path, copy_path)
            # Update working path to the copy
            self.working_path = copy_path
        else:
            self.logger.info(f"[DRY RUN] Would create migration copy at: {copy_path}")
            
        return str(copy_path)
    
    def get_folder_mappings(self, old_realm: str, new_realm: str, 
                           old_char: str = None, new_char: str = None,
                           old_account: str = None, new_account: str = None) -> Dict[str, str]:
        """Generate folder name mappings for renaming."""
        mappings = {}
        
        # Add account mapping
        if old_account and new_account:
            mappings[old_account] = new_account
            
        # Add realm mapping
        if old_realm and new_realm:
            mappings[old_realm] = new_realm
            
        # Add character mapping
        if old_char and new_char:
            mappings[old_char] = new_char
            
        return mappings
    
    def get_content_mappings(self, old_realm: str, new_realm: str,
                            old_char: str = None, new_char: str = None,
                            old_account: str = None, new_account: str = None) -> Dict[str, str]:
        """Generate content replacement mappings for file contents."""
        mappings = {}
        
        # Add realm mapping
        if old_realm and new_realm:
            mappings[old_realm] = new_realm
            
        # Add character mapping
        if old_char and new_char:
            mappings[old_char] = new_char
            
        # Add account mapping
        if old_account and new_account:
            mappings[old_account] = new_account
            
        return mappings
    
    def rename_folders(self, folder_mappings: Dict[str, str], old_account: str = None) -> List[Tuple[str, str]]:
        """Rename folders according to the mappings."""
        renamed_folders = []
        
        # Walk through all directories, process from deepest to shallowest
        all_dirs = []
        for root, dirs, files in os.walk(self.working_path):
            for dir_name in dirs:
                full_path = os.path.join(root, dir_name)
                
                # If we're migrating a specific account, only process that account's folders
                if old_account:
                    # Check if this path is under the specific account we want to migrate
                    account_path = os.path.join(self.working_path, "Account", old_account)
                    if not (full_path == account_path or full_path.startswith(account_path + os.sep)):
                        # Also allow renaming the account folder itself
                        if not (dir_name == old_account and "Account" in root):
                            continue
                
                all_dirs.append((full_path, len(full_path.split(os.sep))))
        
        # Sort by depth (deepest first) to avoid conflicts
        all_dirs.sort(key=lambda x: x[1], reverse=True)
        
        for dir_path, _ in all_dirs:
            dir_name = os.path.basename(dir_path)
            parent_dir = os.path.dirname(dir_path)
            
            # Check if this directory name needs to be changed
            new_name = None
            for old_name, replacement in folder_mappings.items():
                if dir_name == old_name:
                    new_name = replacement
                    break
            
            if new_name and new_name != dir_name:
                new_path = os.path.join(parent_dir, new_name)
                
                if not self.dry_run:
                    if os.path.exists(new_path):
                        self.logger.warning(f"Target directory already exists, merging: {new_path}")
                        # Try to merge directories if target exists
                        try:
                            self._merge_directories(dir_path, new_path)
                            self.logger.info(f"Merged folder: {dir_path} -> {new_path}")
                        except Exception as e:
                            self.logger.error(f"Failed to merge {dir_path} -> {new_path}: {e}")
                            continue
                    else:
                        os.rename(dir_path, new_path)
                        self.logger.info(f"Renamed folder: {dir_path} -> {new_path}")
                else:
                    self.logger.info(f"[DRY RUN] Would rename folder: {dir_path} -> {new_path}")
                
                renamed_folders.append((dir_path, new_path))
                self.changes_made.append(f"Folder: {dir_path} -> {new_path}")
        
        return renamed_folders
    
    def _merge_directories(self, source_dir: str, target_dir: str):
        """Merge source directory into target directory."""
        for item in os.listdir(source_dir):
            source_item = os.path.join(source_dir, item)
            target_item = os.path.join(target_dir, item)
            
            if os.path.isdir(source_item):
                if os.path.exists(target_item):
                    self._merge_directories(source_item, target_item)
                else:
                    shutil.move(source_item, target_item)
            else:
                if os.path.exists(target_item):
                    # File exists, create backup and overwrite
                    backup_name = f"{target_item}.backup_{int(time.time())}"
                    shutil.move(target_item, backup_name)
                    self.logger.info(f"Backed up existing file: {target_item} -> {backup_name}")
                shutil.move(source_item, target_item)
        
        # Remove empty source directory
        if not os.listdir(source_dir):
            os.rmdir(source_dir)
    
    def update_file_contents(self, content_mappings: Dict[str, str], old_account: str = None) -> List[str]:
        """Update file contents according to the mappings."""
        updated_files = []
        
        for root, dirs, files in os.walk(self.working_path):
            # If we're migrating a specific account, only process files under that account
            if old_account:
                account_path = os.path.join(self.working_path, "Account", old_account)
                new_account = content_mappings.get(old_account, old_account)
                new_account_path = os.path.join(self.working_path, "Account", new_account)
                
                # Only process files under the old or new account path, or global config files
                if not (root.startswith(account_path) or 
                       root.startswith(new_account_path) or 
                       root == str(self.working_path)):  # Global config files like Config.wtf
                    continue
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Skip binary files and only process known config file types
                if file_ext not in self.config_extensions:
                    continue
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply all content mappings
                    for old_text, new_text in content_mappings.items():
                        # Use word boundaries to avoid partial matches
                        pattern = rf'\b{re.escape(old_text)}\b'
                        content = re.sub(pattern, new_text, content, flags=re.IGNORECASE)
                    
                    # If content changed, write back to file
                    if content != original_content:
                        if not self.dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.logger.info(f"Updated file content: {file_path}")
                        else:
                            self.logger.info(f"[DRY RUN] Would update file content: {file_path}")
                        
                        updated_files.append(file_path)
                        self.changes_made.append(f"Content: {file_path}")
                
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {e}")
        
        return updated_files
    
    def migrate(self, old_realm: str, new_realm: str, 
                old_char: str = None, new_char: str = None,
                old_account: str = None, new_account: str = None) -> bool:
        """Perform the complete migration process."""
        
        self.logger.info("Starting WoW UI migration...")
        self.logger.info(f"Original WTF Path: {self.wtf_path}")
        self.logger.info(f"Realm: {old_realm} -> {new_realm}")
        if old_char and new_char:
            self.logger.info(f"Character: {old_char} -> {new_char}")
        if old_account and new_account:
            self.logger.info(f"Account: {old_account} -> {new_account}")
        
        if not self.wtf_path.exists():
            self.logger.error(f"WTF folder not found: {self.wtf_path}")
            return False
        
        # Always create a copy for safety
        copy_path = self.create_migration_copy(old_realm, new_realm, old_char, new_char)
        self.logger.info(f"Working on copy at: {self.working_path}")
        
        try:
            # Get mappings
            folder_mappings = self.get_folder_mappings(old_realm, new_realm, old_char, new_char, old_account, new_account)
            content_mappings = self.get_content_mappings(old_realm, new_realm, old_char, new_char, old_account, new_account)
            
            # Rename folders first
            renamed_folders = self.rename_folders(folder_mappings, old_account)
            
            # Update file contents
            updated_files = self.update_file_contents(content_mappings, old_account)
            
            # Summary
            self.logger.info(f"Migration completed!")
            self.logger.info(f"Folders renamed: {len(renamed_folders)}")
            self.logger.info(f"Files updated: {len(updated_files)}")
            self.logger.info(f"Migrated copy created at: {copy_path}")
            self.logger.info(f"Original WTF folder unchanged at: {self.wtf_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
    
    def get_realm_and_character_info(self) -> Dict[str, List[str]]:
        """Scan WTF folder to find existing realm and character names."""
        info = {"realms": [], "characters": [], "accounts": []}
        
        account_path = self.wtf_path / "Account"
        if not account_path.exists():
            return info
        
        # Find accounts
        for account_dir in account_path.iterdir():
            if account_dir.is_dir():
                info["accounts"].append(account_dir.name)
                
                # Find realms in this account
                for item in account_dir.iterdir():
                    if item.is_dir() and item.name != "SavedVariables":
                        realm_name = item.name
                        if realm_name not in info["realms"]:
                            info["realms"].append(realm_name)
                        
                        # Find characters in this realm
                        for char_item in item.iterdir():
                            if char_item.is_dir() and char_item.name != "SavedVariables":
                                char_name = char_item.name
                                if char_name not in info["characters"]:
                                    info["characters"].append(char_name)
        
        return info


def main():
    parser = argparse.ArgumentParser(description="RealmPortal")
    parser.add_argument("wtf_path", help="Path to the WTF folder")
    parser.add_argument("--old-realm", help="Source realm name")
    parser.add_argument("--new-realm", help="Target realm name")
    parser.add_argument("--old-char", help="Source character name")
    parser.add_argument("--new-char", help="Target character name")
    parser.add_argument("--old-account", help="Source account name")
    parser.add_argument("--new-account", help="Target account name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--scan", action="store_true", help="Scan WTF folder to show existing realms, characters, and accounts")
    
    args = parser.parse_args()
    
    migrator = WoWUIMigrator(
        wtf_path=args.wtf_path,
        dry_run=args.dry_run
    )
    
    if args.scan:
        info = migrator.get_realm_and_character_info()
        print("\n=== WTF Folder Information ===")
        print(f"Accounts found: {', '.join(info['accounts']) if info['accounts'] else 'None'}")
        print(f"Realms found: {', '.join(info['realms']) if info['realms'] else 'None'}")
        print(f"Characters found: {', '.join(info['characters']) if info['characters'] else 'None'}")
        return
    
    # Check required arguments for migration
    if not args.old_realm or not args.new_realm:
        parser.error("--old-realm and --new-realm are required for migration operations")
    
    success = migrator.migrate(
        old_realm=args.old_realm,
        new_realm=args.new_realm,
        old_char=args.old_char,
        new_char=args.new_char,
        old_account=args.old_account,
        new_account=args.new_account
    )
    
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed. Check the log for details.")


if __name__ == "__main__":
    main()