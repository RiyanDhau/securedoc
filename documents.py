import json
import os
from datetime import datetime
from crypto_utils import encrypt_data, decrypt_data

DOCUMENTS_FILE = "data/documents.json"


def load_documents() -> dict:
    """Load all documents from the JSON file."""

    if not os.path.exists(DOCUMENTS_FILE):
        return {}

    with open(DOCUMENTS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_documents(documents: dict) -> None:
    """Save all documents to the JSON file."""

    os.makedirs(os.path.dirname(DOCUMENTS_FILE), exist_ok=True)

    with open(DOCUMENTS_FILE, "w") as f:
        json.dump(documents, f, indent=4)


def get_next_id(documents: dict) -> str:
    """Generate the next sequential document ID."""

    if not documents:
        return "1"

    return str(max(int(doc_id) for doc_id in documents) + 1)


def add_document(title: str, content: str, owner: str) -> str:
    """Add a new document with encrypted content. Returns the new document ID."""

    documents = load_documents()
    doc_id = get_next_id(documents)

    documents[doc_id] = {
        "title": title,
        "content": encrypt_data(content),
        "owner": owner,
        "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_documents(documents)
    return doc_id


def view_document(doc_id: str) -> dict:
    """View a single document with decrypted content. Returns None if not found."""

    documents = load_documents()

    if doc_id not in documents:
        return None

    doc = documents[doc_id].copy()
    doc["content"] = decrypt_data(doc["content"])
    return doc


def list_documents() -> dict:
    """List all documents (titles only, content stays encrypted/hidden)."""

    documents = load_documents()
    return {
        doc_id: {
            "title": doc["title"],
            "owner": doc["owner"],
            "date_created": doc["date_created"]
        }
        for doc_id, doc in documents.items()
    }


def search_documents(keyword: str) -> dict:
    """Search documents by title keyword (case-insensitive)."""

    documents = load_documents()
    keyword = keyword.lower()

    results = {
        doc_id: doc for doc_id, doc in documents.items()
        if keyword in doc["title"].lower()
    }

    return results


def update_document(doc_id: str, title: str = None, content: str = None) -> bool:
    """Update a document's title and/or content. Returns False if not found."""

    documents = load_documents()

    if doc_id not in documents:
        return False

    if title is not None:
        documents[doc_id]["title"] = title

    if content is not None:
        documents[doc_id]["content"] = encrypt_data(content)

    documents[doc_id]["date_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_documents(documents)
    return True


def delete_document(doc_id: str) -> bool:
    """Delete a document. Returns False if not found."""

    documents = load_documents()

    if doc_id not in documents:
        return False

    del documents[doc_id]
    save_documents(documents)
    return True


def main():
    """Main menu."""

    print("1. Add Document")
    print("2. View Document")
    print("3. List All Documents")
    print("4. Search Documents")
    print("5. Update Document")
    print("6. Delete Document")

    choice = input("Enter choice: ").strip()

    if choice == '1':
        title = input("Title: ").strip()
        content = input("Content: ").strip()
        owner = input("Owner (username): ").strip()

        try:
            doc_id = add_document(title, content, owner)
            print(f"[+] Document added with ID: {doc_id}")
        except FileNotFoundError as e:
            print(f"[!] Error: {e} (Did you generate the encryption key first?)")

    elif choice == '2':
        doc_id = input("Document ID: ").strip()
        doc = view_document(doc_id)

        if doc:
            print(f"[+] Title: {doc['title']}")
            print(f"    Owner: {doc['owner']}")
            print(f"    Created: {doc['date_created']}")
            print(f"    Modified: {doc['date_modified']}")
            print(f"    Content: {doc['content']}")
        else:
            print("[!] Document not found.")

    elif choice == '3':
        docs = list_documents()
        if docs:
            print("[+] All documents:")
            for doc_id, doc in docs.items():
                print(f"    [{doc_id}] {doc['title']} (owner: {doc['owner']}, created: {doc['date_created']})")
        else:
            print("[!] No documents found.")

    elif choice == '4':
        keyword = input("Search keyword: ").strip()
        results = search_documents(keyword)

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

        if update_document(doc_id, title or None, content or None):
            print("[+] Document updated successfully.")
        else:
            print("[!] Document not found.")

    elif choice == '6':
        doc_id = input("Document ID to delete: ").strip()

        if delete_document(doc_id):
            print("[+] Document deleted successfully.")
        else:
            print("[!] Document not found.")

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()