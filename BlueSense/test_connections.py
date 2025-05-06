#!/usr/bin/env python3
"""
Test script to check if the Bluesky API and Google Cloud Natural Language API connections are working.
"""
import os
import sys
from dotenv import load_dotenv
from atproto import Client
from google.cloud import language_v1

# Load environment variables first
load_dotenv()

def test_bluesky_auth():
    """Test Bluesky authentication."""
    print("Testing Bluesky authentication...")
    username = os.getenv("BSKY_USERNAME")
    password = os.getenv("BSKY_PASSWORD")
    
    if not username or not password:
        print("⚠️ Bluesky credentials not found in .env file. Skipping authentication test.")
        return None, None
    
    try:
        client = Client()
        client.login(username, password)
        print(f"✅ Bluesky authentication successful for user {username}!")
        return True, client
    except Exception as e:
        print(f"❌ Bluesky authentication failed: {e}")
        return False, None

def test_bluesky_connection(client=None):
    """Test connection to Bluesky API."""
    print("Testing Bluesky API connection...")
    try:
        # Create a new client if one wasn't provided
        if client is None:
            client = Client()
            
        # Test with a simple search
        results = client.app.bsky.feed.search_posts({"q": "test", "limit": 1})
        if results and hasattr(results, 'posts') and len(results.posts) > 0:
            print("✅ Bluesky API connection successful!")
            return True
        else:
            print("❌ Bluesky API connection failed: No results returned.")
            return False
    except Exception as e:
        print(f"❌ Bluesky API connection failed: {e}")
        return False

def test_google_cloud_connection():
    """Test connection to Google Cloud Natural Language API."""
    print("Testing Google Cloud Natural Language API connection...")
    try:
        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(
            content="Hello, world!",
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment
        
        print(f"✅ Google Cloud Natural Language API connection successful!")
        print(f"   Sample sentiment analysis: Score={sentiment.score}, Magnitude={sentiment.magnitude}")
        return True
    except Exception as e:
        print(f"❌ Google Cloud Natural Language API connection failed: {e}")
        print("   Make sure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
        return False

def main():
    """Main function to run all tests."""
    print("=== BlueSense API Connection Tests ===\n")
    
    # Test Bluesky authentication first
    bluesky_auth, authenticated_client = test_bluesky_auth()
    print()
    
    # Test Bluesky API connection with the authenticated client
    if bluesky_auth and authenticated_client:
        bluesky_connection = test_bluesky_connection(authenticated_client)
    else:
        bluesky_connection = test_bluesky_connection()
    print()
    
    # Test Google Cloud Natural Language API connection
    google_cloud_connection = test_google_cloud_connection()
    print()
    
    # Print summary
    print("=== Test Summary ===")
    if bluesky_auth is not None:
        print(f"Bluesky Authentication: {'✅ Passed' if bluesky_auth else '❌ Failed'}")
    else:
        print("Bluesky Authentication: ⚠️ Skipped (No credentials provided)")
    print(f"Bluesky API Connection: {'✅ Passed' if bluesky_connection else '❌ Failed'}")
    print(f"Google Cloud Natural Language API: {'✅ Passed' if google_cloud_connection else '❌ Failed'}")
    
    # Set exit code
    if (bluesky_auth is not None and not bluesky_auth) or not bluesky_connection or not google_cloud_connection:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        return 1
    else:
        print("\n✅ All tests passed! Your environment is correctly set up.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 