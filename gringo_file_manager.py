#!/usr/bin/env python3
"""
Advanced File Management System for GRINGO Personal OS
Provides comprehensive file operations, organization, and AI integration
"""

import streamlit as st
import os
import shutil
import json
import sqlite3
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import zipfile
import tarfile
import tempfile

class GringoFileManager:
    def __init__(self, workspace_root: str, memory_db: str):
        self.workspace_root = workspace_root
        self.memory_db = memory_db
        self.current_path = workspace_root
        self.setup_directories()
    
    def setup_directories(self):
        """Create standard directory structure"""
        dirs = [
            "projects", "documents", "downloads", "media", 
            "scripts", "data", "backups", "temp", "processed"
        ]
        for dir_name in dirs:
            os.makedirs(os.path.join(self.workspace_root, dir_name), exist_ok=True)
    
    def get_directory_contents(self, path: str = None) -> Dict[str, Any]:
        """Get contents of directory with metadata"""
        if path is None:
            path = self.current_path
            
        if not os.path.exists(path):
            return {"error": "Directory not found"}
        
        contents = {
            "current_path": path,
            "parent_path": os.path.dirname(path) if path != self.workspace_root else None,
            "directories": [],
            "files": []
        }
        
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    dir_info = self._get_directory_info(item_path)
                    contents["directories"].append(dir_info)
                else:
                    file_info = self._get_file_info(item_path)
                    contents["files"].append(file_info)
                    
        except PermissionError:
            contents["error"] = "Permission denied"
            
        return contents
    
    def _get_directory_info(self, dir_path: str) -> Dict[str, Any]:
        """Get directory metadata"""
        stat = os.stat(dir_path)
        
        # Count contents
        try:
            items = os.listdir(dir_path)
            file_count = sum(1 for item in items if os.path.isfile(os.path.join(dir_path, item)))
            dir_count = sum(1 for item in items if os.path.isdir(os.path.join(dir_path, item)))
        except PermissionError:
            file_count = dir_count = 0
        
        return {
            "name": os.path.basename(dir_path),
            "path": dir_path,
            "type": "directory",
            "size": 0,  # Directories don't have size
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "file_count": file_count,
            "dir_count": dir_count,
            "icon": "📁"
        }
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata with AI enhancement"""
        stat = os.stat(file_path)
        file_type, _ = mimetypes.guess_type(file_path)
        
        # Get AI metadata from database
        ai_data = self._get_ai_metadata(file_path)
        
        # Determine icon based on file type
        icon = self._get_file_icon(file_path, file_type)
        
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "type": "file",
            "size": stat.st_size,
            "size_human": self._format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "file_type": file_type or "unknown",
            "extension": os.path.splitext(file_path)[1],
            "icon": icon,
            "ai_summary": ai_data.get("summary", ""),
            "importance": ai_data.get("importance", 5),
            "tags": ai_data.get("tags", []),
            "agent_actions": ai_data.get("actions", [])
        }
    
    def _get_ai_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get AI-generated metadata for file"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ai_summary, importance_score, tags, agent_actions
                FROM files WHERE filepath = ?
            ''', (file_path,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "summary": result[0] or "",
                    "importance": result[1] or 5,
                    "tags": result[2].split(",") if result[2] else [],
                    "actions": result[3].split("\n") if result[3] else []
                }
        except:
            pass
        
        return {}
    
    def _get_file_icon(self, file_path: str, file_type: str) -> str:
        """Get appropriate icon for file type"""
        ext = os.path.splitext(file_path)[1].lower()
        
        icon_map = {
            # Code files
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.html': '🌐', '.css': '🎨',
            '.java': '☕', '.cpp': '⚙️', '.c': '🔧', '.rs': '🦀', '.go': '🐹',
            
            # Documents
            '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📋', '.md': '📖',
            '.rtf': '📄', '.odt': '📄',
            
            # Data files
            '.json': '📊', '.xml': '📊', '.csv': '📈', '.xlsx': '📊', '.sql': '💾',
            
            # Media files
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🎬', '.svg': '🎨',
            '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mp3': '🎵', '.wav': '🎵',
            
            # Archives
            '.zip': '📦', '.tar': '📦', '.gz': '📦', '.rar': '📦', '.7z': '📦',
            
            # Config files
            '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️', '.yaml': '⚙️', '.yml': '⚙️',
        }
        
        return icon_map.get(ext, '📄')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def create_file(self, name: str, content: str = "", path: str = None) -> bool:
        """Create new file"""
        if path is None:
            path = self.current_path
            
        file_path = os.path.join(path, name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._track_file_in_db(file_path)
            return True
        except Exception as e:
            st.error(f"Failed to create file: {e}")
            return False
    
    def create_directory(self, name: str, path: str = None) -> bool:
        """Create new directory"""
        if path is None:
            path = self.current_path
            
        dir_path = os.path.join(path, name)
        
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            st.error(f"Failed to create directory: {e}")
            return False
    
    def delete_item(self, item_path: str) -> bool:
        """Delete file or directory"""
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
                self._remove_file_from_db(item_path)
            return True
        except Exception as e:
            st.error(f"Failed to delete: {e}")
            return False
    
    def copy_item(self, src_path: str, dst_path: str) -> bool:
        """Copy file or directory"""
        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
                self._track_file_in_db(dst_path)
            return True
        except Exception as e:
            st.error(f"Failed to copy: {e}")
            return False
    
    def move_item(self, src_path: str, dst_path: str) -> bool:
        """Move file or directory"""
        try:
            shutil.move(src_path, dst_path)
            if os.path.isfile(dst_path):
                self._update_file_path_in_db(src_path, dst_path)
            return True
        except Exception as e:
            st.error(f"Failed to move: {e}")
            return False
    
    def extract_archive(self, archive_path: str, extract_to: str = None) -> bool:
        """Extract archive file"""
        if extract_to is None:
            extract_to = os.path.dirname(archive_path)
        
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                st.error("Unsupported archive format")
                return False
            
            # Track extracted files
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    file_path = os.path.join(root, file)
                    self._track_file_in_db(file_path)
            
            return True
        except Exception as e:
            st.error(f"Failed to extract: {e}")
            return False
    
    def search_files(self, query: str, search_content: bool = False) -> List[Dict[str, Any]]:
        """Search for files by name or content"""
        results = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Search by filename
                if query.lower() in file.lower():
                    results.append(self._get_file_info(file_path))
                    continue
                
                # Search by content (for text files)
                if search_content and self._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append(self._get_file_info(file_path))
                    except:
                        pass
        
        return results
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
            '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log', '.csv'
        }
        return os.path.splitext(file_path)[1].lower() in text_extensions
    
    def _track_file_in_db(self, file_path: str):
        """Add file to database tracking"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            stat = os.stat(file_path)
            cursor.execute('''
                INSERT OR REPLACE INTO files 
                (filepath, filename, file_type, size_bytes, created_at, last_modified, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path, 
                os.path.basename(file_path),
                os.path.splitext(file_path)[1],
                stat.st_size,
                datetime.fromtimestamp(stat.st_ctime),
                datetime.fromtimestamp(stat.st_mtime),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Silently fail for non-critical database operations
    
    def _remove_file_from_db(self, file_path: str):
        """Remove file from database tracking"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM files WHERE filepath = ?', (file_path,))
            conn.commit()
            conn.close()
        except:
            pass
    
    def _update_file_path_in_db(self, old_path: str, new_path: str):
        """Update file path in database"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE files SET filepath = ?, filename = ? WHERE filepath = ?
            ''', (new_path, os.path.basename(new_path), old_path))
            conn.commit()
            conn.close()
        except:
            pass

