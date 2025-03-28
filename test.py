import tweepy
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API Credentials
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Set Up Twitter API Client
client = tweepy.Client(bearer_token=X_BEARER_TOKEN)

# User ID of the target Twitter account
user_id = "741042373929508864"  # Replace with the correct User ID

# Define delay to avoid hitting rate limits (15 min = 900 seconds)
DELAY_SECONDS = 900  # Wait for 15 minutes if rate limit is hit

# Function to fetch tweets with rate limit handling
def fetch_tweets_with_delay(user_id):
    while True:
        try:
            # Fetch latest tweets
            response = client.get_users_tweets(id=user_id, max_results=5, tweet_fields=["text"])
            
            # Check if any tweets were returned
            if response.data:
                print(f"✅ Successfully fetched tweets for User ID: {user_id}")
                for tweet in response.data:
                    print(f"📢 Tweet: {tweet.text}")
                break
            else:
                print(f"❗️ No tweets found for User ID: {user_id}")
                break

        # Handle rate limit errors
        except tweepy.errors.TooManyRequests as e:
            print(f"❌ Rate limit exceeded. Waiting for {DELAY_SECONDS // 60} minutes before retrying...")
            time.sleep(DELAY_SECONDS)
        
        # Handle invalid token or authentication issues
        except tweepy.errors.Unauthorized:
            print("❌ Unauthorized. Check your Bearer Token and ensure it's valid.")
            break
        
        # Catch any other errors
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            break

# Fetch tweets with delay and error handling
fetch_tweets_with_delay(user_id)
