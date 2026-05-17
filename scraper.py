"""
scraper.py
────────────────────────────────────────────────────────────────────────────────
Web scraping module for the Interactive Web Scraping Application.

Contains one scraper function per supported website, plus a shared HTTP helper.

Supported sources:
  1. Hacker News        — top story titles, scores, links  (via JSON API)
  2. BBC News           — headline titles and article links (multi-strategy HTML)
  3. Books to Scrape   — book titles, prices, star ratings, links

Why JSON API for Hacker News?
  The Hacker News Algolia API (hn.algolia.com) is public, free, requires no key,
  and is far more stable than scraping the HTML — ideal for internship projects.

Why multi-strategy for BBC?
  BBC frequently updates its frontend React components and data-testid attributes.
  The scraper tries four selector strategies in order and uses the first that
  returns real headlines, making it resilient to minor BBC HTML changes.

Every scraper returns a list of dicts so the rest of the app handles results
uniformly regardless of which site was scraped.

Author  : [Your Name]
Project : Interactive Web Scraping Application
Version : 1.1  (BBC fix — multi-strategy selectors; HN upgraded to JSON API)
────────────────────────────────────────────────────────────────────────────────
"""

import requests
from bs4 import BeautifulSoup
from utils import print_info, print_error

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Realistic browser headers — required by many sites to avoid 403 blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",   # en-GB gives BBC its English edition
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}

# Timeout in seconds — prevents the app hanging on slow/down servers
REQUEST_TIMEOUT = 15

# Cap on results shown per scrape (keeps terminal output readable)
MAX_RESULTS = 30

# BBC base domain (needed to build absolute URLs from relative hrefs)
BBC_BASE = "https://www.bbc.com"


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED HTTP HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_page(url: str) -> BeautifulSoup | None:
    """
    GET a URL and return a BeautifulSoup parse tree.
    All network/HTTP exceptions are caught here so individual scrapers stay clean.

    Returns None on any failure (caller checks for None before proceeding).
    """
    try:
        print_info(f"Connecting to {url} …")
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()                          # raises on 4xx / 5xx
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.ConnectionError:
        print_error("No internet connection. Please check your network.")
    except requests.exceptions.Timeout:
        print_error(f"Request timed out after {REQUEST_TIMEOUT}s.")
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP {e.response.status_code} from server.")
    except requests.exceptions.RequestException as e:
        print_error(f"Network error: {e}")
    return None