class FileManagerUI:
    def __init__(self, file_manager: GringoFileManager):
        self.file_manager = file_manager
    
    def render_file_browser(self):
        """Render the file browser interface"""
        st.subheader("📁 File Manager")
        
        # Current path and navigation
        current_path = self.file_manager.current_path
        rel_path = os.path.relpath(current_path, self.file_manager.workspace_root)
        if rel_path == ".":
            rel_path = "~"
        
        st.text(f"📍 Current: {rel_path}")
        
        # Navigation buttons
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        
        with nav_col1:
            if st.button("🏠 Home"):
                self.file_manager.current_path = self.file_manager.workspace_root
                st.rerun()
        
        with nav_col2:
            if st.button("⬆️ Up") and current_path != self.file_manager.workspace_root:
                self.file_manager.current_path = os.path.dirname(current_path)
                st.rerun()
        
        with nav_col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        with nav_col4:
            # Search functionality
            search_query = st.text_input("🔍 Search", placeholder="filename or content")
        
        # Get directory contents
        contents = self.file_manager.get_directory_contents()
        
        if "error" in contents:
            st.error(contents["error"])
            return
        
        # Display search results
        if search_query:
            st.subheader(f"🔍 Search Results for '{search_query}'")
            results = self.file_manager.search_files(search_query, search_content=True)
            
            if results:
                for file_info in results:
                    col1, col2, col3 = st.columns([1, 4, 2])
                    with col1:
                        st.text(file_info["icon"])
                    with col2:
                        st.text(file_info["name"])
                        st.caption(file_info["path"])
                    with col3:
                        st.text(file_info["size_human"])
            else:
                st.info("No files found")
            return
        
        # File operations toolbar
        st.markdown("**File Operations:**")
        op_col1, op_col2, op_col3, op_col4 = st.columns(4)
        
        with op_col1:
            if st.button("📄 New File"):
                st.session_state.show_new_file_dialog = True
        
        with op_col2:
            if st.button("📁 New Folder"):
                st.session_state.show_new_folder_dialog = True
        
        with op_col3:
            uploaded_file = st.file_uploader("📤 Upload", type=None)
            if uploaded_file:
                self._handle_file_upload(uploaded_file)
        
        with op_col4:
            if st.button("📊 Statistics"):
                self._show_directory_stats(contents)
        
        # Handle dialogs
        self._handle_dialogs()
        
        # Display directories first
        if contents["directories"]:
            st.markdown("**📁 Directories:**")
            for dir_info in contents["directories"]:
                self._render_directory_item(dir_info)
        
        # Display files
        if contents["files"]:
            st.markdown("**📄 Files:**")
            for file_info in contents["files"]:
                self._render_file_item(file_info)
        
        # Show empty directory message
        if not contents["directories"] and not contents["files"]:
            st.info("📭 This directory is empty")
    
    def _render_directory_item(self, dir_info: Dict[str, Any]):
        """Render a directory item"""
        col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
        
        with col1:
            st.text(dir_info["icon"])
        
        with col2:
            if st.button(dir_info["name"], key=f"dir_{dir_info['path']}"):
                self.file_manager.current_path = dir_info["path"]
                st.rerun()
            st.caption(f"{dir_info['file_count']} files, {dir_info['dir_count']} dirs")
        
        with col3:
            st.text(dir_info["modified"].strftime("%m/%d %H:%M"))
        
        with col4:
            if st.button("✏️", key=f"rename_dir_{dir_info['path']}"):
                st.session_state.rename_item = dir_info["path"]
        
        with col5:
            if st.button("🗑️", key=f"delete_dir_{dir_info['path']}"):
                if st.session_state.get('confirm_delete') == dir_info["path"]:
                    self.file_manager.delete_item(dir_info["path"])
                    st.rerun()
                else:
                    st.session_state.confirm_delete = dir_info["path"]
                    st.warning("Click again to confirm deletion")
    
    def _render_file_item(self, file_info: Dict[str, Any]):
        """Render a file item"""
        col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
        
        with col1:
            st.text(file_info["icon"])
        
        with col2:
            if st.button(file_info["name"], key=f"file_{file_info['path']}"):
                st.session_state.selected_file = file_info["path"]
                st.session_state.show_file_viewer = True
            
            # Show AI summary if available
            if file_info["ai_summary"]:
                st.caption(f"🤖 {file_info['ai_summary'][:50]}...")
            
            # Show tags
            if file_info["tags"]:
                tag_str = " ".join([f"#{tag}" for tag in file_info["tags"]])
                st.caption(f"🏷️ {tag_str}")
        
        with col3:
            st.text(file_info["size_human"])
            st.caption(file_info["modified"].strftime("%m/%d %H:%M"))
        
        with col4:
            # Quick AI actions
            if st.button("🤖", key=f"ai_{file_info['path']}"):
                st.session_state.ai_target_file = file_info["path"]
                st.session_state.show_ai_panel = True
        
        with col5:
            if st.button("🗑️", key=f"delete_file_{file_info['path']}"):
                if st.session_state.get('confirm_delete') == file_info["path"]:
                    self.file_manager.delete_item(file_info["path"])
                    st.rerun()
                else:
                    st.session_state.confirm_delete = file_info["path"]
                    st.warning("Click again to confirm deletion")
    
    def _handle_file_upload(self, uploaded_file):
        """Handle file upload"""
        file_path = os.path.join(self.file_manager.current_path, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        self.file_manager._track_file_in_db(file_path)
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        st.rerun()
    
    def _handle_dialogs(self):
        """Handle various dialog modals"""
        # New file dialog
        if st.session_state.get('show_new_file_dialog'):
            with st.form("new_file_form"):
                st.subheader("📄 Create New File")
                filename = st.text_input("File name:", placeholder="example.txt")
                content = st.text_area("Initial content:", height=200)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Create"):
                        if filename:
                            if self.file_manager.create_file(filename, content):
                                st.success(f"✅ Created: {filename}")
                                st.session_state.show_new_file_dialog = False
                                st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_new_file_dialog = False
                        st.rerun()
        
        # New folder dialog
        if st.session_state.get('show_new_folder_dialog'):
            with st.form("new_folder_form"):
                st.subheader("📁 Create New Folder")
                foldername = st.text_input("Folder name:", placeholder="new_folder")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Create"):
                        if foldername:
                            if self.file_manager.create_directory(foldername):
                                st.success(f"✅ Created: {foldername}")
                                st.session_state.show_new_folder_dialog = False
                                st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_new_folder_dialog = False
                        st.rerun()
    
    def _show_directory_stats(self, contents: Dict[str, Any]):
        """Show directory statistics"""
        total_files = len(contents["files"])
        total_dirs = len(contents["directories"])
        total_size = sum(f["size"] for f in contents["files"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Files", total_files)
        col2.metric("Directories", total_dirs)
        col3.metric("Total Size", self.file_manager._format_file_size(total_size))
