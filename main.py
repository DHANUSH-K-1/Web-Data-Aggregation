import streamlit as st
import pandas as pd
import plotly.express as px
from storage.database import init_db, save_data, load_data, clear_data, query_data, DB_NAME
from scraper.parser import parse_books, parse_quotes, parse_jobs
from scraper.cleaner import clean_books_df, clean_quotes_df, clean_jobs_df
from analysis.analyze import (
    analyze_prices, analyze_authors, analyze_ratings_vs_price,
    get_avg_price_by_rating, get_top_5_expensive_books, get_author_counts
)
from analysis.visualize import plot_price_distribution, plot_top_authors

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Web Data Insight Generator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME CONSTANTS ---
THEME_DARK = {
    "bg_color": "#0f172a",         # Deep Slate
    "sidebar_bg": "#1e293b",       # Lighter Slate
    "card_bg": "rgba(30, 41, 59, 0.7)", # Glassy Slate
    "text_color": "#f8fafc",       # Slate 50
    "subtext_color": "#94a3b8",    # Slate 400
    "accent": "#3b82f6",           # Blue 500
    "success": "#10b981",          # Emerald 500
    "warning": "#f59e0b",          # Amber 500
    "error": "#ef4444",            # Red 500
    "border": "rgba(148, 163, 184, 0.1)"
}

THEME_LIGHT = {
    "bg_color": "#f8fafc",         # Slate 50
    "sidebar_bg": "#ffffff",       # White
    "card_bg": "rgba(255, 255, 255, 0.8)", # Glassy White
    "text_color": "#1e293b",       # Slate 800
    "subtext_color": "#64748b",    # Slate 500
    "accent": "#2563eb",           # Blue 600
    "success": "#059669",          # Emerald 600
    "warning": "#d97706",          # Amber 600
    "error": "#dc2626",            # Red 600
    "border": "rgba(148, 163, 184, 0.2)"
}

