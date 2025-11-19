"""
Migration Script: JSON to SQLite
Migrates existing JSON data to SQLite database
"""
import json
import sqlite3
from pathlib import Path
import logging
from datetime import datetime
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.schema import init_db
from app.database.connection import get_db_manager
from app.repositories import (
    PostRepository,
    LinkedInPostRepository,
    MediaRepository,
    JobRepository
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONToSQLiteMigrator:
    """Migrates data from JSON files to SQLite database"""

    def __init__(self, data_dir: str = "data", db_path: str = "data/linkedin_automation.db"):
        self.data_dir = Path(data_dir)
        self.db_path = db_path
        self.db_manager = get_db_manager(db_path)

    def migrate_all(self) -> dict:
        """
        Migrate all JSON data to SQLite

        Returns:
            Dictionary with migration statistics
        """
        logger.info("=" * 60)
        logger.info("Starting JSON to SQLite Migration")
        logger.info("=" * 60)

        # Initialize database
        logger.info("Initializing database schema...")
        init_db(self.db_path)

        stats = {
            'posts': 0,
            'linkedin_posts': 0,
            'media_files': 0,
            'jobs': 0,
            'errors': []
        }

        # Migrate posts
        logger.info("\n1. Migrating Reddit posts...")
        try:
            stats['posts'] = self.migrate_posts()
            logger.info(f"✓ Migrated {stats['posts']} Reddit posts")
        except Exception as e:
            logger.error(f"✗ Failed to migrate posts: {e}")
            stats['errors'].append(f"Posts migration: {e}")

        # Migrate LinkedIn posts (they are stored in posts JSON files)
        logger.info("\n2. Migrating LinkedIn posts...")
        try:
            stats['linkedin_posts'] = self.migrate_linkedin_posts()
            logger.info(f"✓ Migrated {stats['linkedin_posts']} LinkedIn posts")
        except Exception as e:
            logger.error(f"✗ Failed to migrate LinkedIn posts: {e}")
            stats['errors'].append(f"LinkedIn posts migration: {e}")

        # Migrate jobs
        logger.info("\n3. Migrating background jobs...")
        try:
            stats['jobs'] = self.migrate_jobs()
            logger.info(f"✓ Migrated {stats['jobs']} jobs")
        except Exception as e:
            logger.error(f"✗ Failed to migrate jobs: {e}")
            stats['errors'].append(f"Jobs migration: {e}")

        logger.info("\n" + "=" * 60)
        logger.info("Migration Complete!")
        logger.info(f"Total migrated:")
        logger.info(f"  - Reddit posts: {stats['posts']}")
        logger.info(f"  - LinkedIn posts: {stats['linkedin_posts']}")
        logger.info(f"  - Jobs: {stats['jobs']}")
        if stats['errors']:
            logger.warning(f"\nErrors encountered: {len(stats['errors'])}")
            for error in stats['errors']:
                logger.warning(f"  - {error}")
        logger.info("=" * 60)

        return stats

    def migrate_posts(self) -> int:
        """Migrate Reddit posts from JSON to SQLite"""
        posts_dir = self.data_dir / "posts"
        if not posts_dir.exists():
            logger.warning(f"Posts directory not found: {posts_dir}")
            return 0

        count = 0

        with self.db_manager.get_db() as conn:
            post_repo = PostRepository(conn)

            for json_file in posts_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        post_data = json.load(f)

                    # Check if post already exists
                    if post_repo.post_exists(post_data.get('reddit_post_id')):
                        logger.debug(f"Skipping existing post: {post_data.get('reddit_post_id')}")
                        continue

                    # Create post
                    post_repo.create(post_data)
                    count += 1

                except Exception as e:
                    logger.error(f"Failed to migrate {json_file.name}: {e}")
                    continue

        return count

    def migrate_linkedin_posts(self) -> int:
        """Migrate LinkedIn posts from JSON to SQLite"""
        posts_dir = self.data_dir / "posts"
        if not posts_dir.exists():
            return 0

        count = 0

        with self.db_manager.get_db() as conn:
            post_repo = PostRepository(conn)
            linkedin_repo = LinkedInPostRepository(conn)

            for json_file in posts_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    # Check if this JSON contains LinkedIn content
                    if 'linkedin_content' not in data:
                        continue

                    # Get the corresponding Reddit post
                    reddit_post = post_repo.get_by_reddit_id(data.get('reddit_post_id'))
                    if not reddit_post:
                        logger.warning(f"Reddit post not found for LinkedIn content: {data.get('reddit_post_id')}")
                        continue

                    # Create LinkedIn post
                    linkedin_data = {
                        'post_id': reddit_post['id'],
                        'content': data['linkedin_content'].get('content', ''),
                        'status': data.get('status', 'draft'),
                        'quality_score': data['linkedin_content'].get('quality_score', 0),
                        'variation_number': 1,
                        'template_id': data.get('template_id'),
                        'hashtags': json.dumps(data['linkedin_content'].get('hashtags', [])),
                        'notion_page_id': data.get('notion_page_id'),
                        'notion_synced_at': data.get('notion_synced_at')
                    }

                    linkedin_repo.create(linkedin_data)
                    count += 1

                except Exception as e:
                    logger.error(f"Failed to migrate LinkedIn post from {json_file.name}: {e}")
                    continue

        return count

    def migrate_jobs(self) -> int:
        """Migrate jobs from JSON to SQLite"""
        jobs_dir = self.data_dir / "jobs"
        if not jobs_dir.exists():
            logger.warning(f"Jobs directory not found: {jobs_dir}")
            return 0

        count = 0

        with self.db_manager.get_db() as conn:
            job_repo = JobRepository(conn)

            for json_file in jobs_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        job_data = json.load(f)

                    # Check if job already exists
                    if job_repo.get_by_job_id(job_data.get('job_id')):
                        logger.debug(f"Skipping existing job: {job_data.get('job_id')}")
                        continue

                    # Create job
                    job_repo.create(job_data)
                    count += 1

                except Exception as e:
                    logger.error(f"Failed to migrate {json_file.name}: {e}")
                    continue

        return count

    def verify_migration(self) -> dict:
        """Verify migration by comparing counts"""
        logger.info("\nVerifying migration...")

        verification = {}

        with self.db_manager.get_db() as conn:
            post_repo = PostRepository(conn)
            linkedin_repo = LinkedInPostRepository(conn)
            job_repo = JobRepository(conn)

            # Check counts
            verification['db_posts'] = post_repo.get_statistics()['total_posts']
            verification['db_linkedin'] = linkedin_repo.get_statistics()['total_posts']
            verification['db_jobs'] = job_repo.get_statistics()['total_jobs']

        # Count JSON files
        posts_dir = self.data_dir / "posts"
        jobs_dir = self.data_dir / "jobs"

        verification['json_posts'] = len(list(posts_dir.glob("*.json"))) if posts_dir.exists() else 0
        verification['json_jobs'] = len(list(jobs_dir.glob("*.json"))) if jobs_dir.exists() else 0

        logger.info(f"Database posts: {verification['db_posts']}")
        logger.info(f"Database LinkedIn posts: {verification['db_linkedin']}")
        logger.info(f"Database jobs: {verification['db_jobs']}")
        logger.info(f"JSON post files: {verification['json_posts']}")
        logger.info(f"JSON job files: {verification['json_jobs']}")

        return verification


def main():
    """Run migration"""
    migrator = JSONToSQLiteMigrator()

    # Run migration
    stats = migrator.migrate_all()

    # Verify
    verification = migrator.verify_migration()

    logger.info("\n✓ Migration completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Review the migrated data in data/linkedin_automation.db")
    logger.info("2. Test the application with the new database")
    logger.info("3. If everything works, you can archive the old JSON files")
    logger.info("4. Update services to use repositories instead of JSON storage")


if __name__ == "__main__":
    main()
