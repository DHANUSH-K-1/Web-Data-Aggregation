# 📊 Web Data Aggregation & Insight Generator

## 📖 Introduction

**Web Data Aggregation & Insight Generator** is a powerful, end-to-end data pipeline solution designed to automate the extraction, processing, and visualization of web data. 

Unlike simple scraping scripts, this application provides a **full-stack approach** to web intelligence:
1.  **Orchestration**: A GUI-based control center to manage data collection jobs.
2.  **ETL Pipeline**: diverse scrapers (for Books, Quotes, Jobs) feeding into a robust cleaning and deduplication layer.
3.  **Persistence**: High-performance SQLite storage with upsert capabilities.
4.  **Analytics**: Built-in Pandas-driven statistical analysis and interactive Plotly visualizations.

Whether you are looking to track book prices, analyze quote sentiment, or aggregate job listings, this tool provides the scaffold to turn raw HTML into actionable business insights.

---

## 🚀 Key Features

-   **🕷️ Robust Multi-Source Scraping**:
    -   Integrated `requests` with retry logic and user-agent rotation.
    -   Specialized parsers for different data structures (e-commerce, text aggregators, listings).
-   **🧹 Intelligent Data Cleaning**:
    -   Automated text normalization and whitespace handling.
    -   Currency conversion and numerical extraction logic.
-   **💾 Smart Storage**:
    -   SQLite database backend for lightweight yet reliable persistence.
    -   Duplicate detection to ensure data integrity over multiple runs.
-   **📈 Interactive Dashboards**:
    -   Dynamic charts (bar, histograms, box plots) powered by Streamlit and Plotly.
    -   Real-time metrics (averages, counts, distributions).

---

## 📂 Project Structure

Here is a high-level overview of the codebase architecture:

```
├── 📁 analysis/            # Analytics & Visualization Layer
│   ├── analyze.py          # Pandas statistical functions & logic
│   └── visualize.py        # Plotly/Matplotlib charting functions
├── 📁 scraper/             # Data Collection Layer
│   ├── fetcher.py          # HTTP networking logic (Retries, Headers)
│   ├── parser.py           # BeautifulSoup parsing logic
│   └── cleaner.py          # Data normalization & transformation
├── 📁 storage/             # Persistence Layer
│   └── database.py         # SQLite connection & CRUD operations
├── 📄 main.py              # Application Entry Point (Streamlit UI)
├── 📄 data_pipeline.db     # SQLite Database File
└── 📄 requirements.txt     # Python Dependencies
```

---

## 🛠️ Getting Started

Follow these steps to get the application running on your local machine.

### Prerequisites
- Python 3.8 or higher installed.

### Installation

1.  **Clone the repository**
    ```bash
    git clone git@github.com:DHANUSH-K-1/Web-Data-Aggregation.git
    cd Web-Data-Aggregation
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Launch the Application**
    ```bash
    streamlit run main.py
    ```

2.  **Navigate the Interface**:
    -   **🚀 Orchestration**: Go here first. Select a data source (e.g., "Books") and click **"Run Pipeline"** to fetch data.
        *   **Books Default**: `http://books.toscrape.com`
        *   **Quotes Default**: `http://quotes.toscrape.com`
        *   **Jobs Default**: `https://realpython.github.io/fake-jobs/`
    -   **💾 Data Explorer**: View raw data in a table format and download as CSV.
    -   **📈 Insights**: See interactive analytics like "Average Price by Rating" or "Top Authors".

---

## 🧠 Workflow Explanation

This application follows a classical **ETL (Extract, Transform, Load)** pattern, wrapped in a reactive UI:

1.  **User Action**: User triggers a job from the `Orchestration` tab.
2.  **Extract (`scraper/fetcher.py`)**: The app sends HTTP requests to the target URL.
3.  **Transform (`scraper/parser.py` & `cleaner.py`)**: HTML is parsed into dictionaries, and raw strings are converted to proper types (floats, integers).
4.  **Load (`storage/database.py`)**: Cleaned data is saved to `data_pipeline.db`.
5.  **Visualize (`analysis/`)**: When the user switches tabs, the app queries the DB and renders fresh charts on the fly.