def _fetch_json(url: str) -> dict | list | None:
    """
    GET a JSON endpoint and return the parsed Python object.
    Used for the Hacker News Algolia API.

    Returns None on any failure.
    """
    try:
        print_info(f"Fetching API: {url} …")
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print_error("No internet connection. Please check your network.")
    except requests.exceptions.Timeout:
        print_error(f"API request timed out after {REQUEST_TIMEOUT}s.")
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP {e.response.status_code} from API.")
    except ValueError:
        print_error("API returned invalid JSON.")
    except requests.exceptions.RequestException as e:
        print_error(f"Network error: {e}")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  SCRAPER 1 — HACKER NEWS  (JSON API — rock solid, no HTML parsing needed)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_hacker_news() -> list[dict]:
    """
    Fetch the Hacker News front-page stories via the Algolia Search API.

    Why API instead of HTML scraping?
      hn.algolia.com/api is public, free, key-less, and returns clean JSON.
      It is far more stable than parsing HN's HTML, which can change any time.

    Endpoint : https://hn.algolia.com/api/v1/search?tags=front_page
    Data     : story title, original URL (or HN discussion link), point score

    Returns:
        [{"title": ..., "link": ..., "score": ...}, ...]
        Empty list on failure.
    """
    api_url = (
        f"https://hn.algolia.com/api/v1/search"
        f"?tags=front_page&hitsPerPage={MAX_RESULTS}"
    )

    data = _fetch_json(api_url)
    if data is None:
        return []

    results = []
    try:
        hits = data.get("hits", [])
        for hit in hits[:MAX_RESULTS]:
            title  = hit.get("title", "").strip()
            # 'url' is the external link; fall back to the HN discussion page
            link   = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            points = hit.get("points", 0)
            score  = f"{points} points" if points else ""

            if title:
                results.append({"title": title, "link": link, "score": score})

    except Exception as e:
        print_error(f"Parsing Hacker News API response failed: {e}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  SCRAPER 2 — BBC NEWS  (multi-strategy HTML parsing)
# ─────────────────────────────────────────────────────────────────────────────

def _bbc_try_data_testid(soup: BeautifulSoup) -> list[dict]:
    """
    Strategy A — data-testid attributes.
    BBC's React components tag headline elements with data-testid="card-headline".
    This is the most specific and reliable selector when it exists.
    """
    results = []
    seen    = set()

    # Primary: dedicated headline testid
    for el in soup.select('[data-testid="card-headline"]'):
        title = el.get_text(strip=True)
        if not title or len(title) < 15 or title in seen:
            continue
        seen.add(title)

        # Walk up to find a parent <a> for the link
        anchor = el.find_parent("a") or el.find("a")
        link   = ""
        if anchor and anchor.get("href"):
            href = anchor["href"]
            link = href if href.startswith("http") else f"{BBC_BASE}{href}"

        results.append({"title": title, "link": link})
        if len(results) >= MAX_RESULTS:
            break

    return results


def _bbc_try_headings(soup: BeautifulSoup) -> list[dict]:
    """
    Strategy B — h2 and h3 heading tags.
    BBC historically used <h3> for card headlines; newer layouts use <h2>.
    We try both, deduplicate, and filter nav/footer noise by length.
    """
    results = []
    seen    = set()

    for tag in soup.find_all(["h2", "h3"]):
        title = tag.get_text(strip=True)

        # Filter: too short = nav item / button; too long = paragraph text
        if not title or not (20 <= len(title) <= 200):
            continue
        if title in seen:
            continue
        seen.add(title)

        anchor = tag.find_parent("a") or tag.find("a")
        link   = ""
        if anchor and anchor.get("href"):
            href = anchor["href"]
            link = href if href.startswith("http") else f"{BBC_BASE}{href}"

        results.append({"title": title, "link": link})
        if len(results) >= MAX_RESULTS:
            break

    return results


def _bbc_try_anchor_scan(soup: BeautifulSoup) -> list[dict]:
    """
    Strategy C — scan all <a> tags whose text looks like a headline.
    Useful when BBC wraps headlines directly in styled anchor tags
    with no intermediate heading element.
    """
    results = []
    seen    = set()

    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(strip=True)
        href  = anchor["href"]

        # Only BBC article paths (start with /news/ or /sport/ etc.)
        if not (href.startswith("/news/") or href.startswith("/sport/")):
            continue
        if not title or not (25 <= len(title) <= 180):
            continue
        if title in seen:
            continue
        seen.add(title)

        link = f"{BBC_BASE}{href}"
        results.append({"title": title, "link": link})
        if len(results) >= MAX_RESULTS:
            break

    return results


def _bbc_try_any_testid(soup: BeautifulSoup) -> list[dict]:
    """
    Strategy D — broad data-testid sweep.
    Catches any element whose testid contains 'headline' or 'title',
    as BBC sometimes renames testids between deployments.
    """
    results = []
    seen    = set()

    for el in soup.select("[data-testid]"):
        testid = el.get("data-testid", "")
        if "headline" not in testid and "title" not in testid:
            continue
        title = el.get_text(strip=True)
        if not title or len(title) < 20 or title in seen:
            continue
        seen.add(title)

        anchor = el.find_parent("a") or el.find("a")
        link   = ""
        if anchor and anchor.get("href"):
            href = anchor["href"]
            link = href if href.startswith("http") else f"{BBC_BASE}{href}"

        results.append({"title": title, "link": link})
        if len(results) >= MAX_RESULTS:
            break

    return results


def scrape_bbc_news() -> list[dict]:
    """
    Scrape BBC News headlines using a cascade of four selector strategies.

    BBC frequently ships frontend changes that break single-selector scrapers
    (as happened with the original <h3>-only approach that returned only
    "The BBC is in multiple languages"). This function tries strategies in
    order of specificity and returns the first set with ≥ 5 results.

    Strategies (tried in order):
      A. data-testid="card-headline"   — most specific, React component tag
      B. <h2> / <h3> heading tags     — classic semantic HTML approach
      C. <a href="/news/..."> scan    — article links with headline text
      D. Any data-testid with         — broad fallback for renamed testids
         "headline" or "title"

    URL  : https://www.bbc.com/news
    Data : article headline text, article URL

    Returns:
        [{"title": ..., "link": ...}, ...]   Empty list on total failure.
    """
    soup = _fetch_page(f"{BBC_BASE}/news")
    if soup is None:
        return []

    strategies = [
        ("data-testid card-headline", _bbc_try_data_testid),
        ("h2/h3 headings",            _bbc_try_headings),
        ("anchor /news/ scan",        _bbc_try_anchor_scan),
        ("broad data-testid sweep",   _bbc_try_any_testid),
    ]

    for strategy_name, strategy_fn in strategies:
        try:
            results = strategy_fn(soup)
            if len(results) >= 5:          # Enough real headlines → use this
                print_info(f"BBC parsed via: {strategy_name} ({len(results)} items)")
                return results
        except Exception as e:
            print_error(f"BBC strategy '{strategy_name}' crashed: {e}")
            continue                        # Try the next strategy

    # If every strategy returned < 5 results, return whatever the best gave us
    print_error(
        "BBC News returned very few headlines. "
        "Their site structure may have changed again. "
        "Try option 1 (Hacker News) or option 3 (Books) instead."
    )
    return []


# ─────────────────────────────────────────────────────────────────────────────
#  SCRAPER 3 — BOOKS TO SCRAPE
# ─────────────────────────────────────────────────────────────────────────────

_RATING_MAP = {
    "One":   "★☆☆☆☆",
    "Two":   "★★☆☆☆",
    "Three": "★★★☆☆",
    "Four":  "★★★★☆",
    "Five":  "★★★★★",
}


def scrape_books() -> list[dict]:
    """
    Scrape Books to Scrape — a purpose-built, scraping-friendly practice site.

    URL      : https://books.toscrape.com
    Data     : book title, price (GBP), star rating, link to detail page
    Selector : <article class="product_pod"> wraps each book card.

    This site never blocks scrapers and never changes its HTML — ideal for
    reliable, always-working demonstration in internship projects.

    Returns:
        [{"title": ..., "price": ..., "rating": ..., "link": ...}, ...]
        Empty list on failure.
    """
    base_url = "https://books.toscrape.com"
    soup     = _fetch_page(base_url)
    if soup is None:
        return []

    results = []

    try:
        articles = soup.select("article.product_pod")

        for article in articles[:MAX_RESULTS]:

            # Title lives in the 'title' attribute of the nested <a>
            h3     = article.find("h3")
            anchor = h3.find("a") if h3 else None
            title  = anchor["title"] if anchor and anchor.get("title") else "Unknown Title"

            # Price — always present in <p class="price_color">
            price_tag = article.find("p", class_="price_color")
            price     = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Rating — encoded as a second CSS class: "star-rating Three"
            star_tag   = article.find("p", class_="star-rating")
            rating_key = star_tag["class"][1] if star_tag and len(star_tag["class"]) > 1 else ""
            rating     = _RATING_MAP.get(rating_key, "N/A")

            # Link — relative path like "catalogue/a-light-in-the-attic_1000/index.html"
            href = anchor["href"] if anchor and anchor.get("href") else ""
            if href:
                href_clean = href.lstrip("./")
                link = f"{base_url}/catalogue/{href_clean}"
            else:
                link = ""

            results.append({"title": title, "price": price, "rating": rating, "link": link})

    except Exception as e:
        print_error(f"Parsing Books to Scrape failed: {e}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  SCRAPER REGISTRY
#  main.py imports SCRAPERS to build the menu and dispatch calls.
#  To add a 4th site: write a new function above and add one line here.
# ─────────────────────────────────────────────────────────────────────────────

SCRAPERS: dict[int, tuple[str, callable]] = {
    1: ("Hacker News    — Top Stories (API)",  scrape_hacker_news),
    2: ("BBC News       — Latest Headlines",   scrape_bbc_news),
    3: ("Books to Scrape — Book Listings",     scrape_books),
}