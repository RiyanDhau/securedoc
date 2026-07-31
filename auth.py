import json
import os
from  password_tools import hash_password, verify_password

USERS_FILE = "data/users.json"


def load_users() -> dict:
    """Load all users from the JSON file."""

    if not os.path.exists(USERS_FILE):
        return {}

    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users: dict) -> None:
    """Save all users to the JSON file."""

    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def register_user(username: str, password: str) -> bool:
    """Register a new user. Returns False if username already exists."""

    users = load_users()

    if username in users:
        return False

    hashed, salt = hash_password(password)
    users[username] = {
        "password_hash": hashed,
        "salt": salt
    }

    save_users(users)
    return True


def login_user(username: str, password: str) -> bool:
    """Verify login credentials. Returns True if valid."""

    users = load_users()

    if username not in users:
        return False

    stored_hash = users[username]["password_hash"]
    salt = users[username]["salt"]

    return verify_password(password, stored_hash, salt)


def delete_user(username: str) -> bool:
    """Delete a user account. Returns False if user doesn't exist."""

    users = load_users()

    if username not in users:
        return False

    del users[username]
    save_users(users)
    return True


def list_users() -> list[str]:
    """Return a list of all registered usernames."""

    users = load_users()
    return list(users.keys())


def main():
    """Main menu."""

    print("1. Register")
    print("2. Login")
    print("3. Delete User")
    print("4. List Users")

    choice = input("Enter choice: ").strip()

    if choice == '1':
        username = input("Choose a username: ").strip()
        password = input("Choose a password: ").strip()

        if register_user(username, password):
            print(f"[+] User '{username}' registered successfully.")
        else:
            print("[!] Username already exists.")

    elif choice == '2':
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if login_user(username, password):
            print(f"[+] Login successful. Welcome, {username}!")
        else:
            print("[!] Invalid username or password.")

    elif choice == '3':
        username = input("Username to delete: ").strip()

        if delete_user(username):
            print(f"[+] User '{username}' deleted.")
        else:
            print("[!] User not found.")

    elif choice == '4':
        users = list_users()
        if users:
            print("[+] Registered users:")
            for u in users:
                print(f"    - {u}")
        else:
            print("[!] No users registered yet.")

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()