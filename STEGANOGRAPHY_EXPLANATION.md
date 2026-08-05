# Steganography Explanation - Where Does Hidden Data Get Stored?

## Overview
Your SecureDoc project uses **LSB (Least Significant Bit) Steganography** to hide messages inside images.

---

## Technical Details: How It Works

### 1. **Where Data Is Hidden: The Least Significant Bit (LSB)**

In LSB steganography, the message is stored in the **least significant bit** of each pixel's color channel.

**Example:**
- A pixel has RGB values: `(218, 145, 67)`
- In binary:
  - Red: `11011010`
  - Green: `10010001`
  - Blue: `01000011`

The **last bit** (rightmost, least significant) of each channel is modified:
- Red LSB: `0` (can be changed to `0` or `1`)
- Green LSB: `1` (can be changed to `0` or `1`)
- Blue LSB: `1` (can be changed to `0` or `1`)

### 2. **Why LSB?**

Human eyes **cannot** detect LSB changes because:
- Changing the LSB only changes the color value by **±1**
- Example: `218` → `219` (imperceptible to human vision)
- The pixel remains visually identical

### 3. **Step-by-Step Encoding Process** (from your `stego.py`):

```python
# STEP 1: Convert message to binary
Message: "Hi"
Binary:  "01001000" (H) + "01101001" (i)
         = "0100100001101001"

# STEP 2: Add delimiter to mark end of data
DELIMITER = "11111110"
Full binary: "010010000110100111111110"

# STEP 3: Hide in pixels using LSB
Pixel 1: (218, 145, 67)
├─ Replace LSB of R (bit 0 of message): 11011010 → 11011010 (0)
├─ Replace LSB of G (bit 1 of message): 10010001 → 10010000 (1)
└─ Replace LSB of B (bit 2 of message): 01000011 → 01000011 (0)

Result: (218, 145, 66) or (218, 144, 67) etc.

Pixel 2: (100, 200, 150)
├─ Replace LSB of R: 01100100 → 01100101 (0)
├─ Replace LSB of G: 11001000 → 11001000 (1)
└─ Replace LSB of B: 10010110 → 10010111 (1)

Result: (101, 200, 151) or similar
```

---

## Code Breakdown

### **Encoding (Hiding Data)**
```python
def encode_image(image_path: str, secret_message: str):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())
    
    binary_msg = to_binary(secret_message) + DELIMITER
    
    for r, g, b in pixels:
        if data_index < len(binary_msg):
            # Line: r = (r & ~1) | int(binary_msg[data_index])
            # This modifies ONLY the LSB (least significant bit)
            r = (r & ~1) | int(binary_msg[data_index])  # ← LSB manipulation
            data_index += 1
```

**How `r = (r & ~1) | int(binary_msg[data_index])` works:**
1. `r & ~1` → Clears the LSB (sets it to 0)
2. `| int(binary_msg[data_index])` → Sets LSB to 0 or 1 based on message bit

**Example:**
```
Original: r = 218 = 11011010 (binary)
~1 = 11111110 (flip all bits in 1)
r & ~1 = 11011010 & 11111110 = 11011010 (LSB now 0)
int(binary_msg[data_index]) = 1
11011010 | 00000001 = 11011011 (LSB now 1)
Result: r = 219
```

### **Decoding (Extracting Data)**
```python
def decode_image(image_path: str):
    for r, g, b in pixels:
        binary_data += str(r & 1)    # Extract LSB from R
        binary_data += str(g & 1)    # Extract LSB from G
        binary_data += str(b & 1)    # Extract LSB from B
```

**How `r & 1` works:**
- `r = 219 = 11011011` (binary)
- `1 = 00000001` (binary)
- `11011011 & 00000001 = 00000001 = 1`
- Returns the LSB value

---

## Capacity Calculation

Your code stores data in **3 bits per pixel** (R, G, B channels):

```
1 Pixel = 3 bits of data
Image with 1000 pixels = 3000 bits = 375 bytes
```

**For example:**
- 100×100 pixel image = 10,000 pixels = 30,000 bits = **3,750 characters**
- 1000×1000 pixel image = 1,000,000 pixels = 3,000,000 bits = **375,000 characters**

---

## Visual Example

### Before Encoding:
```
Original Image Pixel RGB values (visible to naked eye)
Pixel colors look perfectly normal
```

### After Encoding:
```
Modified Image Pixel RGB values (LSB changed)
- R: 218 → 219 (imperceptible)
- G: 145 → 144 (imperceptible)
- B: 67 → 66 (imperceptible)

Human eyes see NO difference! ✓
```

---

## Delimiter Purpose

Your code uses `DELIMITER = '11111110'` to mark where hidden data ends:

```python
binary_msg = to_binary(secret_message) + DELIMITER
```

When decoding, it stops at the delimiter:
```python
for byte in bytes_list:
    if byte == DELIMITER:
        break  # ← Stops reading here
    message += chr(int(byte, 2))
```

---

## Security Note

⚠️ **LSB steganography is NOT secure against analysis**, but it's perfect for:
- Hiding data in plain sight (no encryption needed initially)
- Combining with encryption (your SecureDoc does this!)
- Learning steganography concepts

For true security, your project **encrypts the message BEFORE hiding it** using Fernet encryption!

---

## Summary for Your Teacher

**Answer:** The hidden data is stored in the **Least Significant Bits (LSB)** of each pixel's RGB color channels:
- **Where:** Last bit of Red, Green, and Blue values
- **How:** By modifying only the LSB (±1 change), the image looks identical
- **Capacity:** 3 bits per pixel (0.375 bytes per pixel)
- **Extraction:** Read LSB from each RGB channel to reconstruct the original message

