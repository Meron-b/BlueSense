# BlueSense - Bluesky Sentiment Analysis

A Streamlit application for analyzing sentiment in Bluesky posts.

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials:
   ```
   BSKY_USERNAME=your_username
   BSKY_PASSWORD=your_password
   ```
4. Run the app:
   ```bash
   streamlit run BlueSense/app.py
   ```

## Deployment to Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file path (`BlueSense/app.py`)
6. Add your secrets in the Streamlit Cloud dashboard:
   - `BSKY_USERNAME`: Your Bluesky username
   - `BSKY_PASSWORD`: Your Bluesky password
   - `GOOGLE_CREDENTIALS`: Your Google Cloud credentials JSON (if using sentiment analysis)

## Features

- Search Bluesky posts
- Analyze sentiment using Google Cloud Natural Language API
- Visualize sentiment trends
- Filter and analyze post content

## Requirements

- Python 3.8+
- Streamlit
- Bluesky account (for authenticated access)
- Google Cloud account (for sentiment analysis)

## Note

For class assignment purposes, the app can run in unauthenticated mode with limited API access. For full functionality, proper credentials need to be set up in the deployment environment.
