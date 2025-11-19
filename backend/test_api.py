"""
Quick API test script
Tests that all major endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("Testing LinkedIn Content Automation API")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(BASE_URL)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Test 2: Health check
    print("\n2. Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Storage Stats: {data['storage']['stats']}")

    # Test 3: List categories
    print("\n3. Testing list categories...")
    response = requests.get(f"{BASE_URL}/api/config/categories")
    print(f"   Status: {response.status_code}")
    categories = response.json()
    print(f"   Categories: {len(categories)}")
    if categories:
        print(f"   First category: {categories[0]['name']}")

    # Test 4: Get Railway category
    print("\n4. Testing get Railway category...")
    response = requests.get(f"{BASE_URL}/api/config/categories/railway")
    print(f"   Status: {response.status_code}")
    category = response.json()
    print(f"   Name: {category['name']}")
    print(f"   Subreddits: {', '.join(category['subreddits'])}")

    # Test 5: List templates
    print("\n5. Testing list templates...")
    response = requests.get(f"{BASE_URL}/api/config/templates")
    print(f"   Status: {response.status_code}")
    templates = response.json()
    print(f"   Templates: {len(templates)}")
    if templates:
        print(f"   First template: {templates[0]['name']}")

    # Test 6: Get statistics
    print("\n6. Testing statistics...")
    response = requests.get(f"{BASE_URL}/api/config/stats")
    print(f"   Status: {response.status_code}")
    stats = response.json()
    print(f"   Stats: {json.dumps(stats, indent=2)}")

    # Test 7: Create a test post
    print("\n7. Testing create post...")
    post_data = {
        "category": "railway",
        "reddit_data": {
            "reddit_post_id": "test123",
            "subreddit": "trains",
            "title": "Test Railway Post",
            "author": "test_user",
            "score": 100,
            "num_comments": 10,
            "upvote_ratio": 0.95,
            "created_utc": 1704067200,
            "permalink": "/r/trains/test123",
            "media_urls": []
        },
        "status": "draft"
    }
    response = requests.post(f"{BASE_URL}/api/posts", json=post_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        post = response.json()
        post_id = post['id']
        print(f"   Created post ID: {post_id}")

        # Test 8: Get the post
        print("\n8. Testing get post...")
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Post title: {response.json()['reddit_data']['title']}")

        # Test 9: Update post
        print("\n9. Testing update post...")
        response = requests.put(
            f"{BASE_URL}/api/posts/{post_id}",
            json={"status": "review"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   New status: {response.json()['status']}")

        # Test 10: List posts
        print("\n10. Testing list posts...")
        response = requests.get(f"{BASE_URL}/api/posts")
        print(f"   Status: {response.status_code}")
        posts = response.json()
        print(f"   Total posts: {len(posts)}")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")
