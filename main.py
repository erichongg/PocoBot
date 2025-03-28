import requests
from bs4 import BeautifulSoup
import discord
import asyncio
from google.cloud import translate_v2 as translate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Google Translate credentials
translate_client = translate.Client.from_service_account_json("google-credentials.json")

# Discord bot setup
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Set up Discord client
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# URL to scrape tweets (via Nitter)
USERNAME = "EricHonng"  # Make sure the username is correct
NITTER_URL = f"https://nitter.net/{USERNAME}"

# Store the last tweet to avoid duplicates
last_tweet_id = None


def get_latest_tweet():
    """Fetch and parse latest tweets from Nitter."""
    global last_tweet_id
    print(f"✅ Checking for new tweets at: {NITTER_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Send request to Nitter with headers
    response = requests.get(NITTER_URL, headers=headers)

    # Print full HTML for inspection
    print(f"🌐 Nitter Response Status: {response.status_code}")
    print(f"🔍 Full HTML Response:\n{response.text[:1000]}...")  # Print first 1000 chars of HTML

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Check if divs are being found
        divs = soup.find_all("div")
        print(f"🔎 Found {len(divs)} div elements.")

        # Print first 5 divs to see structure
        for i, div in enumerate(divs[:5]):
            print(f"➡️ Div {i+1}: {div}")

        # Look for tweet content
        tweet_element = soup.find("div", class_="timeline-item")
        if tweet_element:
            tweet_content = tweet_element.find("div", class_="tweet-content").text.strip()
            tweet_id = tweet_element["data-id"]  # Get tweet ID to prevent duplicates

            # Debugging tweet content
            print(f"📢 New Tweet Found: {tweet_content}")
            print(f"🔎 Tweet ID: {tweet_id}")

            # Return if the tweet is new
            if tweet_id != last_tweet_id:
                last_tweet_id = tweet_id
                return tweet_content
    else:
        print(f"❌ Failed to fetch tweets. Status Code: {response.status_code}")

    return None

# Function to detect and translate tweet to English
def translate_to_english(text):
    """Translate the text to English using Google Cloud Translation."""
    try:
        result = translate_client.translate(text, target_language="en")
        translated_text = result["translatedText"]
        print(f"🌐 Translated Text: {translated_text}")  # Debug Line
        return translated_text
    except Exception as e:
        print(f"❌ Error during translation: {e}")
        return text  # Return original text if translation fails


# Discord event to start the bot
@bot.event
async def on_ready():
    """Event that triggers when the bot is ready."""
    print(f"✅ Logged in as {bot.user.name}")
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    # Send a test message when the bot is ready
    await channel.send("NI LE LA MA")

    while True:
        tweet = get_latest_tweet()
        if tweet:
            # Detect language before translating
            detected_lang = translate_client.detect_language(tweet)["language"]
            print(f"🔎 Detected Language: {detected_lang}")  # Debug Line

            if detected_lang == "ja":
                translated_tweet = translate_to_english(tweet)
                await channel.send(f"📢 **New Translated Tweet:**\n{translated_tweet}")
            else:
                await channel.send(f"📢 **New Tweet:**\n{tweet}")
        
        # Check for new tweets every 5 minutes (for testing)
        print("⏰ Waiting 60 seconds before checking for new tweets...")  # Debug Line
        await asyncio.sleep(60)  # Change to 3600 for 1-hour delay in production


# Run the bot
try:
    bot.run(DISCORD_BOT_TOKEN)
except Exception as e:
    print(f"❌ Error starting Discord bot: {e}")
