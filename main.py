"""
Interactive CLI for URL Shortener.

Run with: python3 main.py
"""

from url_shortener import URLShortener


def print_menu():
    """Display the main menu."""
    print("\n" + "="*50)
    print("URL SHORTENER - Interactive CLI")
    print("="*50)
    print("1. Create a short URL")
    print("2. Retrieve original URL")
    print("3. Update a short URL")
    print("4. Delete a short URL")
    print("5. List all URLs")
    print("6. Exit")
    print("="*50)


def main():
    """Main CLI loop."""
    shortener = URLShortener()
    
    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()
        
        try:
            if choice == "1":
                # Create
                original = input("Enter the original URL: ").strip()
                custom = input("Enter custom short code (or press Enter to auto-generate): ").strip()
                
                if custom:
                    short_code = shortener.create(original, custom_short_code=custom)
                else:
                    short_code = shortener.create(original)
                
                print(f"✓ Short URL created: {short_code} -> {original}")
            
            elif choice == "2":
                # Read
                short_code = input("Enter the short code to look up: ").strip()
                url = shortener.read(short_code)
                
                if url:
                    print(f"✓ Original URL: {url}")
                else:
                    print(f"✗ Short code '{short_code}' not found")
            
            elif choice == "3":
                # Update
                short_code = input("Enter the short code to update: ").strip()
                new_url = input("Enter the new original URL: ").strip()
                
                try:
                    shortener.update(short_code, new_url)
                    print(f"✓ Updated: {short_code} -> {new_url}")
                except ValueError as e:
                    print(f"✗ Error: {e}")
            
            elif choice == "4":
                # Delete
                short_code = input("Enter the short code to delete: ").strip()
                
                try:
                    shortener.delete(short_code)
                    print(f"✓ Deleted: {short_code}")
                except ValueError as e:
                    print(f"✗ Error: {e}")
            
            elif choice == "5":
                # List all
                all_urls = shortener.list_all()
                if all_urls:
                    print("\nAll stored mappings:")
                    print("-" * 50)
                    for short, full in all_urls.items():
                        print(f"  {short:15} -> {full}")
                    print("-" * 50)
                else:
                    print("No URLs stored yet.")
            
            elif choice == "6":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please select 1-6.")
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
