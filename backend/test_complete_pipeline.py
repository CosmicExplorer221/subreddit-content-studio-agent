"""
Complete Pipeline Integration Test
Tests the full LinkedIn content automation workflow:
1. Reddit content fetching + Media downloads
2. Content generation with Gemini
3. Notion database sync
"""
import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_step(step_num: int, description: str):
    """Print a step header"""
    print(f"\n{step_num}. {description}")
    print("-" * 70)


def check_service_status(service_name: str, endpoint: str) -> Dict:
    """Check if a service is configured"""
    response = requests.get(f"{BASE_URL}{endpoint}")
    status = response.json()

    print(f"   {service_name} Status: ", end="")

    if status.get('status') in ['configured', 'connected', 'active']:
        print(f"✓ {status.get('status')}")
        return {'configured': True, 'status': status}
    elif status.get('status') == 'not_configured':
        print(f"✗ Not configured")
        return {'configured': False, 'status': status}
    else:
        print(f"⚠️  {status.get('status', 'unknown')}")
        return {'configured': True, 'status': status}


def poll_job(job_id: str, max_wait: int = 60) -> Dict:
    """Poll a background job until completion"""
    print(f"   Polling job {job_id[:8]}...")

    for i in range(max_wait):
        time.sleep(1)

        response = requests.get(f"{BASE_URL}/api/reddit/jobs/{job_id}")

        if response.status_code == 200:
            job = response.json()
            status = job.get('status', 'unknown')

            if status == 'completed':
                print(f"   ✓ Job completed!")
                return job
            elif status == 'failed':
                print(f"   ✗ Job failed: {job.get('error', 'Unknown error')}")
                return job
            else:
                print(f"   [{i+1}/{max_wait}] Status: {status}...", end='\r')
        else:
            print(f"   ✗ Error checking job: {response.status_code}")
            return None

    print(f"\n   ⚠️  Job did not complete within {max_wait} seconds")
    return None


