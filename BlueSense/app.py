import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from dotenv import load_dotenv
from atproto import Client, client_utils
from google.cloud import language_v1
import re
import html  # Add this import at the top if not already present
# Import advanced visualizations
from advanced_visualizations import (
    sentiment_over_time, 
    common_terms_by_sentiment,
    sentiment_magnitude_scatter
)

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="BlueSense - Bluesky Sentiment Analysis",
    page_icon="🔍",
    layout="wide"
)

# Add custom theme styling
st.markdown("""
    <style>
        /* Main background and text colors */
        body, .stApp {
            background-color: #FFFFFF !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #0085FF !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #0085FF;
            color: white;
            border: none;
            border-radius: 4px;
        }
        .stButton>button:hover {
            background-color: #0066CC; /* Darker blue for hover */
            border: none;
            color: white;
        }
        
        /* Input fields */
        .stTextInput>div>div>input {
            border: 1px solid #CCCCCC !important;
            border-radius: 4px;
            box-shadow: none !important;
        }
        .stTextInput>div>div>input:focus {
            border: 1.5px solid #888888 !important;
            box-shadow: none !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #FFFFFF;
            border-bottom: 2px solid #0085FF;
        }
        .stTabs [data-baseweb="tab"] {
            color: #0085FF;
            background-color: #FFFFFF !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #0085FF !important;
            font-weight: bold;
            border-bottom: none !important;
        }
        
        /* Success messages */
        .stSuccess {
            background-color: #F0F8FF;
            border: 1px solid #0085FF;
        }
        
        /* Info messages */
        .stInfo {
            background-color: #F0F8FF;
            border: 1px solid #0085FF;
        }
        
        /* Warning messages */
        .stWarning {
            background-color: #FFF3E8;
            border: 1px solid #FF8C00;
        }
        
        /* Error messages */
        .stError {
            background-color: #FFE8E8;
            border: 1px solid #FF0000;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function definitions
@st.cache_resource
def init_bluesky_client():
    """Initialize and return a Bluesky client."""
    try:
        client = Client()
        # Get credentials from environment variables or Streamlit secrets
        BSKY_USERNAME = st.secrets.get("BSKY_USERNAME", os.getenv("BSKY_USERNAME"))
        BSKY_PASSWORD = st.secrets.get("BSKY_PASSWORD", os.getenv("BSKY_PASSWORD"))
        
        if BSKY_USERNAME and BSKY_PASSWORD:
            client.login(BSKY_USERNAME, BSKY_PASSWORD)
            st.success(f"Successfully logged in to Bluesky as {BSKY_USERNAME}")
        else:
            st.warning("Bluesky credentials not found. Running in unauthenticated mode with API limits.")
        return client
    except Exception as e:
        st.error(f"Failed to initialize Bluesky client: {e}")
        return None

@st.cache_resource
def init_language_client():
    """Initialize and return a Google Cloud Natural Language client."""
    try:
        # Check for Google Cloud credentials in Streamlit secrets
        if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
            if 'GOOGLE_CREDENTIALS' in st.secrets:
                # Create a temporary credentials file
                creds_path = '/tmp/google_credentials.json'
                with open(creds_path, 'w') as f:
                    json.dump(st.secrets['GOOGLE_CREDENTIALS'], f)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        return language_v1.LanguageServiceClient()
    except Exception as e:
        st.error(f"Failed to initialize Google Cloud Natural Language client: {e}")
        return None

def parse_bluesky_post(post):
    """Custom parser for Bluesky posts that handles different content types."""
    try:
        post_data = {
            'text': '',
            'has_video': False,
            'has_starter_pack': False,
            'is_valid': False
        }
        if hasattr(post, 'record') and hasattr(post.record, 'text'):
            post_data['text'] = post.record.text
        if hasattr(post, 'embed'):
            if hasattr(post.embed, 'type'):
                if 'video' in str(post.embed.type):
                    post_data['has_video'] = True
                    return post_data
            if hasattr(post.embed, 'record') and hasattr(post.embed.record, 'embeds'):
                for embed in post.embed.record.embeds:
                    if hasattr(embed, 'type') and 'video' in str(embed.type):
                        post_data['has_video'] = True
                        return post_data
            if (hasattr(post.embed, 'record') and 
                hasattr(post.embed.record, 'type') and 
                'starterPack' in str(post.embed.record.type)):
                post_data['has_starter_pack'] = True
                return post_data
        post_data['is_valid'] = bool(post_data['text'])
        return post_data
    except Exception as e:
        return {'text': '', 'has_video': False, 'has_starter_pack': False, 'is_valid': False}

def search_bluesky(client, query, limit=100):
    """Search Bluesky for posts containing the query."""
    try:
        search_results = client.app.bsky.feed.search_posts({
            "q": query, 
            "limit": 100
        })
        valid_posts = []
        skipped_videos = 0
        skipped_starter_packs = 0
        for post in search_results.posts:
            parsed_post = parse_bluesky_post(post)
            if parsed_post['has_video']:
                skipped_videos += 1
                continue
            if parsed_post['has_starter_pack']:
                skipped_starter_packs += 1
                continue
            if parsed_post['is_valid']:
                valid_posts.append(post)
            if len(valid_posts) >= limit:
                break
        if not valid_posts:
            st.warning(f"No valid posts found after filtering. Skipped {skipped_videos} posts with videos and {skipped_starter_packs} starter pack views. Try a different search term.")
        else:
            skipped_total = skipped_videos + skipped_starter_packs
            if skipped_total > 0:
                st.info(f"Found {len(valid_posts)} valid posts. Skipped {skipped_videos} posts with videos and {skipped_starter_packs} starter pack views.")
        return valid_posts
    except Exception as e:
        st.error(f"Error searching Bluesky: {e}")
        return []

def analyze_sentiment(text, language_client):
    """Analyze the sentiment of text using Google Cloud Natural Language API."""
    try:
        document = language_v1.Document(
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        sentiment = language_client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment
        return {
            "score": sentiment.score,
            "magnitude": sentiment.magnitude
        }
    except Exception as e:
        # Suppress unsupported language errors
        if "not supported for document_sentiment analysis" in str(e):
            return None
        st.error(f"Error analyzing sentiment: {e}")
        return {"score": 0, "magnitude": 0}

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def categorize_sentiment(score):
    if score > 0.25:
        return "Positive"
    elif score < -0.25:
        return "Negative"
    else:
        return "Neutral"

# App title and description
left, center, right = st.columns([1, 3, 1])
with center:
    st.title("BlueSense 🔍")
    st.markdown("""
        Analyze sentiment of posts on Bluesky related to specific keywords.
        This tool uses Google Cloud Natural Language API to perform sentiment analysis.
    """)

    # Initialize Bluesky client
    bluesky_client = init_bluesky_client()
    language_client = init_language_client()

    # Main app
    if bluesky_client and language_client:
        # Input for keyword search
        keyword = st.text_input("Enter a keyword to analyze sentiment on Bluesky", "")
        
        # Set up a button to trigger the analysis
        if st.button("Analyze Sentiment") and keyword:
            # Display progress information
            with st.spinner(f"Searching for posts containing '{keyword}'..."):
                posts = search_bluesky(bluesky_client, keyword, limit=100)
            
            if posts:
                st.success(f"Found {len(posts)} posts related to '{keyword}'")
                
                # Process posts and analyze sentiment
                with st.spinner("Analyzing sentiment..."):
                    results = []
                    for post in posts:
                        # Extract text content
                        text = post.record.text if hasattr(post, 'record') and hasattr(post.record, 'text') else ""
                        
                        if text:
                            # Clean the text
                            cleaned_text = clean_text(text)
                            
                            # Analyze sentiment
                            sentiment = analyze_sentiment(cleaned_text, language_client)
                            if sentiment is None:
                                continue  # Skip this post
                            
                            # Categorize sentiment
                            category = categorize_sentiment(sentiment["score"])
                            
                            # Add to results
                            results.append({
                                "text": text,
                                "cleaned_text": cleaned_text,
                                "score": sentiment["score"],
                                "magnitude": sentiment["magnitude"],
                                "category": category,
                                "created_at": post.indexed_at if hasattr(post, 'indexed_at') else "",
                                "author": post.author.display_name if hasattr(post, 'author') and hasattr(post.author, 'display_name') else ""
                            })
                    
                    # Convert to DataFrame for easier analysis
                    df = pd.DataFrame(results)
                    
                    # Create tabs for different visualizations
                    tab1, tab2, tab3 = st.tabs([
                        "Overview", 
                        "Temporal Analysis", 
                        "Advanced Analysis"
                    ])
                    
                    # Tab 1: Overview
                    with tab1:
                        # Display sentiment distribution
                        st.subheader("Sentiment Distribution")
                        
                        # Count sentiment categories
                        sentiment_counts = df["category"].value_counts()
                        
                        # Create columns for pie chart and sample posts
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            # Create a pie chart
                            fig, ax = plt.subplots(figsize=(10, 6))
                            colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
                            wedges, texts, autotexts = ax.pie(
                                sentiment_counts, 
                                labels=sentiment_counts.index, 
                                autopct='%1.1f%%',
                                colors=[colors[cat] for cat in sentiment_counts.index]
                            )
                            # Equal aspect ratio ensures that pie is drawn as a circle
                            ax.axis('equal')  
                            plt.setp(autotexts, size=10, weight="bold")
                            st.pyplot(fig)
                        
                        with col2:
                            # Display sentiment score distribution
                            fig, ax = plt.subplots(figsize=(10, 6))
                            ax.hist(df["score"], bins=20, color='skyblue', edgecolor='black')
                            ax.set_xlabel("Sentiment Score (-1 to 1)")
                            ax.set_ylabel("Number of Posts")
                            ax.set_title("Distribution of Sentiment Scores")
                            ax.grid(True, linestyle='--', alpha=0.7)
                            st.pyplot(fig)
                        
                        # Add extra space before sample posts
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        
                        # Display top 5 most positive and negative posts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Most Positive Posts")
                            top_positive = df.nlargest(5, "score")
                            for i, row in top_positive.iterrows():
                                author_html = html.escape(str(row['author'])) if row['author'] else "Unknown"
                                st.markdown(f"""
                                **Score: {row['score']:.2f}**  
                                "{row['text']}"<br>
                                <span style='color: #888;'>by {author_html}</span>
                                """, unsafe_allow_html=True)
                                st.divider()
                        
                        with col2:
                            st.markdown("### Most Negative Posts")
                            top_negative = df.nsmallest(5, "score")
                            for i, row in top_negative.iterrows():
                                author_html = html.escape(str(row['author'])) if row['author'] else "Unknown"
                                st.markdown(f"""
                                **Score: {row['score']:.2f}**  
                                "{row['text']}"<br>
                                <span style='color: #888;'>by {author_html}</span>
                                """, unsafe_allow_html=True)
                                st.divider()
                    
                    # Tab 2: Temporal Analysis
                    with tab2:
                        st.subheader("Sentiment Over Time")
                        
                        # Create sentiment over time chart
                        time_plot = sentiment_over_time(df)
                        if time_plot:
                            st.pyplot(time_plot)
                        else:
                            st.info("Insufficient time data to create a temporal analysis.")
                        
                        # Common terms by sentiment
                        st.subheader("Common Terms by Sentiment")
                        terms_plot = common_terms_by_sentiment(df)
                        if terms_plot:
                            st.pyplot(terms_plot)
                        else:
                            st.info("Not enough text data to extract common terms.")
                    
                    # Tab 3: Advanced Analysis
                    with tab3:
                        st.subheader("Advanced Sentiment Analysis")
                        
                        # Sentiment magnitude scatter plot
                        scatter_plot = sentiment_magnitude_scatter(df)
                        st.pyplot(scatter_plot)
                        
                        # Display explanation of score vs. magnitude
                        with st.expander("Understanding Score vs. Magnitude"):
                            st.markdown("""
                            ### Sentiment Score vs. Magnitude Explained
                            
                            - **Sentiment Score**: Ranges from -1.0 (negative) to 1.0 (positive) and represents the overall emotional leaning of the text.
                            
                            - **Magnitude**: Represents the strength or intensity of emotion (both positive and negative) within the text, regardless of score. 
                              Higher magnitude generally indicates stronger emotional content.
                            
                            #### Key Insights:
                            
                            - **High Score, High Magnitude**: Strong positive emotion (e.g., excitement, joy)
                            - **Low Score, High Magnitude**: Strong negative emotion (e.g., anger, sadness)
                            - **Near-zero Score, Low Magnitude**: Neutral or factual content
                            - **Near-zero Score, High Magnitude**: Mixed emotions or conflicting sentiments
                            """)
                        
                        # Display raw data in an expandable section
                        with st.expander("View all analyzed posts"):
                            st.dataframe(df[["text", "score", "magnitude", "category", "author"]])
            else:
                st.warning(f"No posts found containing '{keyword}'")
    else:
        st.error("Failed to initialize required clients. Please check your configuration.")

    # Instructions for setting up Google Cloud credentials
    with st.expander("Setup Instructions"):
        st.markdown("""
        ### Setting Up Google Cloud Credentials
        
        To use this application, you need to set up Google Cloud credentials:
        
        1. Create a Google Cloud project and enable the Natural Language API
        2. Create a service account and download the JSON key file
        3. Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your JSON key file
        
        ### Setting Up Bluesky Credentials (Optional)
        
        While the app can work without logging in, for better API limits:
        
        1. Create a `.env` file in the project directory
        2. Add your Bluesky credentials:
           ```
           BSKY_USERNAME=your_username
           BSKY_PASSWORD=your_password
           ```
        """)

    # Add GitHub footer
    st.markdown(
        """
        <div style='text-align: left; margin-top: 3em; color: #888; font-size: 1.1em;'>
            More info and ⭐ at
            <a href="https://github.com/coms2132-sp25/final-project-Meron-b" target="_blank" style="color: #0085FF; text-decoration: underline;">
                github.com/coms2132-sp25/final-project-Meron-b
            </a>
        </div>
        """,
        unsafe_allow_html=True
    ) 