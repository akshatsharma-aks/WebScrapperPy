"""
main.py
────────────────────────────────────────────────────────────────────────────────
Entry point and menu controller for the Interactive Web Scraping Application.

Architecture:
  main.py  ──imports──▶  scraper.py  (fetches & parses websites)
  main.py  ──imports──▶  utils.py    (display, filtering, file saving)

Flow per session:
  1. User picks a website from the source menu
  2. App scrapes and displays results
  3. User can optionally filter by keyword
  4. User can optionally save results to scraped_data.txt
  5. User decides to scrape again or exit

Author  : [Your Name]
Project : Interactive Web Scraping Application
Version : 1.0
────────────────────────────────────────────────────────────────────────────────
"""

from scraper import SCRAPERS
from utils import (
    Color,
    print_welcome_banner,
    print_section_header,
    print_menu_box,
    print_results,
    print_success,
    print_error,
    print_info,
    print_divider,
    filter_by_keyword,
    save_to_file,
    get_int_input,
)


# ─────────────────────────────────────────────────────────────────────────────
#  WEBSITE SELECTION MENU
# ─────────────────────────────────────────────────────────────────────────────

def show_source_menu() -> int:
    """
    Display the website selection menu and return the user's choice.

    Returns:
        Integer key from SCRAPERS dict (1, 2, or 3)
    """
    options = [name for _, (name, _) in sorted(SCRAPERS.items())]
    print_menu_box("SELECT A WEBSITE TO SCRAPE", options)
    return get_int_input("Your choice: ", range(1, len(SCRAPERS) + 1))


# ─────────────────────────────────────────────────────────────────────────────
#  POST-SCRAPE ACTION MENU
# ─────────────────────────────────────────────────────────────────────────────

def show_action_menu(items: list[dict], source_name: str) -> str:
    """
    After displaying results, let the user choose what to do next.

    Options:
      1. Filter results by keyword
      2. Save results to file
      3. Scrape again (return to source menu)
      4. Exit

    Args:
        items       : The scraped results currently in memory
        source_name : Human-readable name of the source that was scraped

    Returns:
        One of: "filter" | "save" | "again" | "exit"
    """
    actions = [
        "Filter results by keyword",
        "Save results to  scraped_data.txt",
        "Scrape a different website",
        "Exit application",
    ]
    print_menu_box("WHAT WOULD YOU LIKE TO DO?", actions)
    choice = get_int_input("Your choice: ", range(1, 5))

    action_map = {1: "filter", 2: "save", 3: "again", 4: "exit"}
    return action_map[choice]


# ─────────────────────────────────────────────────────────────────────────────
#  KEYWORD FILTER FLOW
# ─────────────────────────────────────────────────────────────────────────────

def run_filter(items: list[dict], source_name: str) -> list[dict]:
    """
    Ask for a keyword, filter items, and display filtered results.

    Args:
        items       : Full unfiltered result list
        source_name : Source label used in the display header

    Returns:
        Filtered list (may be the original list if no keyword or no matches)
    """
    print_section_header("FILTER RESULTS")
    keyword = input(f"  {Color.BOLD}Enter keyword to search: {Color.RESET}").strip()

    if not keyword:
        print_info("No keyword entered — showing all results.")
        return items

    filtered = filter_by_keyword(items, keyword)

    if not filtered:
        print_info(f'No results matched "{keyword}". Showing original list.')
        return items

    print_success(f'Found {len(filtered)} result(s) matching "{keyword}"')
    print_results(filtered, f'{source_name} (filtered: "{keyword}")')
    return filtered


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Drive the full application lifecycle:
      welcome → source selection → scrape → display → actions → loop/exit
    """
    print_welcome_banner()

    # Outer loop — restarts at website selection when user picks "scrape again"
    while True:

        # ── Step 1: Pick a website ──
        source_choice             = show_source_menu()
        source_name, scrape_func  = SCRAPERS[source_choice]

        print_info(f"Starting scrape: {source_name}")
        print_divider()

        # ── Step 2: Scrape ──
        items = scrape_func()

        if not items:
            # scraper.py already printed a specific error — just prompt the user
            print_error("No data was retrieved. The site may be down or its layout has changed.")
            print_info("Try again or choose a different website.\n")
            continue  # Back to source menu

        # ── Step 3: Display results ──
        print_results(items, source_name)
        current_items = items  # may be narrowed by filter later

        # ── Step 4: Post-scrape action loop ──
        #    Stays here until the user picks "scrape again" or "exit"
        while True:
            action = show_action_menu(current_items, source_name)

            if action == "filter":
                current_items = run_filter(current_items, source_name)

            elif action == "save":
                save_to_file(current_items, source_name)

            elif action == "again":
                print_info("Returning to website selection…\n")
                break  # Break inner loop → outer loop restarts

            elif action == "exit":
                print_exit_message()
                return  # Terminate the application


# ─────────────────────────────────────────────────────────────────────────────
#  EXIT MESSAGE
# ─────────────────────────────────────────────────────────────────────────────

def print_exit_message() -> None:
    print(f"""
{Color.CYAN}{Color.BOLD}  ╔══════════════════════════════════════════════════════════════╗
  ║   Thank you for using the Web Scraping App!  Goodbye  👋     ║
  ║   Check scraped_data.txt for any saved results.              ║
  ╚══════════════════════════════════════════════════════════════╝{Color.RESET}
""")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