def test_complete_pipeline():
    """Test the complete automation pipeline"""

    print_section("LinkedIn Content Automation - Complete Pipeline Test")

    # Track results
    results = {
        'reddit_configured': False,
        'gemini_configured': False,
        'notion_configured': False,
        'posts_fetched': 0,
        'posts_generated': 0,
        'posts_synced': 0,
        'post_ids': []
    }

    # ========================================================================
    # STEP 1: Check all service statuses
    # ========================================================================
    print_step(1, "Checking Service Configurations")

    # Check Reddit
    reddit_check = check_service_status("Reddit API", "/api/reddit/status")
    results['reddit_configured'] = reddit_check['configured']

    # Check Gemini
    gemini_check = check_service_status("Gemini API", "/api/config/settings")
    # Gemini check is indirect - we'll test it when generating

    # Check Notion
    notion_check = check_service_status("Notion API", "/api/notion/status")
    results['notion_configured'] = notion_check['configured']

    # Check Media
    media_check = check_service_status("Media Storage", "/api/media/status")

    print("\n   Configuration Summary:")
    print(f"   - Reddit API: {'✓' if results['reddit_configured'] else '✗'}")
    print(f"   - Gemini API: (will test during generation)")
    print(f"   - Notion API: {'✓' if results['notion_configured'] else '✗'}")
    print(f"   - Media Storage: ✓")

    # ========================================================================
    # STEP 2: Fetch Reddit posts with media
    # ========================================================================
    if not results['reddit_configured']:
        print_step(2, "Skipping Reddit Fetch (Not Configured)")
        print("\n   ⚠️  Reddit API not configured.")
        print("   To test the full pipeline, configure Reddit credentials in .env")
        print("   See .env.example for instructions")
        return results

    print_step(2, "Fetching Reddit Posts from Railway Category")
    print("   Configuration:")
    print("   - Category: railway")
    print("   - Time filter: week")
    print("   - Limit: 3 posts")
    print("   - Download media: Yes")

    response = requests.post(
        f"{BASE_URL}/api/reddit/fetch",
        json={
            "category": "railway",
            "time_filter": "week",
            "limit": 3
        },
        params={"download_media": True}
    )

    if response.status_code != 200:
        print(f"\n   ✗ Failed to start fetch job: {response.status_code}")
        print(f"   Response: {response.text}")
        return results

    fetch_result = response.json()
    fetch_job_id = fetch_result['job_id']

    print(f"\n   Job queued: {fetch_job_id[:8]}...")

    # Poll fetch job
    fetch_job = poll_job(fetch_job_id, max_wait=60)

    if not fetch_job or fetch_job.get('status') != 'completed':
        print("\n   ✗ Fetch job did not complete successfully")
        return results

    results['posts_fetched'] = len(fetch_job.get('posts_saved', []))
    results['post_ids'] = fetch_job.get('posts_saved', [])

    print(f"\n   Posts fetched: {results['posts_fetched']}")
    print(f"   Post IDs: {', '.join([pid[:8] + '...' for pid in results['post_ids']])}")

    if results['posts_fetched'] == 0:
        print("\n   ⚠️  No posts fetched. Try adjusting filters or time range.")
        return results

    # ========================================================================
    # STEP 3: Generate LinkedIn content with Gemini
    # ========================================================================
    print_step(3, "Generating LinkedIn Content with Gemini")
    print(f"   Posts to generate: {len(results['post_ids'])}")
    print("   Template: professional (category default)")
    print("   Variations: 2")

    response = requests.post(
        f"{BASE_URL}/api/posts/generate",
        json={
            "post_ids": results['post_ids'],
            "template_id": "professional",
            "variations": 2
        }
    )

    if response.status_code == 503:
        print("\n   ✗ Gemini API not configured")
        print("   Set GEMINI_API_KEY in .env file to enable content generation")
        print("   Get API key from: https://makersuite.google.com/app/apikey")
        results['gemini_configured'] = False
        return results
    elif response.status_code != 200:
        print(f"\n   ✗ Failed to start generation job: {response.status_code}")
        print(f"   Response: {response.text}")
        return results

    results['gemini_configured'] = True

    gen_result = response.json()
    gen_job_id = gen_result['job_id']

    print(f"\n   Job queued: {gen_job_id[:8]}...")

    # Poll generation job
    gen_job = poll_job(gen_job_id, max_wait=120)

    if not gen_job or gen_job.get('status') != 'completed':
        print("\n   ✗ Generation job did not complete successfully")
        return results

    results['posts_generated'] = gen_job.get('successful', 0)

    print(f"\n   Content generated for: {results['posts_generated']} posts")
    print(f"   Failed: {gen_job.get('failed', 0)}")

    # Show sample of generated content
    if gen_job.get('results'):
        first_result = gen_job['results'][0]
        best_content = first_result.get('best_content', {})

        print(f"\n   Sample Generated Content:")
        print(f"   - Quality Score: {best_content.get('quality_score', 0)}/100")
        print(f"   - Character Count: {best_content.get('char_count', 0)}")
        print(f"   - Hashtags: {len(best_content.get('hashtags', []))}")

        content_preview = best_content.get('content', '')[:150]
        print(f"\n   Preview:")
        print(f"   {content_preview}...")

    if results['posts_generated'] == 0:
        print("\n   ⚠️  No content generated. Check Gemini API key and error logs.")
        return results

    # ========================================================================
    # STEP 4: Sync to Notion database
    # ========================================================================
    if not results['notion_configured']:
        print_step(4, "Skipping Notion Sync (Not Configured)")
        print("\n   ⚠️  Notion API not configured")
        print("   Set NOTION_API_TOKEN and NOTION_DATABASE_ID in .env to enable")
        print("   See .env.example for instructions")
        return results

    print_step(4, "Syncing Posts to Notion Database")
    print(f"   Posts to sync: {len(results['post_ids'])}")
    print("   Update existing: No (duplicate detection enabled)")

    response = requests.post(
        f"{BASE_URL}/api/notion/sync",
        json={
            "post_ids": results['post_ids'],
            "update_existing": False
        }
    )

    if response.status_code != 200:
        print(f"\n   ✗ Failed to start sync job: {response.status_code}")
        print(f"   Response: {response.text}")
        return results

    sync_result = response.json()
    sync_job_id = sync_result['job_id']

    print(f"\n   Job queued: {sync_job_id[:8]}...")

    # Poll sync job
    sync_job = poll_job(sync_job_id, max_wait=60)

    if not sync_job or sync_job.get('status') != 'completed':
        print("\n   ✗ Sync job did not complete successfully")
        return results

    results['posts_synced'] = sync_job.get('created', 0)

    print(f"\n   Notion Sync Results:")
    print(f"   - Created: {sync_job.get('created', 0)}")
    print(f"   - Updated: {sync_job.get('updated', 0)}")
    print(f"   - Duplicates: {sync_job.get('duplicates', 0)}")
    print(f"   - Failed: {sync_job.get('failed', 0)}")

    # Show Notion page URLs if available
    sync_results = sync_job.get('results', {})
    created_pages = sync_results.get('created', [])

    if created_pages:
        print(f"\n   Sample Notion Page:")
        page = created_pages[0]
        if page.get('url'):
            print(f"   URL: {page['url']}")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_section("Pipeline Test Complete")

    print("\n   Summary:")
    print(f"   ✓ Reddit posts fetched: {results['posts_fetched']}")

    if results['gemini_configured']:
        print(f"   ✓ LinkedIn content generated: {results['posts_generated']}")
    else:
        print(f"   ✗ Content generation: Gemini not configured")

    if results['notion_configured']:
        print(f"   ✓ Posts synced to Notion: {results['posts_synced']}")
    else:
        print(f"   ✗ Notion sync: Not configured")

    print("\n   Next Steps:")

    if not results['gemini_configured']:
        print("   1. Configure Gemini API key in .env")
        print("      Get key from: https://makersuite.google.com/app/apikey")

    if not results['notion_configured']:
        print("   2. Configure Notion API in .env")
        print("      Get credentials from: https://www.notion.so/my-integrations")

    if results['gemini_configured'] and results['notion_configured']:
        print("   ✓ All integrations configured!")
        print("   - Review generated content in posts")
        print("   - Check Notion database for synced pages")
        print("   - Customize templates in data/templates/")
        print("   - Add more categories in data/categories/")

    print("\n" + "=" * 70)

    return results


