from PIL import Image

DELIMITER = '11111110'


def to_binary(message: str) -> str:
    """Convert string message to binary using UTF-8 byte encoding.

    Using UTF-8 bytes (instead of ord() per character) guarantees every
    unit is exactly 8 bits, even for special characters like curly quotes
    ('), em-dashes (\u2014), or accented letters, which have Unicode code
    points above 255 and would otherwise break the fixed 8-bit alignment
    this scheme depends on.
    """
    data = message.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in data)


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

    byte_values = bytearray()

    for byte in bytes_list:
        if byte == DELIMITER:
            break
        byte_values.append(int(byte, 2))

    # Decode the collected UTF-8 bytes back into a proper string.
    # errors='replace' avoids a crash if the image was corrupted/altered
    # and the byte stream isn't valid UTF-8 at some point.
    message = byte_values.decode('utf-8', errors='replace')

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