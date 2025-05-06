import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import matplotlib.cm as cm
from collections import Counter
import re
import matplotlib.dates as mdates

def create_wordcloud(df, sentiment_category=None):
    """
    Create a word cloud from the text of posts, optionally filtered by sentiment category.
    
    Args:
        df: DataFrame containing the posts
        sentiment_category: Optional filter by sentiment category ('Positive', 'Negative', 'Neutral')
    
    Returns:
        A matplotlib figure containing the word cloud
    """
    # Filter by sentiment category if specified
    if sentiment_category:
        text_data = ' '.join(df[df['category'] == sentiment_category]['cleaned_text'])
    else:
        text_data = ' '.join(df['cleaned_text'])
    
    # If no text data, return None
    if not text_data:
        return None
    
    # Create word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100,
        contour_width=3,
        contour_color='steelblue'
    ).generate(text_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    
    # Set title
    if sentiment_category:
        ax.set_title(f"Word Cloud for {sentiment_category} Posts", fontsize=16)
    else:
        ax.set_title("Word Cloud for All Posts", fontsize=16)
    
    return fig

def sentiment_over_time(df):
    """
    Create a plot showing sentiment over time.
    
    Args:
        df: DataFrame containing the posts with 'created_at' and 'score' columns
    
    Returns:
        A matplotlib figure showing sentiment over time
    """
    # Check if we have timestamp data
    if 'created_at' not in df.columns or df['created_at'].isna().all():
        return None
    
    # Convert created_at to datetime
    df['datetime'] = pd.to_datetime(df['created_at'])
    
    # Sort by datetime
    df = df.sort_values('datetime')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot scatter with colormap based on sentiment score
    scatter = ax.scatter(
        df['datetime'], 
        df['score'],
        c=df['score'], 
        cmap=cm.coolwarm,
        alpha=0.7,
        s=100
    )
    
    # Add best fit line
    z = np.polyfit(range(len(df)), df['score'], 1)
    p = np.poly1d(z)
    ax.plot(df['datetime'], p(range(len(df))), "r--", alpha=0.8, linewidth=2)
    
    # Add horizontal line at zero
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Sentiment Score')
    
    # Set labels and title
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Sentiment Score', fontsize=12)
    ax.set_title('Sentiment Score Over Time', fontsize=16)

    # Format x-axis to show both date and time
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y %H:%M'))
    fig.autofmt_xdate()

    # Tight layout
    plt.tight_layout()
    
    return fig

def common_terms_by_sentiment(df):
    """
    Create a bar chart showing the most common terms for each sentiment category.
    
    Args:
        df: DataFrame containing the posts
    
    Returns:
        A matplotlib figure showing common terms by sentiment
    """
    # Function to extract words from text
    def extract_words(text):
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return [word for word in words if word not in stopwords]
    
    # Simple stopwords list (can be expanded)
    stopwords = {'the', 'and', 'this', 'that', 'for', 'you', 'but', 'not', 'with', 'are', 'have',
                'from', 'they', 'will', 'has', 'can', 'was', 'were', 'what', 'when', 'who', 'how',
                'all', 'their', 'there', 'been', 'would', 'could', 'should', 'your', 'his', 'her',
                'our', 'just', 'more', 'some', 'like', 'very', 'much', 'then', 'than', 'also'}
    
    # Get most common words for each sentiment category
    categories = ['Positive', 'Neutral', 'Negative']
    common_words = {}
    
    for category in categories:
        if category not in df['category'].values:
            continue
            
        # Extract words from all posts in this category
        words = []
        for text in df[df['category'] == category]['cleaned_text']:
            words.extend(extract_words(text))
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Get top 10 words
        common_words[category] = word_counts.most_common(10)
    
    # Create plot
    fig, axes = plt.subplots(1, len(common_words), figsize=(15, 5))
    
    # Adjust for the case of only one category
    if len(common_words) == 1:
        axes = [axes]
    
    # Color map for categories
    colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
    
    # Plot for each category
    for i, (category, words) in enumerate(common_words.items()):
        if not words:  # Skip if no words
            continue
            
        # Unzip words and counts
        labels, values = zip(*words)
        
        # Create horizontal bar chart
        axes[i].barh(labels, values, color=colors[category])
        axes[i].set_title(f"Common Words in {category} Posts")
        axes[i].set_xlabel('Count')
        
        # Invert y-axis to have most common word at the top
        axes[i].invert_yaxis()
    
    plt.tight_layout()
    return fig

def sentiment_magnitude_scatter(df):
    """
    Create a scatter plot of sentiment score vs. magnitude.
    
    Args:
        df: DataFrame containing the posts with 'score' and 'magnitude' columns
    
    Returns:
        A matplotlib figure showing sentiment score vs. magnitude
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define colors for each category
    category_colors = {
        'Positive': 'green',
        'Neutral': 'gray',
        'Negative': 'red'
    }
    
    # Plot scatter points with colors based on category
    for category, color in category_colors.items():
        category_df = df[df['category'] == category]
        if not category_df.empty:
            ax.scatter(
                category_df['score'], 
                category_df['magnitude'],
                color=color,
                alpha=0.7,
                label=category,
                s=100
            )
    
    # Add vertical lines at sentiment thresholds
    ax.axvline(x=-0.25, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0.25, color='gray', linestyle='--', alpha=0.5)
    
    # Add region labels
    ax.text(-0.9, ax.get_ylim()[1]*0.9, "Negative", fontsize=12, color='red')
    ax.text(0, ax.get_ylim()[1]*0.9, "Neutral", fontsize=12, color='gray')
    ax.text(0.6, ax.get_ylim()[1]*0.9, "Positive", fontsize=12, color='green')
    
    # Set labels and title
    ax.set_xlabel('Sentiment Score', fontsize=12)
    ax.set_ylabel('Magnitude', fontsize=12)
    ax.set_title('Sentiment Score vs. Magnitude', fontsize=16)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Set limits
    ax.set_xlim(-1.1, 1.1)
    
    return fig 