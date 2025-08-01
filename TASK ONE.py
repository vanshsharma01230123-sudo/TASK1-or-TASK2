"app.py (Main Flask App)"
from flask import Flask, render_template, request
from scraper import fetch_case_data, init_db, log_query
import os

app = Flask(__name__)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    year = request.form['year']

    try:
        result = fetch_case_data(case_type, case_number, year)
        log_query(case_type, case_number, year, result['raw_html'])
        return render_template('result.html', data=result)
    except Exception as e:
        return render_template('result.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
"""scraper.py """
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_case_data(case_type, case_number, filing_year):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Example: Replace with actual Faridabad court search URL
        page.goto("https://services.ecourts.gov.in/ecourtindia_v6/")

        # Interact with form (update selectors as needed)
        # Example navigation and scraping here is pseudo-structured

        page.fill('input[name="case_type"]', case_type)
        page.fill('input[name="case_number"]', case_number)
        page.fill('input[name="filing_year"]', filing_year)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Parse details (example structure – update with actual court HTML)
        data = {
            "Parties": soup.find("div", {"id": "parties"}).text.strip(),
            "Filing Date": soup.find("span", {"id": "filing_date"}).text.strip(),
            "Next Hearing": soup.find("span", {"id": "next_hearing"}).text.strip(),
            "Latest Order PDF": soup.find("a", {"class": "pdf-link"})['href']
        }

        browser.close()
        return data, html
"database.py"
import sqlite3
from datetime import datetime

def log_query(case_type, case_number, filing_year, raw_html):
    conn = sqlite3.connect('queries.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT,
        case_number TEXT,
        filing_year TEXT,
        timestamp TEXT,
        raw_response TEXT
    )''')

    c.execute("INSERT INTO queries VALUES (NULL, ?, ?, ?, ?, ?)", (
        case_type, case_number, filing_year, datetime.now().isoformat(), raw_html
    ))
    conn.commit()
    conn.close()
"templates/index.html"
<!DOCTYPE html>
<html>
<head>
  <title>Court Data Fetcher</title>
</head>
<body>
  <h2>Search Court Case</h2>
  <form method="POST">
    <label>Case Type:</label>
    <input name="case_type" required><br>
    <label>Case Number:</label>
    <input name="case_number" required><br>
    <label>Filing Year:</label>
    <input name="filing_year" required><br>
    <button type="submit">Search</button>
  </form>
  {% if error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}
</body>
</html>
