# 🕷️ Interactive Web Scraping Application

> A menu-driven Python application that fetches live data from real websites
> using `requests` and `BeautifulSoup`, with keyword filtering, colored output,
> and automatic file saving.
> Built as part of a Software Development Internship.

---

## 🧾 Project Overview

This application lets users interactively scrape three real websites, filter
results by keyword, and save them to a timestamped text file — all from a
clean, colorful console interface. Every component is split into its own module
following the **Single Responsibility Principle**.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🌐 3 Live Sources | Hacker News, BBC News, Books to Scrape |
| 🎨 Colored Output | ANSI colors for badges, titles, prices, links |
| 🔍 Keyword Filter | Case-insensitive search across all scraped fields |
| 💾 Save to File | Results appended to `scraped_data.txt` with timestamp |
| 🔁 Scrape Again | Loop back to source menu without restarting |
| 🛡️ Error Handling | Connection errors, timeouts, HTTP errors, parse errors |
| 🕐 Timestamp | Every result set is stamped with the scrape date-time |

---

## 🗂️ Project Structure

```
WebScraperProject/
│
├── main.py            # Entry point — menu controller, application flow
├── scraper.py         # All website-specific scraping functions
├── utils.py           # Colors, display helpers, file saving, input utils
├── scraped_data.txt   # Auto-created when user saves results
└── README.md
```

**Module responsibilities:**

```
main.py  ──imports──▶  scraper.py   (fetches + parses websites)
main.py  ──imports──▶  utils.py     (display, filter, save, input)
```

---

## ⚙️ Requirements

- Python 3.10 or higher
- `requests` library
- `beautifulsoup4` library

---

## 📦 Installation

```bash
# Install dependencies
pip install requests beautifulsoup4

# Clone / download the project, then run:
python main.py
```

---

## 🚀 How to Run

```bash
# Navigate to the project folder
cd WebScraperProject

# Run the application
python main.py
```

---

## 🖥️ Sample Console Output

### Welcome Banner
```
  ╔══════════════════════════════════════════════════════════════╗
  ║          INTERACTIVE WEB SCRAPING APPLICATION  v1.0         ║
  ║          Internship Project  ·  Python  ·  BeautifulSoup    ║
  ╠══════════════════════════════════════════════════════════════╣
  ║  Scrape live data from Hacker News, BBC News & Books        ║
  ║  Filter results · Save to file · Timestamped output         ║
  ╚══════════════════════════════════════════════════════════════╝
```

### Website Selection
```
  ┌────────────────────────────────────────────────┐
  │         SELECT A WEBSITE TO SCRAPE             │
  ├────────────────────────────────────────────────┤
  │   1.  Hacker News  — Top Stories               │
  │   2.  BBC News     — Latest Headlines          │
  │   3.  Books to Scrape — Book Listings          │
  └────────────────────────────────────────────────┘
  Your choice: 1
  ℹ  Starting scrape: Hacker News  — Top Stories
  ────────────────────────────────────────────────────────────
  ℹ  Connecting to https://news.ycombinator.com …
```

### Results Display
```
  ════════════════════════════════════════════════════════════
   HACKER NEWS  — TOP STORIES — 30 RESULT(S)
  ════════════════════════════════════════════════════════════

  Scraped at: 2024-06-15  14:32:07

   1   Show HN: I built a terminal-based AI coding assistant
       ▲ 487 points
       https://github.com/user/repo

   2   PostgreSQL 17 Released
       ▲ 312 points
       https://www.postgresql.org/about/news/postgresql-17/
```

### Keyword Filter
```
  Your choice: 1
  Enter keyword to search: python
  ✔  Found 4 result(s) matching "python"
```

### Save to File
```
  Your choice: 2
  ✔  Saved 30 result(s) → /home/user/WebScraperProject/scraped_data.txt
```

### scraped_data.txt (example)
```
======================================================================
  SOURCE    : Hacker News  — Top Stories
  SCRAPED AT: 2024-06-15  14:32:07
  RESULTS   : 30
======================================================================

[1] Show HN: I built a terminal-based AI coding assistant
     Score  : 487 points
     Link   : https://github.com/user/repo

[2] PostgreSQL 17 Released
     Score  : 312 points
     Link   : https://www.postgresql.org/about/news/postgresql-17/
```

---

## 🧠 Concepts Demonstrated

- **`requests`** — HTTP GET with custom headers and timeout
- **`BeautifulSoup`** — HTML parsing with CSS selectors and `find`/`find_all`
- **Exception handling** — `ConnectionError`, `Timeout`, `HTTPError`, `ValueError`
- **Modular design** — Three focused modules, clean imports
- **ANSI colors** — Cross-platform colored terminal output
- **File I/O** — Append mode with UTF-8 encoding
- **List comprehension & dict** — Efficient data structuring
- **Type hints** — `list[dict]`, `str`, `int` throughout
- **f-strings** — Consistent modern string formatting

---

## 👤 Author

**[Your Full Name]**
B.Tech CSE — [Year]
[College Name]
GitHub: [@yourusername](https://github.com/yourusername)

---

## 📄 License

Open source — free to use for learning and internship portfolio.
