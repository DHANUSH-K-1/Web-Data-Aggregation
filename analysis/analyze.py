import pandas as pd
import plotly.express as px

def get_avg_price_by_rating(books_df):
    """
    Returns a DataFrame with average price per rating.
    """
    if books_df.empty:
        return pd.DataFrame()
    
    return books_df.groupby('rating')['price'].mean().reset_index().sort_values('price', ascending=False)

def get_top_5_expensive_books(books_df):
    """
    Returns the top 5 highest priced items.
    """
    if books_df.empty:
        return pd.DataFrame()
        
    return books_df.sort_values('price', ascending=False).head(5)[['title', 'price', 'rating']]

def get_author_counts(quotes_df):
    """
    Returns the count of quotes per author.
    """
    if quotes_df.empty:
        return pd.DataFrame()
        
    return quotes_df['author'].value_counts().reset_index(name='count').rename(columns={'index': 'author'})

def analyze_prices(books_df):
    """
    Generates a histogram of book prices.
    Returns: Plotly Figure
    """
    if books_df.empty:
        return None
        
    fig = px.histogram(books_df, x="price", nbins=20, title="Price Frequency Coaster (GBP)")
    return fig

def analyze_authors(quotes_df):
    """
    Generates a bar chart of top authors.
    Returns: Plotly Figure
    """
    if quotes_df.empty:
        return None
        
    top_authors = get_author_counts(quotes_df).head(10)
    fig = px.bar(top_authors, x='count', y='author', orientation='h', title="Most Quoted Authors")
    return fig

def analyze_ratings_vs_price(books_df):
    """
    Generates scatter plot for rating vs price.
    Returns: Plotly Figure
    """
    if books_df.empty:
        return None
        
    # Ensure numeric
    df = books_df.copy()
    df['rating_num'] = pd.to_numeric(df['rating'], errors='coerce')
    
    fig = px.scatter(df, x="price", y="rating_num", title="Do expensive books have better ratings?",
                     labels={"rating_num": "Star Rating (1-5)", "price": "Price (£)"})
    return fig
