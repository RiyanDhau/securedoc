import hashlib
import random
import string


def check_strength(password: str) -> tuple[str, list[str]]:
    """Check password strength and return rating + list of missing criteria."""

    criteria = {
        "At least 8 characters": len(password) >= 8,
        "Contains uppercase letter": any(c.isupper() for c in password),
        "Contains lowercase letter": any(c.islower() for c in password),
        "Contains digit": any(c.isdigit() for c in password),
        "Contains special character": any(c in string.punctuation for c in password),
    }

    score = sum(criteria.values())
    missing = [rule for rule, passed in criteria.items() if not passed]

    if score <= 2:
        rating = "Weak"
    elif score <= 4:
        rating = "Moderate"
    else:
        rating = "Strong"

    return rating, missing


def generate_password(length: int = 12) -> str:
    """Generate a random strong password of given length."""

    if length < 4:
        raise ValueError("Password length should be at least 4.")

    # Ensure at least one of each character type
    pool = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    all_chars = string.ascii_letters + string.digits + string.punctuation
    pool += [random.choice(all_chars) for _ in range(length - len(pool))]

    random.shuffle(pool)
    return ''.join(pool)


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Generate a hash of the given text using the specified algorithm."""

    algorithms = {
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "md5": hashlib.md5,
    }

    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm. Choose from: {list(algorithms.keys())}")

    hasher = algorithms[algorithm]()
    hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with a salt using PBKDF2 (for secure storage)."""

    if salt is None:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )

    return hashed.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify a password against its stored hash and salt."""

    new_hash, _ = hash_password(password, salt)
    return new_hash == stored_hash


def main():
    """Main menu."""

    print("1. Check Password Strength")
    print("2. Generate Strong Password")
    print("3. Generate Hash of Text")

    choice = input("Enter choice: ").strip()

    if choice == '1':
        pwd = input("Enter password to check: ").strip()
        rating, missing = check_strength(pwd)
        print(f"[+] Strength: {rating}")
        if missing:
            print("[!] Missing:")
            for item in missing:
                print(f"    - {item}")

    elif choice == '2':
        try:
            length = int(input("Enter desired length (default 12): ").strip() or 12)
            pwd = generate_password(length)
            print(f"[+] Generated password: {pwd}")
        except ValueError as e:
            print(f"[!] Error: {e}")

    elif choice == '3':
        text = input("Enter text to hash: ").strip()
        algo = input("Algorithm (sha256/sha512/md5) [default sha256]: ").strip() or "sha256"
        try:
            result = hash_text(text, algo)
            print(f"[+] {algo.upper()} hash: {result}")
        except ValueError as e:
            print(f"[!] Error: {e}")

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()