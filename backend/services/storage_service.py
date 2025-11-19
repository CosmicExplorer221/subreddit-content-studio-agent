"""
JSON Storage Service - Following backend-architect.md
Simple file-based storage for development/local use
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


class JSONStorage:
    """Simple JSON file storage service"""

    def __init__(self):
        """Initialize storage and ensure data directory exists"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure all required JSON files exist"""
        required_files = {
            "posts.json": {"posts": []},
            "generated_posts.json": {"generated_posts": []},
            "templates.json": {"templates": []},
            "categories.json": {"categories": []},
            "settings.json": {}
        }

        for filename, default_data in required_files.items():
            filepath = DATA_DIR / filename
            if not filepath.exists():
                self._write_json(filepath, default_data)
                logger.info(f"Created {filename} with default data")

    def _read_json(self, filepath: Path) -> Dict:
        """Read JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}, returning empty dict")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {e}")
            return {}

    def _write_json(self, filepath: Path, data: Dict):
        """Write JSON file atomically"""
        temp_file = filepath.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(filepath)
            logger.debug(f"Successfully wrote {filepath}")
        except Exception as e:
            logger.error(f"Error writing {filepath}: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise

    # === Posts ===

    def get_posts(self, category: Optional[str] = None) -> List[Dict]:
        """Get all posts, optionally filtered by category"""
        data = self._read_json(DATA_DIR / "posts.json")
        posts = data.get("posts", [])

        if category:
            posts = [p for p in posts if p.get("category") == category]

        return posts

    def get_post_by_id(self, post_id: str) -> Optional[Dict]:
        """Get a specific post by ID"""
        posts = self.get_posts()
        for post in posts:
            if post.get("id") == post_id:
                return post
        return None

    # === Generated Posts ===

    def get_generated_posts(self) -> List[Dict]:
        """Get all generated posts"""
        data = self._read_json(DATA_DIR / "generated_posts.json")
        return data.get("generated_posts", [])

    def get_generated_post_by_id(self, gen_post_id: str) -> Optional[Dict]:
        """Get a specific generated post by ID"""
        posts = self.get_generated_posts()
        for post in posts:
            if post.get("id") == gen_post_id:
                return post
        return None

    def save_generated_post(self, generated_post: Dict) -> Dict:
        """Save a generated post"""
        data = self._read_json(DATA_DIR / "generated_posts.json")
        posts = data.get("generated_posts", [])

        # Check if already exists
        existing_index = next(
            (i for i, p in enumerate(posts) if p.get("id") == generated_post.get("id")),
            None
        )

        if existing_index is not None:
            posts[existing_index] = generated_post
            logger.info(f"Updated generated post {generated_post.get('id')}")
        else:
            posts.append(generated_post)
            logger.info(f"Created generated post {generated_post.get('id')}")

        data["generated_posts"] = posts
        self._write_json(DATA_DIR / "generated_posts.json", data)

        return generated_post

    def update_generated_post(self, gen_post_id: str, updates: Dict) -> Optional[Dict]:
        """Update a generated post"""
        post = self.get_generated_post_by_id(gen_post_id)
        if not post:
            return None

        post.update(updates)
        return self.save_generated_post(post)

    def delete_generated_post(self, gen_post_id: str) -> bool:
        """Delete a generated post"""
        data = self._read_json(DATA_DIR / "generated_posts.json")
        posts = data.get("generated_posts", [])

        original_length = len(posts)
        posts = [p for p in posts if p.get("id") != gen_post_id]

        if len(posts) < original_length:
            data["generated_posts"] = posts
            self._write_json(DATA_DIR / "generated_posts.json", data)
            logger.info(f"Deleted generated post {gen_post_id}")
            return True

        return False

    # === Templates ===

    def get_templates(self, category: Optional[str] = None) -> List[Dict]:
        """Get all templates, optionally filtered by category"""
        data = self._read_json(DATA_DIR / "templates.json")
        templates = data.get("templates", [])

        if category:
            templates = [t for t in templates if t.get("category") == category]

        return templates

    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID"""
        templates = self.get_templates()
        for template in templates:
            if template.get("id") == template_id:
                return template
        return None

    # === Categories ===

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        data = self._read_json(DATA_DIR / "categories.json")
        return data.get("categories", [])

    def get_category_by_id(self, category_id: str) -> Optional[Dict]:
        """Get a specific category by ID"""
        categories = self.get_categories()
        for category in categories:
            if category.get("id") == category_id:
                return category
        return None

    # === Settings ===

    def get_settings(self) -> Dict:
        """Get application settings"""
        return self._read_json(DATA_DIR / "settings.json")

    def update_settings(self, settings: Dict):
        """Update application settings"""
        current = self.get_settings()
        current.update(settings)
        self._write_json(DATA_DIR / "settings.json", current)
        logger.info("Updated settings")


# Singleton instance
_storage = None

def get_storage() -> JSONStorage:
    """Get storage singleton instance"""
    global _storage
    if _storage is None:
        _storage = JSONStorage()
    return _storage
