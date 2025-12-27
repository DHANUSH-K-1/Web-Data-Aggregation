import matplotlib.pyplot as plt
import seaborn as sns
import io

def plot_price_distribution(books_df):
    """
    Generates a static histogram of prices using Matplotlib/Seaborn.
    Returns: BytesIO object identifying the image.
    """
    if books_df.empty:
        return None
    
    plt.figure(figsize=(10, 6))
    sns.histplot(books_df['price'], bins=20, kde=True)
    plt.title('Price Distribution')
    plt.xlabel('Price (£)')
    plt.ylabel('Count')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def plot_top_authors(quotes_df):
    """
    Generates a static bar chart of top authors.
    Returns: BytesIO object identifying the image.
    """
    if quotes_df.empty:
        return None
        
    top_authors = quotes_df['author'].value_counts().head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_authors.values, y=top_authors.index)
    plt.title('Top 10 Authors by Quote Count')
    plt.xlabel('Number of Quotes')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
