import os
from datetime import datetime

import auth
import documents
import password_tools
from stego import encode_image, decode_image
from crypto_utils import generate_key


def print_header(title: str) -> None:
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def login_screen() -> str:
    """Show login/register screen until a user successfully logs in. Returns username."""

    while True:
        print_header("DOCUMENT SECURING SYSTEM")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            if auth.login_user(username, password):
                print(f"\n[+] Login successful. Welcome, {username}!")
                return username
            else:
                print("\n[!] Invalid username or password.")

        elif choice == '2':
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()

            rating, missing = password_tools.check_strength(password)
            print(f"[i] Password strength: {rating}")
            if missing:
                print("[!] Consider adding:")
                for item in missing:
                    print(f"    - {item}")

            if auth.register_user(username, password):
                print(f"[+] User '{username}' registered successfully. Please login.")
            else:
                print("[!] Username already exists.")

        elif choice == '3':
            print("Goodbye!")
            exit(0)

        else:
            print("[!] Invalid choice!")


def documents_menu(current_user: str) -> None:
    """Document management submenu."""

    while True:
        print_header("DOCUMENT MANAGEMENT")
        print("1. Add Document")
        print("2. View Document")
        print("3. List All Documents")
        print("4. Search Documents")
        print("5. Update Document")
        print("6. Delete Document")
        print("7. Back to Main Menu")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            title = input("Title: ").strip()
            content = input("Content: ").strip()
            try:
                doc_id = documents.add_document(title, content, current_user)
                print(f"[+] Document added with ID: {doc_id}")
            except FileNotFoundError as e:
                print(f"[!] Error: {e}")

        elif choice == '2':
            doc_id = input("Document ID: ").strip()
            doc = documents.view_document(doc_id)
            if doc:
                print(f"[+] Title: {doc['title']}")
                print(f"    Owner: {doc['owner']}")
                print(f"    Created: {doc['date_created']}")
                print(f"    Modified: {doc['date_modified']}")
                print(f"    Content: {doc['content']}")
            else:
                print("[!] Document not found.")

        elif choice == '3':
            docs = documents.list_documents()
            if docs:
                print("[+] All documents:")
                for doc_id, doc in docs.items():
                    print(f"    [{doc_id}] {doc['title']} (owner: {doc['owner']}, created: {doc['date_created']})")
            else:
                print("[!] No documents found.")

        elif choice == '4':
            keyword = input("Search keyword: ").strip()
            results = documents.search_documents(keyword)
            if results:
                print(f"[+] Found {len(results)} match(es):")
                for doc_id, doc in results.items():
                    print(f"    [{doc_id}] {doc['title']} (owner: {doc['owner']})")
            else:
                print("[!] No matches found.")

        elif choice == '5':
            doc_id = input("Document ID to update: ").strip()
            title = input("New title (leave blank to keep unchanged): ").strip()
            content = input("New content (leave blank to keep unchanged): ").strip()
            if documents.update_document(doc_id, title or None, content or None):
                print("[+] Document updated successfully.")
            else:
                print("[!] Document not found.")

        elif choice == '6':
            doc_id = input("Document ID to delete: ").strip()
            if documents.delete_document(doc_id):
                print("[+] Document deleted successfully.")
            else:
                print("[!] Document not found.")

        elif choice == '7':
            break

        else:
            print("[!] Invalid choice!")


def stego_menu() -> None:
    """Steganography submenu."""

    while True:
        print_header("STEGANOGRAPHY")
        print("1. Hide Message in Image")
        print("2. Extract Message from Image")
        print("3. Back to Main Menu")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            img_path = input("Enter image path: ").strip()
            message = input("Enter secret message: ").strip()
            try:
                encode_image(img_path, message)
            except (FileNotFoundError, ValueError) as e:
                print(f"[!] Error: {e}")

        elif choice == '2':
            img_path = input("Enter encoded image path: ").strip()
            try:
                decode_image(img_path)
            except FileNotFoundError as e:
                print(f"[!] Error: {e}")

        elif choice == '3':
            break

        else:
            print("[!] Invalid choice!")


def password_menu() -> None:
    """Password tools submenu."""

    while True:
        print_header("PASSWORD TOOLS")
        print("1. Check Password Strength")
        print("2. Generate Strong Password")
        print("3. Generate Hash of Text")
        print("4. Back to Main Menu")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            pwd = input("Enter password to check: ").strip()
            rating, missing = password_tools.check_strength(pwd)
            print(f"[+] Strength: {rating}")
            if missing:
                print("[!] Missing:")
                for item in missing:
                    print(f"    - {item}")

        elif choice == '2':
            try:
                length = int(input("Enter desired length (default 12): ").strip() or 12)
                pwd = password_tools.generate_password(length)
                print(f"[+] Generated password: {pwd}")
            except ValueError as e:
                print(f"[!] Error: {e}")

        elif choice == '3':
            text = input("Enter text to hash: ").strip()
            algo = input("Algorithm (sha256/sha512/md5) [default sha256]: ").strip() or "sha256"
            try:
                result = password_tools.hash_text(text, algo)
                print(f"[+] {algo.upper()} hash: {result}")
            except ValueError as e:
                print(f"[!] Error: {e}")

        elif choice == '4':
            break

        else:
            print("[!] Invalid choice!")


def generate_report() -> None:
    """Display a summary report of system usage."""

    print_header("SYSTEM REPORT")

    users = auth.list_users()
    docs = documents.list_documents()

    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total registered users : {len(users)}")
    print(f"Total documents stored : {len(docs)}")

    if docs:
        print("\nDocuments by owner:")
        owner_counts = {}
        for doc in docs.values():
            owner_counts[doc['owner']] = owner_counts.get(doc['owner'], 0) + 1
        for owner, count in owner_counts.items():
            print(f"    {owner}: {count} document(s)")

    input("\nPress Enter to return to main menu...")


def main_menu(current_user: str) -> None:
    """Main menu shown after login."""

    while True:
        print_header(f"MAIN MENU  (Logged in as: {current_user})")
        print("1. Document Management")
        print("2. Steganography")
        print("3. Password Tools")
        print("4. Generate Report")
        print("5. Logout")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            documents_menu(current_user)
        elif choice == '2':
            stego_menu()
        elif choice == '3':
            password_menu()
        elif choice == '4':
            generate_report()
        elif choice == '5':
            print(f"[+] Logged out. Goodbye, {current_user}!")
            break
        else:
            print("[!] Invalid choice!")


def main():
    """Program entry point."""

    # Ensure encryption key exists before anything else runs
    if not os.path.exists("data/secret.key"):
        os.makedirs("data", exist_ok=True)
        generate_key()

    while True:
        current_user = login_screen()
        main_menu(current_user)


if __name__ == "__main__":
    main()