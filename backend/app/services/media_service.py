"""
Media Download Service
Implements media-handler agent for downloading and managing media files
"""
import aiohttp
import aiofiles
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class MediaDownloader:
    """Async media downloader for videos and images"""

    def __init__(self, base_path: str = "downloads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_category_path(self, category: str) -> Path:
        """Get path for category"""
        category_path = self.base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        return category_path

    def _get_file_extension(self, url: str, content_type: str = None) -> str:
        """Extract file extension from URL or content-type"""
        # Try URL first
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1]

        if ext and ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mov']:
            return ext

        # Try content-type header
        if content_type:
            ext_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'video/mp4': '.mp4',
                'video/webm': '.webm',
                'video/quicktime': '.mov'
            }
            return ext_map.get(content_type, '.bin')

        # Default
        return '.jpg' if 'jpg' in url or 'jpeg' in url else '.mp4'

    def _validate_file(self, file_path: Path, expected_type: str = None) -> bool:
        """Validate downloaded file"""
        if not file_path.exists():
            return False

        # Check minimum size (avoid empty files)
        if os.path.getsize(file_path) < 1024:  # 1KB minimum
            return False

        # Check file signature (magic numbers)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)

            # Image signatures
            image_sigs = [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89\x50\x4E\x47',  # PNG
                b'\x47\x49\x46\x38'  # GIF
            ]

            # Video signatures
            video_sigs = [
                b'ftyp',  # MP4 (partial)
                b'\x1A\x45\xDF\xA3'  # WEBM
            ]

            # Check if valid media file
            is_image = any(header.startswith(sig) for sig in image_sigs)
            is_video = b'ftyp' in header or header.startswith(b'\x1A\x45\xDF\xA3')

            return is_image or is_video

        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False

    async def download_file(
        self,
        url: str,
        category: str,
        post_id: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Download a single file

        Args:
            url: URL to download
            category: Category for organization
            post_id: Post ID for subdirectory
            filename: Optional custom filename

        Returns:
            Dictionary with download status and metadata
        """
        try:
            # Create post directory
            post_dir = self._get_category_path(category) / post_id
            post_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename if not provided
            if not filename:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"media_{url_hash}"

            logger.info(f"Downloading: {url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status != 200:
                        return {
                            "status": "failed",
                            "url": url,
                            "error": f"HTTP {response.status}"
                        }

                    # Get file extension
                    content_type = response.headers.get('content-type', '')
                    ext = self._get_file_extension(url, content_type)

                    # Determine media type
                    if 'image' in content_type or ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        media_type = "image"
                    elif 'video' in content_type or ext in ['.mp4', '.webm', '.mov']:
                        media_type = "video"
                    else:
                        media_type = "unknown"

                    # Create file path
                    file_path = post_dir / f"{filename}{ext}"

                    # Download file in chunks
                    file_size = 0
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            file_size += len(chunk)

                    # Validate file
                    if not self._validate_file(file_path):
                        os.remove(file_path)
                        return {
                            "status": "failed",
                            "url": url,
                            "error": "File validation failed"
                        }

                    logger.info(f"  ✓ Downloaded: {file_path.name} ({file_size / 1024:.1f} KB)")

                    return {
                        "status": "success",
                        "url": url,
                        "file_path": str(file_path),
                        "filename": file_path.name,
                        "media_type": media_type,
                        "file_size": file_size,
                        "content_type": content_type
                    }

        except asyncio.TimeoutError:
            return {
                "status": "failed",
                "url": url,
                "error": "Download timeout"
            }

        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return {
                "status": "failed",
                "url": url,
                "error": str(e)
            }

    async def download_reddit_video(
        self,
        video_url: str,
        category: str,
        post_id: str
    ) -> Dict:
        """
        Download Reddit video (handles DASH format)

        Reddit videos are often in DASH format with separate audio/video streams.
        This downloads the video stream. For audio merging, ffmpeg would be needed.
        """
        try:
            # Reddit video URLs often end with /DASH_xxx.mp4
            # We'll download the main video stream
            base_url = video_url.rsplit('/', 1)[0]

            # Try different quality options
            quality_options = ['DASH_720.mp4', 'DASH_480.mp4', 'DASH_360.mp4']

            for quality in quality_options:
                try_url = f"{base_url}/{quality}"

                result = await self.download_file(
                    url=try_url,
                    category=category,
                    post_id=post_id,
                    filename="video"
                )

                if result["status"] == "success":
                    logger.info(f"  ✓ Downloaded Reddit video at {quality}")
                    return result

            # If all qualities failed, try original URL
            return await self.download_file(
                url=video_url,
                category=category,
                post_id=post_id,
                filename="video"
            )

        except Exception as e:
            logger.error(f"Error downloading Reddit video: {e}")
            return {
                "status": "failed",
                "url": video_url,
                "error": str(e)
            }

    async def download_post_media(
        self,
        post_id: str,
        category: str,
        media_urls: List[str],
        media_type: Optional[str] = None
    ) -> Dict:
        """
        Download all media for a post

        Args:
            post_id: Reddit post ID
            category: Category for organization
            media_urls: List of media URLs
            media_type: Type of media (image, video, gallery)

        Returns:
            Dictionary with download results
        """
        if not media_urls:
            return {
                "status": "success",
                "post_id": post_id,
                "downloaded": [],
                "failed": [],
                "message": "No media URLs to download"
            }

        logger.info(f"Downloading {len(media_urls)} media file(s) for post {post_id}")

        downloaded = []
        failed = []

        # Download all media files
        for idx, url in enumerate(media_urls):
            # Special handling for Reddit videos
            if 'v.redd.it' in url or 'reddit_video' in url:
                result = await self.download_reddit_video(url, category, post_id)
            else:
                result = await self.download_file(
                    url=url,
                    category=category,
                    post_id=post_id,
                    filename=f"media_{idx + 1}" if len(media_urls) > 1 else "media"
                )

            if result["status"] == "success":
                downloaded.append(result)
            else:
                failed.append(result)

            # Small delay between downloads
            await asyncio.sleep(0.5)

        success_count = len(downloaded)
        fail_count = len(failed)

        logger.info(f"✓ Downloaded {success_count}/{len(media_urls)} media files for post {post_id}")

        return {
            "status": "success" if success_count > 0 else "failed",
            "post_id": post_id,
            "category": category,
            "downloaded": downloaded,
            "failed": failed,
            "summary": {
                "total": len(media_urls),
                "success": success_count,
                "failed": fail_count
            }
        }

    def get_post_media_info(self, category: str, post_id: str) -> Dict:
        """
        Get information about downloaded media for a post
        """
        post_dir = self._get_category_path(category) / post_id

        if not post_dir.exists():
            return {
                "post_id": post_id,
                "category": category,
                "exists": False,
                "files": []
            }

        files = []
        for file_path in post_dir.glob("*"):
            if file_path.is_file() and not file_path.name.endswith('.json'):
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })

        return {
            "post_id": post_id,
            "category": category,
            "exists": True,
            "files": files,
            "count": len(files)
        }

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_size = 0
        file_count = 0
        categories = {}

        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir():
                category_size = 0
                category_files = 0

                for file_path in category_dir.rglob("*"):
                    if file_path.is_file():
                        size = os.path.getsize(file_path)
                        total_size += size
                        category_size += size
                        file_count += 1
                        category_files += 1

                categories[category_dir.name] = {
                    "files": category_files,
                    "size_mb": category_size / (1024 * 1024)
                }

        return {
            "total_files": file_count,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "categories": categories
        }


# Singleton instance
_media_downloader = None


def get_media_downloader() -> MediaDownloader:
    """Get media downloader singleton"""
    global _media_downloader
    if _media_downloader is None:
        _media_downloader = MediaDownloader(base_path="downloads")
    return _media_downloader