# --- CUSTOM CSS ---
def get_custom_css(theme_name):
    t = THEME_DARK if theme_name == "Dark" else THEME_LIGHT
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font_family: 'Inter', sans-serif;
            color: {t["text_color"]};
        }}
        
        .stApp {{
            background-color: {t["bg_color"]};
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: {t["sidebar_bg"]};
            border-right: 1px solid {t["border"]};
        }}
        
        /* Glassmorphism Cards */
        div[data-testid="stMetric"], .css-1r6slb0, .stDataFrame {{
            background-color: {t["card_bg"]};
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid {t["border"]};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        /* Buttons */
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            height: 2.75rem;
            background-color: {t["accent"]}; 
            color: white;
            border: none;
            font-weight: 600;
            letter-spacing: 0.025em;
            transition: all 0.2s;
        }}
        
        .stButton>button:hover {{
            opacity: 0.9;
            transform: scale(1.01);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }}
        
        .stButton>button:active {{
            transform: scale(0.98);
        }}
        
        /* Secondary Button (Clear Data) */
        button[kind="secondary"] {{
            background-color: transparent !important;
            border: 1px solid {t["error"]} !important;
            color: {t["error"]} !important;
        }}
        
        button[kind="secondary"]:hover {{
            background-color: {t["error"]}15 !important; 
        }}

        /* Typography */
        h1, h2, h3 {{
            color: {t["text_color"]} !important;
            font-weight: 700;
        }}
        
        p, label {{
            color: {t["subtext_color"]};
        }}
        
        /* Inputs */
        .stTextInput>div>div>input, .stSelectbox>div>div>div {{
            background-color: {t["card_bg"]};
            color: {t["text_color"]};
            border-radius: 8px;
            border: 1px solid {t["border"]};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 20px;
            background-color: transparent;
            padding-bottom: 5px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            border: none;
            color: {t["subtext_color"]};
            font-weight: 600;
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {t["accent"]};
            border-bottom: 2px solid {t["accent"]};
        }}

    </style>
    """

# --- INITIALIZATION ---
init_db()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🔮 Data Insights")
    
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio("Theme Mode", ["Dark", "Light"], horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🛠️ Pipeline Status")
    st.info("System Ready\n\n1. Fetch\n2. Parse\n3. Clean\n4. Store\n5. Analyze")
    
    st.markdown("### 🗑️ Zone")
    if st.button("Clear Database", type="secondary"):
        clear_data("scraped_books")
        clear_data("scraped_quotes")
        clear_data("scraped_jobs")
        st.toast("Database cleared successfully!", icon="🗑️")
        st.rerun()

# --- APPLY CSS ---
st.markdown(get_custom_css(theme_choice), unsafe_allow_html=True)
t_code = THEME_DARK if theme_choice == "Dark" else THEME_LIGHT

# --- MAIN HEADER ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("Web Data Aggregation & Insight Generator")
    st.markdown(f"<span style='color:{t_code['subtext_color']}'>Automated pipeline for cleaning, storing, and analyzing unstructured web data.</span>", unsafe_allow_html=True)
with col_head2:
    st.metric("Active DB", DB_NAME, delta="Connected", delta_color="normal")

# --- TABS ---
tabs = st.tabs(["🏠 Home", "🚀 Orchestration", "💾 Data Explorer", "🔎 Search", "📈 Analytics", "🖼️ Reports"])

# --- TAB 1: HOME ---
with tabs[0]:
    st.markdown("### System Architecture")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background:{t_code['card_bg']}; padding:20px; border-radius:12px; border:1px solid {t_code['border']};">
            <h4 style="margin-top:0;">Core Capabilities</h4>
            <p>Our autonomous scraper engine handles the complete data lifecycle:</p>
            <ul>
                <li><strong>Fetch:</strong> Resilient HTTP requests with automatic retries and user-agent rotation.</li>
                <li><strong>Parse:</strong> Intelligent HTML parsing to extract structured content.</li>
                <li><strong>Clean:</strong> Data normalization, currency conversion, and text sanitization.</li>
                <li><strong>Store:</strong> ACID-compliant local storage with deduplication.</li>
                <li><strong>Analyze:</strong> Real-time pandas-based analytics and Plotly visualizations.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=250)
        st.success(f"Running on Streamlit v{st.__version__}")

# --- TAB 2: ORCHESTRATION ---
with tabs[1]:
    st.header("Pipeline Orchestration")
    st.markdown("Configure and execute data ingestion jobs.")
    
    col_ctrl, col_log = st.columns([1, 2])
    
    with col_ctrl:
        st.subheader("Configuration")
        source_type = st.selectbox("Data Source", ["Books", "Quotes", "Jobs"])
        
        if source_type == "Books":
            target_url = st.text_input("Target URL Template", "http://books.toscrape.com/catalogue/page-{}.html")
            st.caption("Use `{}` as a placeholder for pagination.")
        elif source_type == "Quotes":
            target_url = st.text_input("Target URL Template", "http://quotes.toscrape.com/page/{}/")
            st.caption("Use `{}` as a placeholder for pagination.")
        else: # Jobs
            target_url = st.text_input("Target URL", "https://realpython.github.io/fake-jobs/")
            st.caption("Single page scrape.")
            
        limit_items = st.number_input("Max Items Limit", min_value=10, max_value=500, value=20, step=10)
        
        run_btn = st.button("▶️ Start Extraction", type="primary")

    with col_log:
        st.subheader("Execution Log")
        log_container = st.container()
        
        if run_btn:
            with st.status("Initializing Pipeline...", expanded=True) as status:
                st.write(f"🚀 **Starting Job:** {source_type} Scraper")
                st.write(f"🔗 **Target:** `{target_url}`")
                
                try:
                    if source_type == "Books":
                        st.write("📥 Fetching raw HTML...")
                        raw_books = parse_books(limit=limit_items, base_url=target_url)
                        
                        st.write(f"🧩 Parsed {len(raw_books)} items. Cleaning data...")
                        clean_books = clean_books_df(raw_books)
                        
                        st.write("💾 Upserting to database...")
                        save_data(clean_books, "scraped_books")
                        st.session_state['active_dataset'] = "Books"
                        
                    elif source_type == "Quotes":
                        st.write("📥 Fetching raw HTML...")
                        raw_quotes = parse_quotes(limit=limit_items, base_url=target_url)
                        
                        st.write(f"🧩 Parsed {len(raw_quotes)} items. Cleaning data...")
                        clean_quotes = clean_quotes_df(raw_quotes)
                        
                        st.write("💾 Upserting to database...")
                        save_data(clean_quotes, "scraped_quotes")
                        st.session_state['active_dataset'] = "Quotes"

                    elif source_type == "Jobs":
                        st.write("📥 Fetching raw HTML...")
                        raw_jobs = parse_jobs(limit=limit_items, base_url=target_url)
                        
                        st.write(f"🧩 Parsed {len(raw_jobs)} items. Cleaning data...")
                        clean_jobs = clean_jobs_df(raw_jobs)
                        
                        st.write("💾 Upserting to database...")
                        save_data(clean_jobs, "scraped_jobs")
                        st.session_state['active_dataset'] = "Jobs"
                    
                    status.update(label="Pipeline Completed Successfully", state="complete", expanded=False)
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Pipeline Failed: {str(e)}")
                    status.update(label="Pipeline Failed", state="error")

# --- TAB 3: DATA EXPLORER ---
with tabs[2]:
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.header("Data Explorer")
    with col_d2:
        st.write("") # Spacer
        
    # Selector
    options = ["Books", "Quotes", "Jobs"]
    default_idx = options.index(st.session_state.get('active_dataset', "Books")) if st.session_state.get('active_dataset') in options else 0
    dataset = st.selectbox("Select Collection", options, index=default_idx)
    
    # Load Data
    if dataset == "Books":
        df = load_data("scraped_books")
        config = {
            "price": st.column_config.NumberColumn("Price (£)", format="£%.2f"),
            "rating": st.column_config.NumberColumn("Rating", format="%d ⭐"),
            "url": st.column_config.LinkColumn("Product Link")
        }
    elif dataset == "Quotes":
        df = load_data("scraped_quotes")
        config = {
            "tags": st.column_config.ListColumn("Tags")
        }
    else: # Jobs
        df = load_data("scraped_jobs")
        config = {
            "apply_link": st.column_config.LinkColumn("Apply Here")
        }

    if not df.empty:
        st.dataframe(
            df, 
            use_container_width=True, 
            column_config=config,
            hide_index=True
        )
        
        st.download_button(
            "📥 Export to CSV", 
            df.to_csv(index=False).encode('utf-8'),
            f"{dataset.lower()}_data.csv",
            "text/csv"
        )
    else:
        st.info(f"No data found for {dataset}. Run the orchestration pipeline first.")

# --- TAB 4: SEARCH ---
with tabs[3]:
    st.header("Global Search")
    st.markdown("Perform low-latency queries directly against the database logic.")
    
    search_dataset = st.radio("Target Collection", ["Books", "Quotes", "Jobs"], horizontal=True)
    st.divider()
    
    mongo_query = {}
    
    if search_dataset == "Books":
        c1, c2 = st.columns(2)
        with c1:
            title_q = st.text_input("Book Title", placeholder="e.g. Star Wars")
        with c2:
            price_range = st.slider("Price Range (£)", 0, 100, (0, 100))
            
        if title_q: mongo_query["title"] = {"$regex": title_q, "$options": "i"}
        if price_range != (0, 100): mongo_query["price"] = {"$gte": price_range[0], "$lte": price_range[1]}

    elif search_dataset == "Quotes":
        c1, c2 = st.columns(2)
        with c1:
            author_q = st.text_input("Author Name", placeholder="e.g. Einstein")
        with c2:
            tag_q = st.text_input("Tag", placeholder="e.g. love")
            
        if author_q: mongo_query["author"] = {"$regex": author_q, "$options": "i"}
        if tag_q: mongo_query["tags"] = tag_q

    else: # Jobs
        c1, c2 = st.columns(2)
        with c1:
            job_q = st.text_input("Role Title", placeholder="e.g. Developer")
        with c2:
            company_q = st.text_input("Company", placeholder="e.g. Google")
            
        if job_q: mongo_query["title"] = {"$regex": job_q, "$options": "i"}
        if company_q: mongo_query["company"] = {"$regex": company_q, "$options": "i"}

    if st.button("Run Search Query", type="primary"):
        coll_map = {"Books": "scraped_books", "Quotes": "scraped_quotes", "Jobs": "scraped_jobs"}
        
        with st.spinner("Searching..."):
            res = query_data(coll_map[search_dataset], mongo_query, limit=50)
            
        if not res.empty:
            st.success(f"Found {len(res)} results")
            st.dataframe(res, use_container_width=True)
        else:
            st.warning("No matches found matching your criteria.")

# --- TAB 5: ANALYTICS ---
with tabs[4]:
    st.header("Analytics Dashboard")
    
    insight_ds = st.selectbox("Analyze Dataset", ["Books", "Quotes"], key="analytics_select")
    
    if insight_ds == "Books":
        df_books = load_data("scraped_books")
        if not df_books.empty and 'price' in df_books.columns:
            # KPIS
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Inventory", len(df_books))
            k2.metric("Average Price", f"£{df_books['price'].mean():.2f}")
            k3.metric("Catalog Variety", f"{df_books['title'].nunique()} Titles")
            
            st.markdown("### 📊 Price Landscape")
            # Interactive Plotly Chart
            fig = px.histogram(
                df_books, 
                x="price", 
                nbins=20, 
                title="Price Distribution",
                color_discrete_sequence=[t_code['accent']],
                template="plotly_dark" if theme_choice=="Dark" else "plotly_white"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Top 5 Most Expensive")
                st.table(get_top_5_expensive_books(df_books))
            with c2:
                st.markdown("#### Price by Rating")
                avg_r = get_avg_price_by_rating(df_books)
                st.bar_chart(avg_r.set_index('rating'), color=t_code['accent'])
        else:
            st.warning("No book analytics available. Please run the pipeline.")

    else: # Quotes
        df_quotes = load_data("scraped_quotes")
        if not df_quotes.empty:
            k1, k2 = st.columns(2)
            k1.metric("Total Quotes", len(df_quotes))
            k2.metric("Unique Authors", df_quotes['author'].nunique())
            
            st.markdown("### 🗣️ Author Dominance")
            author_counts = get_author_counts(df_quotes)
            st.bar_chart(author_counts.set_index('author').head(10), color=t_code['accent'])
        else:
            st.warning("No quote analytics available. Please run the pipeline.")

# --- TAB 6: REPORTS ---
with tabs[5]:
    st.header("Downloadable Reports")
    st.markdown("Generate and download static image reports for offline use.")
    
    rep_ds = st.selectbox("Source Data", ["Books", "Quotes"], key="rep_select")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        if rep_ds == "Books":
            df = load_data("scraped_books")
            if not df.empty and 'price' in df.columns:
                buf = plot_price_distribution(df)
                if buf:
                    st.image(buf, caption="Price Distribution Histogeam", use_container_width=True)
                    st.download_button("⬇️ Download PNG", buf, "price_dist.png", "image/png")
            else:
                st.warning("No data.")
                
    with col_r2:
        if rep_ds == "Quotes":
            df = load_data("scraped_quotes")
            if not df.empty:
                buf = plot_top_authors(df)
                if buf:
                    st.image(buf, caption="Top Authors Bar Chart", use_container_width=True)
                    st.download_button("⬇️ Download PNG", buf, "author_dist.png", "image/png")
            else:
                st.warning("No data.")