def test_with_existing_posts():
    """Test generation and sync with existing posts"""
    print_section("Testing with Existing Posts")

    print_step(1, "Fetching Existing Posts")

    response = requests.get(f"{BASE_URL}/api/posts?category=railway&limit=3")

    if response.status_code != 200:
        print(f"   ✗ Failed to fetch posts: {response.status_code}")
        return

    posts = response.json()

    if not posts:
        print("   ⚠️  No existing posts found")
        print("   Run test_complete_pipeline() first to fetch posts from Reddit")
        return

    print(f"   Found {len(posts)} existing posts")

    post_ids = [post['id'] for post in posts]

    # Test generation
    print_step(2, "Testing Content Generation")

    response = requests.post(
        f"{BASE_URL}/api/posts/generate",
        json={
            "post_ids": post_ids[:2],  # Test with 2 posts
            "variations": 1
        }
    )

    if response.status_code == 503:
        print("   ✗ Gemini API not configured")
        return
    elif response.status_code != 200:
        print(f"   ✗ Failed: {response.status_code}")
        return

    result = response.json()
    job = poll_job(result['job_id'])

    if job and job.get('status') == 'completed':
        print(f"   ✓ Generated content for {job.get('successful', 0)} posts")

    # Test Notion sync
    print_step(3, "Testing Notion Sync")

    response = requests.post(
        f"{BASE_URL}/api/notion/sync",
        json={
            "post_ids": post_ids[:2],
            "update_existing": False
        }
    )

    if response.status_code == 503:
        print("   ✗ Notion API not configured")
        return
    elif response.status_code != 200:
        print(f"   ✗ Failed: {response.status_code}")
        return

    result = response.json()
    job = poll_job(result['job_id'])

    if job and job.get('status') == 'completed':
        print(f"   ✓ Synced {job.get('created', 0)} new posts")
        print(f"   ℹ️  Skipped {job.get('duplicates', 0)} duplicates")


if __name__ == "__main__":
    try:
        # Run complete pipeline test
        results = test_complete_pipeline()

        # Optionally test with existing posts
        # Uncomment to test generation/sync with existing data:
        # print("\n\n")
        # test_with_existing_posts()

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   cd backend && python -m app.main")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
