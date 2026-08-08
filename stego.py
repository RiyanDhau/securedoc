from PIL import Image

DELIMITER = '11111110'


def to_binary(message: str) -> str:
    """Convert string message to binary."""
    return ''.join(format(ord(char), '08b') for char in message)


def encode_image(image_path: str, secret_message: str) -> None:
    """Encode a secret message into an image."""
    
    # Open and ensure RGB format
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary_msg = to_binary(secret_message) + DELIMITER
    max_capacity = len(pixels) * 3

    # Check capacity
    if len(binary_msg) > max_capacity:
        raise ValueError("Message too large for this image.")

    new_pixels = []
    data_index = 0

    for r, g, b in pixels:
        if data_index < len(binary_msg):
            r = (r & ~1) | int(binary_msg[data_index])
            data_index += 1

        if data_index < len(binary_msg):
            g = (g & ~1) | int(binary_msg[data_index])
            data_index += 1

        if data_index < len(binary_msg):
            b = (b & ~1) | int(binary_msg[data_index])
            data_index += 1

        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save("encoded.png")

    print("[+] Message successfully encoded into 'encoded.png'")


 


def decode_image(image_path: str) -> None:
    """Decode a hidden message from an image."""

    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary_data = ""

    for r, g, b in pixels:
        binary_data += str(r & 1)
        binary_data += str(g & 1)
        binary_data += str(b & 1)

    bytes_list = [
        binary_data[i:i + 8]
        for i in range(0, len(binary_data), 8)
    ]

    message = ""

    for byte in bytes_list:
        if byte == DELIMITER:
            break
        message += chr(int(byte, 2))

    print("[+] Hidden message:", message)


def main():
    """Main menu."""
    
    print("1. Encode")
    print("2. Decode")

    choice = input("Enter choice: ").strip()

    if choice == '1':
        img_path = input("Enter image path: ").strip()
        message = input("Enter secret message: ").strip()
        encode_image(img_path, message)

    elif choice == '2':
        img_path = input("Enter encoded image path: ").strip()
        decode_image(img_path)

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()