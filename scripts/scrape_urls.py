import requests
from bs4 import BeautifulSoup
import sqlite3
import csv
import os

# Connect to (or create) the SQLite database
def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn

# Recreate the table (drop existing if needed)
def recreate_table(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS articles")
    cursor.execute('''CREATE TABLE articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        site TEXT,
                        category TEXT,
                        url TEXT,
                        title TEXT,
                        published_time TEXT,
                        modified_time TEXT,
                        author TEXT,
                        article_text TEXT
                      )''')
    conn.commit()

# Insert extracted data into the database
def insert_article(conn, site, category, url, title, published_time, modified_time, author, article_text):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO articles (site, category, url, title, published_time, modified_time, author, article_text)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (site, category, url, title, published_time, modified_time, author, article_text))
    conn.commit()  # Commit after every insert to ensure data is saved

# Fetch metadata and article text from the URL
def fetch_metadata_and_article(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get title
        title = soup.title.string if soup.title else "Title not found"

        # Get publish time
        published_time = None
        published_time_tags = [
            'meta[property="article:published_time"]',
            'meta[name="article:published_time"]',
            'meta[itemprop="datePublished"]'
        ]
        for tag in published_time_tags:
            published_time_meta = soup.select_one(tag)
            if published_time_meta and published_time_meta.get('content'):
                published_time = published_time_meta['content']
                break

        # Get modified time
        modified_time = None
        modified_time_tags = [
            'meta[property="article:modified_time"]',
            'meta[name="article:modified_time"]',
            'meta[itemprop="dateModified"]'
        ]
        for tag in modified_time_tags:
            modified_time_meta = soup.select_one(tag)
            if modified_time_meta and modified_time_meta.get('content'):
                modified_time = modified_time_meta['content']
                break

        # Get author
        author = None
        author_tags = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[itemprop="author"]'
        ]
        for tag in author_tags:
            author_meta = soup.select_one(tag)
            if author_meta and author_meta.get('content'):
                author = author_meta['content']
                break

        # Extract article text
        article_text = ""
        article_container = soup.find('article')
        if article_container:
            paragraphs = article_container.find_all('p')
            article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            # If no <article> tag is found, fall back to searching for paragraphs in large <div>
            div_container = soup.find('div', {'class': 'article-content'}) or soup.find('div', {'class': 'post-content'})
            if div_container:
                paragraphs = div_container.find_all('p')
                article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            else:
                # Fallback to finding all <p> tags in the document
                paragraphs = soup.find_all('p')
                article_text = "\n".join([p.get_text(strip=True) for p in paragraphs])

        return title, published_time, modified_time, author, article_text

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None, None, None, None

# Read the last processed row from a checkpoint file
def read_last_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return int(f.read().strip())
    return 0

# Write the last processed row to a checkpoint file
def write_checkpoint(checkpoint_file, row_count):
    with open(checkpoint_file, 'w') as f:
        f.write(str(row_count))

# Process URLs from the CSV file and save to the database with row limit
def process_csv(file_path, conn, checkpoint_file, row_limit=None):
    last_checkpoint = read_last_checkpoint(checkpoint_file)
    print(f"Resuming from row {last_checkpoint}...")

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        row_count = 0  # Counter for rows processed

        for row in reader:
            if row_count < last_checkpoint:
                row_count += 1  # Skip already processed rows
                continue

            if row_limit and row_count >= row_limit:
                print(f"\nReached row limit: {row_limit}. Stopping.")
                break

            site = row['site']
            category = row['category']
            url = row['url'].strip()

            print(f"\n{row_count} - Fetching metadata and article for: {url}")
            title, published_time, modified_time, author, article_text = fetch_metadata_and_article(url)

            if title:
                # Insert data into the database
                insert_article(conn, site, category, url, title, published_time, modified_time, author, article_text)

            row_count += 1  # Increment row counter

            # Save checkpoint after processing each row
            write_checkpoint(checkpoint_file, row_count)

# Specify the database name and CSV file path
db_name = 'articles_021024.db'
file_path = 'last_urls.csv'
row_limit = None  # Set your desired row limit here (or None for no limit)
checkpoint_file = 'progress_checkpoint.txt'  # File to store the progress

# Connect to the database and recreate the table (optional)
conn = connect_db(db_name)
recreate_table(conn)  # Uncomment if you need to recreate the table

# Process URLs from the CSV file and save metadata and article text to the database
process_csv(file_path, conn, checkpoint_file, row_limit)

# Close the database connection
conn.close()
