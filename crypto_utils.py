import os
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = "data/secret.key"


def generate_key() -> None:
    """Generate a new encryption key and save it to file (run once)."""

    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)

    if os.path.exists(KEY_FILE):
        print("[!] Key already exists. Skipping generation.")
        return

    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

    print(f"[+] Key generated and saved to '{KEY_FILE}'")


def load_key() -> bytes:
    """Load the encryption key from file."""

    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError(
            "Encryption key not found. Run generate_key() first."
        )

    with open(KEY_FILE, "rb") as f:
        return f.read()


def encrypt_data(text: str) -> str:
    """Encrypt a string and return the encrypted token as a string."""

    key = load_key()
    fernet = Fernet(key)
    token = fernet.encrypt(text.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_data(token: str) -> str:
    """Decrypt an encrypted token back into the original string."""

    key = load_key()
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(token.encode('utf-8'))
        return decrypted.decode('utf-8')
    except InvalidToken:
        raise ValueError("Invalid or corrupted data. Cannot decrypt.")


def main():
    """Main menu."""

    print("1. Generate Encryption Key (run once)")
    print("2. Encrypt Text")
    print("3. Decrypt Text")

    choice = input("Enter choice: ").strip()

    if choice == '1':
        generate_key()

    elif choice == '2':
        text = input("Enter text to encrypt: ").strip()
        try:
            token = encrypt_data(text)
            print(f"[+] Encrypted: {token}")
        except FileNotFoundError as e:
            print(f"[!] Error: {e}")

    elif choice == '3':
        token = input("Enter encrypted text: ").strip()
        try:
            original = decrypt_data(token)
            print(f"[+] Decrypted: {original}")
        except (FileNotFoundError, ValueError) as e:
            print(f"[!] Error: {e}")

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()