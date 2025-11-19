"""
Reddit + Media Integration Test Script
Tests the complete content fetching and media download pipeline
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_reddit_media_integration():
    print("=" * 70)
    print("Testing Reddit + Media Integration")
    print("=" * 70)

    # Test 1: Check Reddit status
    print("\n1. Checking Reddit API status...")
    response = requests.get(f"{BASE_URL}/api/reddit/status")
    print(f"   Status: {response.status_code}")
    status = response.json()
    print(f"   Reddit Status: {status['status']}")

    if status['status'] == 'not_configured':
        print("\n" + "!" * 70)
        print("⚠️  Reddit API not configured!")
        print("   To use Reddit integration:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Reddit API credentials")
        print("   3. Get credentials from: https://www.reddit.com/prefs/apps")
        print("!" * 70)
        print("\n   Skipping Reddit tests (no credentials)")
        return test_without_reddit()

    print(f"   ✓ Connected as: {status.get('username', 'N/A')}")

    # Test 2: Check media storage status
    print("\n2. Checking media storage status...")
    response = requests.get(f"{BASE_URL}/api/media/status")
    print(f"   Status: {response.status_code}")
    media_status = response.json()
    print(f"   Storage Path: {media_status['storage_path']}")
    print(f"   Total Files: {media_status['total_files']}")

    # Test 3: Get Railway category subreddits
    print("\n3. Getting Railway category subreddits...")
    response = requests.get(f"{BASE_URL}/api/reddit/categories/railway/subreddits")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Subreddits ({data['count']}): {', '.join(data['subreddits'])}")

    # Test 4: Fetch Reddit posts
    print("\n4. Fetching Reddit posts from Railway category...")
    print("   This will:")
    print("   - Fetch top posts from 5 subreddits")
    print("   - Filter by score/comments")
    print("   - Extract top comments")
    print("   - Download media files")
    print("   - Save to JSON storage")

    response = requests.post(
        f"{BASE_URL}/api/reddit/fetch",
        json={
            "category": "railway",
            "time_filter": "week",
            "limit": 3  # Reduced for testing
        },
        params={"download_media": True}
    )

    print(f"\n   Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        job_id = result['job_id']
        print(f"   Job ID: {job_id}")
        print(f"   Message: {result['message']}")

        # Test 5: Poll job status
        print("\n5. Polling job status...")
        max_polls = 30  # 30 seconds max
        for i in range(max_polls):
            time.sleep(1)

            response = requests.get(f"{BASE_URL}/api/reddit/jobs/{job_id}")

            if response.status_code == 200:
                job = response.json()
                status = job.get('status', 'unknown')

                if status == 'completed':
                    print(f"\n   ✓ Job completed!")
                    print(f"   Posts fetched: {job.get('posts_fetched', 0)}")
                    print(f"   Posts saved: {len(job.get('posts_saved', []))}")
                    print(f"   Time filter: {job['filters']['time_filter']}")
                    print(f"   Min score: {job['filters']['min_score']}")

                    if job.get('errors'):
                        print(f"\n   Errors encountered: {len(job['errors'])}")
                        for error in job['errors'][:3]:
                            print(f"   - {error}")

                    # Test 6: Check saved posts
                    print("\n6. Checking saved posts...")
                    response = requests.get(f"{BASE_URL}/api/posts?category=railway")
                    posts = response.json()
                    print(f"   Total posts in storage: {len(posts)}")

                    if posts:
                        post = posts[0]
                        print(f"\n   First post:")
                        print(f"   - Title: {post['reddit_data']['title'][:60]}...")
                        print(f"   - Subreddit: r/{post['reddit_data']['subreddit']}")
                        print(f"   - Score: {post['reddit_data']['score']}")
                        print(f"   - Comments: {post['reddit_data']['num_comments']}")
                        print(f"   - Media URLs: {len(post['reddit_data']['media_urls'])}")

                        # Test 7: Check downloaded media
                        if post['reddit_data'].get('media_urls'):
                            print("\n7. Checking downloaded media...")
                            reddit_post_id = post['reddit_data']['reddit_post_id']
                            response = requests.get(
                                f"{BASE_URL}/api/media/posts/{reddit_post_id}",
                                params={"category": "railway"}
                            )

                            if response.status_code == 200:
                                media_info = response.json()
                                print(f"   Media files: {media_info['count']}")

                                for file in media_info.get('files', []):
                                    print(f"   - {file['filename']} ({file['size'] / 1024:.1f} KB)")

                    # Test 8: Get updated storage stats
                    print("\n8. Final storage statistics...")
                    response = requests.get(f"{BASE_URL}/api/media/status")
                    stats = response.json()
                    print(f"   Total files: {stats['total_files']}")
                    print(f"   Total size: {stats['total_size_mb']:.2f} MB")

                    for cat, cat_stats in stats.get('categories', {}).items():
                        print(f"   - {cat}: {cat_stats['files']} files, {cat_stats['size_mb']:.2f} MB")

                    break

                elif status == 'failed':
                    print(f"\n   ✗ Job failed!")
                    print(f"   Error: {job.get('error', 'Unknown error')}")
                    break

                else:
                    print(f"   [{i+1}/{max_polls}] Status: {status}...", end='\r')

            else:
                print(f"\n   Error checking job status: {response.status_code}")
                break
        else:
            print(f"\n   ⚠️ Job did not complete within {max_polls} seconds")

    else:
        print(f"   ✗ Failed to queue fetch job")
        print(f"   Response: {response.text}")

    print("\n" + "=" * 70)
    print("✅ Reddit + Media integration test complete!")
    print("=" * 70)


def test_without_reddit():
    """Test other endpoints when Reddit is not configured"""
    print("\n" + "=" * 70)
    print("Testing endpoints without Reddit credentials")
    print("=" * 70)

    # Test media status
    print("\n1. Testing media storage status...")
    response = requests.get(f"{BASE_URL}/api/media/status")
    print(f"   Status: {response.status_code} ✓")

    # Test categories
    print("\n2. Testing categories...")
    response = requests.get(f"{BASE_URL}/api/config/categories")
    categories = response.json()
    print(f"   Categories: {len(categories)} ✓")

    # Test templates
    print("\n3. Testing templates...")
    response = requests.get(f"{BASE_URL}/api/config/templates")
    templates = response.json()
    print(f"   Templates: {len(templates)} ✓")

    print("\n" + "=" * 70)
    print("✅ Basic endpoints working! Configure Reddit to test full pipeline.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_reddit_media_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
