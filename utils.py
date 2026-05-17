"""
utils.py
────────────────────────────────────────────────────────────────────────────────
Utility module for the Interactive Web Scraping Application.

Provides:
  - ANSI color codes for colorful console output
  - Print helpers  : banners, headers, tables, success/error messages
  - File helpers   : save scraped results to timestamped text file
  - Misc helpers   : keyword filter, timestamp generator

Author  : [Your Name]
Project : Interactive Web Scraping Application
Version : 1.0
────────────────────────────────────────────────────────────────────────────────
"""

import os
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  ANSI COLOR CODES
#  These work on Linux/macOS terminals and modern Windows terminals (Win10+).
#  If colors look like garbage, set NO_COLOR=1 in your environment.
# ─────────────────────────────────────────────────────────────────────────────

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"

    # Backgrounds (used sparingly for headers)
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"


def _colorize(text: str, *codes: str) -> str:
    """Wrap text in ANSI codes and reset at the end."""
    return "".join(codes) + text + Color.RESET


# ─────────────────────────────────────────────────────────────────────────────
#  BANNER & SECTION HEADERS
# ─────────────────────────────────────────────────────────────────────────────

def print_welcome_banner() -> None:
    """Print the application welcome banner."""
    banner = f"""
{Color.CYAN}{Color.BOLD}
  ╔══════════════════════════════════════════════════════════════╗
  ║          INTERACTIVE WEB SCRAPING APPLICATION  v1.0         ║
  ║          Internship Project  ·  Python  ·  BeautifulSoup    ║
  ╠══════════════════════════════════════════════════════════════╣
  ║  Scrape live data from Hacker News, BBC News & Books        ║
  ║  Filter results · Save to file · Timestamped output         ║
  ╚══════════════════════════════════════════════════════════════╝
{Color.RESET}"""
    print(banner)


def print_section_header(title: str) -> None:
    """Print a styled section header."""
    width = 60
    print(f"\n{Color.CYAN}{Color.BOLD}  {'═' * width}")
    print(f"   {title.upper()}")
    print(f"  {'═' * width}{Color.RESET}\n")


def print_menu_box(title: str, options: list[str]) -> None:
    """
    Render a bordered menu box.

    Args:
        title   : Box title string
        options : List of option strings (numbered automatically)
    """
    width = 48
    print(f"\n{Color.BLUE}{Color.BOLD}  ┌{'─' * width}┐")
    # Center the title
    padded = title.center(width)
    print(f"  │{padded}│")
    print(f"  ├{'─' * width}┤")
    for i, opt in enumerate(options, start=1):
        line = f"   {i}.  {opt}"
        print(f"  │{line:<{width}}│")
    print(f"  └{'─' * width}┘{Color.RESET}")


# ─────────────────────────────────────────────────────────────────────────────
#  SUCCESS / ERROR / INFO MESSAGES
# ─────────────────────────────────────────────────────────────────────────────

def print_success(message: str) -> None:
    print(f"  {Color.GREEN}{Color.BOLD}✔  {message}{Color.RESET}")

def print_error(message: str) -> None:
    print(f"  {Color.RED}{Color.BOLD}✖  ERROR: {message}{Color.RESET}")

def print_info(message: str) -> None:
    print(f"  {Color.YELLOW}ℹ  {message}{Color.RESET}")

def print_divider() -> None:
    print(f"  {Color.GREY}{'─' * 60}{Color.RESET}")


# ─────────────────────────────────────────────────────────────────────────────
#  RESULT DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

