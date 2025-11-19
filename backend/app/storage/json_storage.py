"""
JSON File Storage Manager
Handles all JSON file operations with thread-safety and atomic writes
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import threading
import shutil
from contextlib import contextmanager


class JSONStorage:
    """Thread-safe JSON file storage manager"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_lock(self, file_path: str) -> threading.Lock:
        """Get or create a lock for a specific file"""
        with self._global_lock:
            if file_path not in self._locks:
                self._locks[file_path] = threading.Lock()
            return self._locks[file_path]

    def _get_file_path(self, collection: str, filename: str = None) -> Path:
        """Get full file path for a collection"""
        collection_path = self.base_path / collection
        collection_path.mkdir(parents=True, exist_ok=True)

        if filename:
            return collection_path / f"{filename}.json"
        return collection_path

    @contextmanager
    def _atomic_write(self, file_path: Path):
        """Context manager for atomic file writes"""
        temp_path = file_path.with_suffix('.json.tmp')
        try:
            yield temp_path
            # Atomic rename
            shutil.move(str(temp_path), str(file_path))
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def read(self, collection: str, filename: str) -> Optional[Dict]:
        """Read a JSON file"""
        file_path = self._get_file_path(collection, filename)

        if not file_path.exists():
            return None

        lock = self._get_lock(str(file_path))
        with lock:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {file_path}: {e}")
            except Exception as e:
                raise IOError(f"Error reading {file_path}: {e}")

    def write(self, collection: str, filename: str, data: Dict) -> None:
        """Write data to a JSON file (atomic write)"""
        file_path = self._get_file_path(collection, filename)

        lock = self._get_lock(str(file_path))
        with lock:
            with self._atomic_write(file_path) as temp_path:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

    def list_all(self, collection: str) -> List[str]:
        """List all files in a collection"""
        collection_path = self._get_file_path(collection)

        if not collection_path.exists():
            return []

        files = []
        for file_path in collection_path.glob("*.json"):
            # Exclude temp files
            if not file_path.name.endswith('.tmp'):
                files.append(file_path.stem)

        return sorted(files)

    def delete(self, collection: str, filename: str) -> bool:
        """Delete a JSON file"""
        file_path = self._get_file_path(collection, filename)

        if not file_path.exists():
            return False

        lock = self._get_lock(str(file_path))
        with lock:
            try:
                file_path.unlink()
                return True
            except Exception as e:
                raise IOError(f"Error deleting {file_path}: {e}")

    def exists(self, collection: str, filename: str) -> bool:
        """Check if a file exists"""
        file_path = self._get_file_path(collection, filename)
        return file_path.exists()

    def update(self, collection: str, filename: str, updates: Dict) -> Dict:
        """Update a JSON file (merge with existing data)"""
        existing = self.read(collection, filename) or {}
        existing.update(updates)
        existing['updated_at'] = datetime.now().isoformat()
        self.write(collection, filename, existing)
        return existing

    def query(self, collection: str, filter_fn=None, limit: int = None) -> List[Dict]:
        """Query all files in a collection with optional filter"""
        results = []

        for filename in self.list_all(collection):
            data = self.read(collection, filename)
            if data:
                # Add metadata
                data['_id'] = filename

                # Apply filter
                if filter_fn is None or filter_fn(data):
                    results.append(data)

                    # Check limit
                    if limit and len(results) >= limit:
                        break

        return results

    def count(self, collection: str, filter_fn=None) -> int:
        """Count files in a collection with optional filter"""
        count = 0

        for filename in self.list_all(collection):
            if filter_fn is None:
                count += 1
            else:
                data = self.read(collection, filename)
                if data and filter_fn(data):
                    count += 1

        return count


class StorageManager:
    """High-level storage manager for specific collections"""

    def __init__(self, base_path: str = "data"):
        self.storage = JSONStorage(base_path)

    # Categories
    def get_category(self, category_id: str) -> Optional[Dict]:
        """Get a category by ID"""
        return self.storage.read("categories", category_id)

    def list_categories(self) -> List[Dict]:
        """List all categories"""
        return self.storage.query("categories")

    def create_category(self, category_id: str, data: Dict) -> Dict:
        """Create a new category"""
        data['id'] = category_id
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        self.storage.write("categories", category_id, data)
        return data

    def update_category(self, category_id: str, updates: Dict) -> Dict:
        """Update a category"""
        return self.storage.update("categories", category_id, updates)

    def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        return self.storage.delete("categories", category_id)

    # Templates
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a template by ID"""
        return self.storage.read("templates", template_id)

    def list_templates(self) -> List[Dict]:
        """List all templates"""
        return self.storage.query("templates")

    def create_template(self, template_id: str, data: Dict) -> Dict:
        """Create a new template"""
        data['id'] = template_id
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        self.storage.write("templates", template_id, data)
        return data

    def update_template(self, template_id: str, updates: Dict) -> Dict:
        """Update a template"""
        return self.storage.update("templates", template_id, updates)

    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        return self.storage.delete("templates", template_id)

    # Posts
    def get_post(self, post_id: str) -> Optional[Dict]:
        """Get a post by ID"""
        return self.storage.read("posts", post_id)

    def list_posts(self, category: str = None, status: str = None, limit: int = None) -> List[Dict]:
        """List posts with optional filters"""
        def filter_fn(post):
            if category and post.get('category') != category:
                return False
            if status and post.get('status') != status:
                return False
            return True

        return self.storage.query("posts", filter_fn=filter_fn if (category or status) else None, limit=limit)

    def create_post(self, post_id: str, data: Dict) -> Dict:
        """Create a new post"""
        data['id'] = post_id
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        data.setdefault('status', 'draft')
        self.storage.write("posts", post_id, data)
        return data

    def update_post(self, post_id: str, updates: Dict) -> Dict:
        """Update a post"""
        return self.storage.update("posts", post_id, updates)

    def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        return self.storage.delete("posts", post_id)

    # Settings
    def get_settings(self) -> Dict:
        """Get application settings"""
        settings = self.storage.read("settings", "app_settings")
        if not settings:
            # Return default settings
            return {
                "app_name": "LinkedIn Content Automation",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat()
            }
        return settings

    def update_settings(self, updates: Dict) -> Dict:
        """Update application settings"""
        settings = self.get_settings()
        settings.update(updates)
        settings['updated_at'] = datetime.now().isoformat()
        self.storage.write("settings", "app_settings", settings)
        return settings

    # Statistics
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        return {
            "categories": len(self.storage.list_all("categories")),
            "templates": len(self.storage.list_all("templates")),
            "posts": len(self.storage.list_all("posts")),
            "posts_by_status": {
                "draft": self.storage.count("posts", lambda p: p.get('status') == 'draft'),
                "review": self.storage.count("posts", lambda p: p.get('status') == 'review'),
                "approved": self.storage.count("posts", lambda p: p.get('status') == 'approved'),
                "published": self.storage.count("posts", lambda p: p.get('status') == 'published'),
            }
        }


# Singleton instance
_storage_instance = None


def get_storage() -> StorageManager:
    """Get storage manager singleton"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageManager(base_path="data")
    return _storage_instance
