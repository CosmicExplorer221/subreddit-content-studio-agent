"""
Database Schema Definition
Following backend-architect.md specifications
"""
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def init_db(db_path: str = "data/linkedin_automation.db") -> None:
    """
    Initialize database with schema
    Creates all tables if they don't exist
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Posts table - stores Reddit posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reddit_post_id TEXT UNIQUE NOT NULL,
                subreddit TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                author TEXT,
                score INTEGER DEFAULT 0,
                num_comments INTEGER DEFAULT 0,
                upvote_ratio REAL DEFAULT 0.0,
                created_utc INTEGER,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                permalink TEXT,
                flair TEXT,
                media_type TEXT,
                media_urls TEXT,
                top_comments TEXT
            )
        """)

        # Create indexes for posts table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_reddit_post_id ON posts(reddit_post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_fetched_at ON posts(fetched_at)")

        # LinkedIn posts table - stores generated LinkedIn content
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                quality_score INTEGER DEFAULT 0,
                variation_number INTEGER DEFAULT 1,
                template_id TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_date TIMESTAMP,
                published_date TIMESTAMP,
                hashtags TEXT,
                notion_page_id TEXT,
                notion_synced_at TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for linkedin_posts table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_posts_post_id ON linkedin_posts(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_posts_status ON linkedin_posts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_posts_quality_score ON linkedin_posts(quality_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_posts_template_id ON linkedin_posts(template_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_posts_notion_page_id ON linkedin_posts(notion_page_id)")

        # Media files table - tracks downloaded media
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                duration REAL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'downloaded',
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for media_files table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_files_post_id ON media_files(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_files_file_type ON media_files(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_files_status ON media_files(status)")

        # Reddit comments table - stores top comments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reddit_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                comment_id TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT,
                score INTEGER DEFAULT 0,
                created_utc INTEGER,
                is_top BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for reddit_comments table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_comments_post_id ON reddit_comments(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_comments_score ON reddit_comments(score)")

        # Analytics table - tracks performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkedin_post_id INTEGER,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (linkedin_post_id) REFERENCES linkedin_posts(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for analytics table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_linkedin_post_id ON analytics(linkedin_post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_recorded_at ON analytics(recorded_at)")

        # Job queue table - background jobs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                job_type TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                progress INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                params TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Create indexes for job_queue table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_queue_job_id ON job_queue(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_queue_job_type ON job_queue(job_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_queue_created_at ON job_queue(created_at)")

        # Config table - application configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database schema initialized successfully")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


def migrate_db(db_path: str = "data/linkedin_automation.db") -> None:
    """
    Run database migrations
    Add any schema changes here
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Future migrations will go here
        # Example:
        # cursor.execute("ALTER TABLE posts ADD COLUMN new_field TEXT")

        conn.commit()
        logger.info("Database migrations completed")

    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()
