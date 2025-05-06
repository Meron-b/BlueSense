## 🔍 BlueSense: BlueSky Sentiment Analysis Platform

A Streamlit application for analyzing sentiment in Bluesky posts.

Try it out yourself! ➡ [bluesense.streamlit.app](https://bluesense.streamlit.app/)

#
BlueSense is an interactive platform that allows users to analyze sentiment around specific topics or keywords on **BlueSky**, an open-source, decentralized social media platform launched in 2023 as an alternative to Twitter/X. On BlueSense users can input topics of interest, and the system retrieves relevant posts to perform sentiment analysis, presenting results through intuitive visualizations.

BlueSense provides a simple yet powerful interface that enables users to:

- **Input Topics**: Enter keywords, hashtags, or phrases through a user-friendly web interface.
- **Data Collection**: Upon input, the system makes targeted API calls to BlueSky to retrieve a sample of posts (100) related to the specified topic.
- **Sentiment Analysis**: Each retrieved post undergoes sentiment analysis using Google Cloud Natural Language API to classify sentiment as positive, negative, or neutral.
- **Results Visualization**: The system provides a comprehensive analysis through multiple interactive tabs:
    - **Overview Tab**:
        - Overall sentiment distribution pie chart showing percentages of positive/negative/neutral posts
        - Sentiment score distribution histogram
        - Top 5 most positive and negative posts with their scores and authors
    - **Temporal Analysis Tab**:
        - Interactive timeline showing sentiment trends over time (day of use)
        - Common terms analysis by sentiment category
    - **Advanced Analysis Tab**:
        - Sentiment score vs. magnitude scatter plot
        - Detailed explanation of sentiment metrics
        - Raw data view of all analyzed posts

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
    - Set up Google Cloud Natural Language API:
     - Create a Google Cloud project
     - Enable the Natural Language API
     - Create a service account and download the JSON key file
     - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your key file:
       ```bash
       export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key-file.json
       ```
4. Run the app:
   ```bash
   streamlit run BlueSense/app.py
   ```

## Requirements

- Python 3.8+
- Streamlit
- Bluesky account (for authenticated access)
- Google Cloud account (for sentiment analysis)
