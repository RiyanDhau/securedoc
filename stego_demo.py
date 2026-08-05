"""
Steganography Demo - Shows Before/After Pixel Values
Demonstrates where data gets hidden in images using LSB technique
"""

from PIL import Image


def to_binary(message: str) -> str:
    """Convert string message to binary."""
    return ''.join(format(ord(char), '08b') for char in message)


def create_demo_image():
    """Create a simple test image for demonstration."""
    # Create a 10x10 image with gradient colors
    width, height = 10, 10
    pixels = []
    
    for y in range(height):
        for x in range(width):
            r = (x * 25) % 256
            g = (y * 25) % 256
            b = ((x + y) * 12) % 256
            pixels.append((r, g, b))
    
    img = Image.new('RGB', (width, height))
    img.putdata(pixels)
    img.save("demo_original.png")
    print("[+] Demo image created: demo_original.png")
    return img


def show_pixel_values(image_path: str, num_pixels: int = 10, title: str = ""):
    """Display pixel RGB values from an image."""
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())
    
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"{'Pixel #':<10} {'R':<8} {'G':<8} {'B':<8} {'Binary (LSBs)':<20}")
    print(f"{'-'*70}")
    
    for i in range(min(num_pixels, len(pixels))):
        r, g, b = pixels[i]
        r_lsb = r & 1
        g_lsb = g & 1
        b_lsb = b & 1
        lsb_binary = f"{r_lsb}{g_lsb}{b_lsb}"
        
        print(f"{i:<10} {r:<8} {g:<8} {b:<8} {lsb_binary:<20}")


def compare_pixels(original_path: str, encoded_path: str, num_pixels: int = 15):
    """Compare original and encoded image pixels side by side."""
    img_orig = Image.open(original_path).convert("RGB")
    img_enc = Image.open(encoded_path).convert("RGB")
    
    pixels_orig = list(img_orig.getdata())
    pixels_enc = list(img_enc.getdata())
    
    print(f"\n{'='*100}")
    print("PIXEL COMPARISON: Original vs Encoded")
    print(f"{'='*100}")
    print(f"{'Pixel':<8} {'Original RGB':<25} {'Encoded RGB':<25} {'Changed?':<15} {'LSB Changed':<15}")
    print(f"{'-'*100}")
    
    changes = 0
    lsb_changes = 0
    
    for i in range(min(num_pixels, len(pixels_orig))):
        r_orig, g_orig, b_orig = pixels_orig[i]
        r_enc, g_enc, b_enc = pixels_enc[i]
        
        changed = (r_orig, g_orig, b_orig) != (r_enc, g_enc, b_enc)
        
        # Check if only LSB changed
        r_diff = abs(r_orig - r_enc)
        g_diff = abs(g_orig - g_enc)
        b_diff = abs(b_orig - b_enc)
        
        lsb_only = (r_diff <= 1 and g_diff <= 1 and b_diff <= 1)
        
        if changed:
            changes += 1
            if lsb_only:
                lsb_changes += 1
        
        changed_str = "YES" if changed else "NO"
        lsb_str = "LSB Only" if lsb_only and changed else "NO"
        
        orig_rgb = f"({r_orig}, {g_orig}, {b_orig})"
        enc_rgb = f"({r_enc}, {g_enc}, {b_enc})"
        
        print(f"{i:<8} {orig_rgb:<25} {enc_rgb:<25} {changed_str:<15} {lsb_str:<15}")
    
    print(f"{'-'*100}")
    print(f"Total pixels changed: {changes}")
    print(f"Changed by LSB only: {lsb_changes}")
    print(f"Average change per channel: ±1 (imperceptible to human eye!)")


def show_binary_hiding(message: str):
    """Show how the message is converted to binary and hidden in LSBs."""
    binary = to_binary(message)
    DELIMITER = '11111110'
    full_binary = binary + DELIMITER
    
    print(f"\n{'='*70}")
    print("HOW MESSAGE IS CONVERTED TO BINARY")
    print(f"{'='*70}")
    
    print(f"\nOriginal message: '{message}'")
    print(f"Message length: {len(message)} characters")
    
    print(f"\nCharacter breakdown:")
    for char in message:
        binary_char = format(ord(char), '08b')
        print(f"  '{char}' (ASCII {ord(char):3d}) -> {binary_char}")
    
    print(f"\nFull binary string: {binary}")
    print(f"Delimiter added:   {DELIMITER}")
    print(f"Total bits needed: {len(full_binary)} bits")
    print(f"Pixels needed:     {len(full_binary) // 3 + 1} pixels (3 bits per pixel)")
    
    print(f"\n{'='*70}")
    print("HOW BITS ARE HIDDEN IN PIXEL LSBs")
    print(f"{'='*70}")
    print(f"\nBinary data: {full_binary[:24]}... (showing first 24 bits)")
    print(f"\nPixel 1: {full_binary[0:3]} -> bits placed in R(LSB), G(LSB), B(LSB)")
    print(f"  |-R LSB = {full_binary[0]}")
    print(f"  |-G LSB = {full_binary[1]}")
    print(f"  |-B LSB = {full_binary[2]}")
    
    print(f"\nPixel 2: {full_binary[3:6]} -> bits placed in R(LSB), G(LSB), B(LSB)")
    print(f"  |-R LSB = {full_binary[3]}")
    print(f"  |-G LSB = {full_binary[4]}")
    print(f"  |-B LSB = {full_binary[5]}")
    
    print(f"\nPixel 3: {full_binary[6:9]} -> bits placed in R(LSB), G(LSB), B(LSB)")
    print(f"  |-R LSB = {full_binary[6]}")
    print(f"  |-G LSB = {full_binary[7]}")
    print(f"  |-B LSB = {full_binary[8]}")
    
    print(f"\n... and so on until all bits are hidden!")