def print_results(items: list[dict], source_name: str) -> None:
    """
    Display scraped results in a clean numbered format.

    Each item dict should contain at minimum:
      - 'title'  : str  — headline or product name
    And optionally:
      - 'link'   : str  — URL
      - 'price'  : str  — price (for e-commerce sources)
      - 'rating' : str  — star rating
      - 'score'  : str  — upvote/comment count (for news sources)

    Args:
        items       : List of result dicts from the scraper
        source_name : Human-readable name of the scraped website
    """
    if not items:
        print_info("No results to display.")
        return

    print_section_header(f"{source_name} — {len(items)} result(s)")
    timestamp = get_timestamp()
    print(f"  {Color.GREY}Scraped at: {timestamp}{Color.RESET}\n")

    for idx, item in enumerate(items, start=1):
        # ── Index badge ──
        badge = _colorize(f" {idx:>2} ", Color.BG_CYAN, Color.WHITE, Color.BOLD)
        title = _colorize(item.get("title", "N/A"), Color.WHITE, Color.BOLD)
        print(f"  {badge}  {title}")

        # Optional fields — print only if present
        if item.get("score"):
            print(f"       {Color.YELLOW}▲ {item['score']}{Color.RESET}")

        if item.get("price"):
            print(f"       {Color.GREEN}Price: {item['price']}{Color.RESET}", end="")
            if item.get("rating"):
                print(f"  {Color.YELLOW}★ {item['rating']}{Color.RESET}", end="")
            print()

        if item.get("link"):
            # Truncate very long URLs for display cleanliness
            url = item["link"]
            display_url = (url[:72] + "…") if len(url) > 75 else url
            print(f"       {Color.CYAN}{Color.DIM}{display_url}{Color.RESET}")

        print()  # blank line between items

    print_divider()


# ─────────────────────────────────────────────────────────────────────────────
#  KEYWORD FILTER
# ─────────────────────────────────────────────────────────────────────────────

def filter_by_keyword(items: list[dict], keyword: str) -> list[dict]:
    """
    Case-insensitive keyword search across title and link fields.

    Args:
        items   : Full list of scraped result dicts
        keyword : Search term entered by the user

    Returns:
        Filtered list containing only matching items
    """
    kw = keyword.strip().lower()
    if not kw:
        return items  # Empty keyword → return everything

    filtered = []
    for item in items:
        # Search in title and link fields (both optional)
        haystack = (item.get("title", "") + " " + item.get("link", "")).lower()
        if kw in haystack:
            filtered.append(item)

    return filtered


# ─────────────────────────────────────────────────────────────────────────────
#  FILE SAVE
# ─────────────────────────────────────────────────────────────────────────────

def save_to_file(items: list[dict], source_name: str, filename: str = "scraped_data.txt") -> None:
    """
    Append scraped results to a plain-text file with a timestamp header.

    Each save session is separated by a clear divider block so the file
    remains readable across multiple scrape runs.

    Args:
        items       : List of result dicts to save
        source_name : Name of the website that was scraped
        filename    : Output file path (default: scraped_data.txt)
    """
    if not items:
        print_error("Nothing to save — result list is empty.")
        return

    timestamp = get_timestamp()

    try:
        # 'a' mode → append; file is created if it doesn't exist
        with open(filename, "a", encoding="utf-8") as f:
            # ── Session header ──
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"  SOURCE    : {source_name}\n")
            f.write(f"  SCRAPED AT: {timestamp}\n")
            f.write(f"  RESULTS   : {len(items)}\n")
            f.write("=" * 70 + "\n\n")

            # ── Individual results ──
            for idx, item in enumerate(items, start=1):
                f.write(f"[{idx}] {item.get('title', 'N/A')}\n")
                if item.get("score"):
                    f.write(f"     Score  : {item['score']}\n")
                if item.get("price"):
                    f.write(f"     Price  : {item['price']}\n")
                if item.get("rating"):
                    f.write(f"     Rating : {item['rating']}\n")
                if item.get("link"):
                    f.write(f"     Link   : {item['link']}\n")
                f.write("\n")

        # Resolve to absolute path for clarity in the success message
        abs_path = os.path.abspath(filename)
        print_success(f"Saved {len(items)} result(s) → {abs_path}")

    except OSError as e:
        print_error(f"Could not write to file: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  MISC HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_timestamp() -> str:
    """Return current date-time formatted as a readable string."""
    return datetime.now().strftime("%Y-%m-%d  %H:%M:%S")


def get_int_input(prompt: str, valid_range: range) -> int:
    """
    Prompt the user for an integer within a given range.
    Re-prompts on invalid input — never crashes.

    Args:
        prompt      : Text shown to the user
        valid_range : Acceptable integer values (e.g. range(1, 5))

    Returns:
        A valid integer from within valid_range
    """
    while True:
        raw = input(f"  {Color.BOLD}{prompt}{Color.RESET}").strip()
        try:
            value = int(raw)
            if value in valid_range:
                return value
            print_error(f"Please enter a number between {valid_range.start} and {valid_range.stop - 1}.")
        except ValueError:
            print_error("Invalid input — please enter a whole number.")
