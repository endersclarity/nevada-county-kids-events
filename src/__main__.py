"""Main entry point for the application"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Nevada County Kids Events - Event Scraping Engine"
    )
    parser.add_argument(
        "--source",
        help="Event source to scrape (e.g., knco)",
        default="knco"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cache and force fresh scrape"
    )

    args = parser.parse_args()
    print(f"Nevada County Kids Events v0.1.0")
    print(f"Source: {args.source}")
    print(f"Cache: {'disabled' if args.no_cache else 'enabled'}")
    print("\nOrchestrator not yet implemented. See E2.6.")

if __name__ == "__main__":
    main()