def demonstrate_lsb_modification():
    """Demonstrate how LSB modification works at the bit level."""
    print(f"\n{'='*70}")
    print("LSB MODIFICATION TECHNIQUE - BIT LEVEL DETAILS")
    print(f"{'='*70}")
    
    examples = [
        (218, 0, "Hide 0"),
        (218, 1, "Hide 1"),
        (145, 0, "Hide 0"),
        (145, 1, "Hide 1"),
    ]
    
    for value, bit, desc in examples:
        binary_orig = format(value, '08b')
        modified = (value & ~1) | int(bit)
        binary_new = format(modified, '08b')
        
        print(f"\n{desc}:")
        print(f"  Original value: {value:3d} = {binary_orig}")
        print(f"  Step 1: value & ~1 = {value:3d} & 254 = {value & ~1:3d} ({format(value & ~1, '08b')}) [Clear LSB]")
        print(f"  Step 2: result | {bit} = {value & ~1:3d} | {bit} = {modified:3d} ({binary_new}) [Set LSB to {bit}]")
        print(f"  * Change: {value} -> {modified} (imperceptible! +/-{abs(value - modified)})")


def main():
    """Run the complete steganography demo."""
    from stego import encode_image, decode_image
    
    print("\n" + "="*70)
    print("STEGANOGRAPHY DEMO - LSB HIDING TECHNIQUE")
    print("="*70)
    
    # Step 1: Show binary conversion
    secret_message = "Hello"
    show_binary_hiding(secret_message)
    
    # Step 2: Show LSB modification technique
    demonstrate_lsb_modification()
    
    # Step 3: Create and display original image
    print(f"\n{'='*70}")
    print("STEP 1: Creating original test image")
    print(f"{'='*70}")
    create_demo_image()
    show_pixel_values("demo_original.png", num_pixels=15, title="Original Image Pixel Values")
    
    # Step 4: Encode the message
    print(f"\n{'='*70}")
    print("STEP 2: Encoding message into image")
    print(f"{'='*70}")
    print(f"Hiding message: '{secret_message}'")
    encode_image("demo_original.png", secret_message)
    
    # Step 5: Show encoded image pixels
    show_pixel_values("encoded.png", num_pixels=15, title="Encoded Image Pixel Values")
    
    # Step 6: Compare original vs encoded
    compare_pixels("demo_original.png", "encoded.png", num_pixels=15)
    
    # Step 7: Decode and verify
    print(f"\n{'='*70}")
    print("STEP 3: Decoding message from encoded image")
    print(f"{'='*70}")
    decode_image("encoded.png")
    
    # Step 8: Visual analysis
    print(f"\n{'='*70}")
    print("STEP 4: VISUAL ANALYSIS")
    print(f"{'='*70}")
    img_orig = Image.open("demo_original.png")
    img_enc = Image.open("encoded.png")
    
    print("\nOriginal Image: demo_original.png")
    print("Encoded Image:  encoded.png")
    print("\n* Both images look IDENTICAL to the human eye!")
    print("* But the encoded image contains hidden data in the LSBs!")
    
    # Calculate visual difference
    pixels_orig = list(img_orig.getdata())
    pixels_enc = list(img_enc.getdata())
    
    print(f"\nPixel value differences:")
    diffs = []
    for (r1, g1, b1), (r2, g2, b2) in zip(pixels_orig, pixels_enc):
        diffs.extend([abs(r1-r2), abs(g1-g2), abs(b1-b2)])
    
    max_diff = max(diffs) if diffs else 0
    avg_diff = sum(diffs) / len(diffs) if diffs else 0
    
    print(f"  Max difference: {max_diff}")
    print(f"  Average difference: {avg_diff:.4f}")
    print(f"  All differences <= 1: {max_diff <= 1}")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("""
* Data is hidden in the LEAST SIGNIFICANT BIT (LSB) of each color channel
* Only R, G, B values change by +/-1 (imperceptible)
* Each pixel stores 3 bits (1 bit per channel)
* Message is encoded as binary and distributed across pixels
* Delimiter marks the end of the message
* No visual difference to human eyes, but data is definitely there!
    """)


if __name__ == "__main__":
    main()
