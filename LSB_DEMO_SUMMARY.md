# LSB Steganography Demo - Complete Results

## The Demonstration

We hid the message **"Hello"** in a 10x10 pixel image to show exactly how LSB steganography works.

---

## Step 1: Message to Binary Conversion

```
Message: "Hello"
Characters:
  'H' (ASCII  72) -> 01001000
  'e' (ASCII 101) -> 01100101
  'l' (ASCII 108) -> 01101100
  'l' (ASCII 108) -> 01101100
  'o' (ASCII 111) -> 01101111

Full binary: 0100100001100101011011000110110001101111
Delimiter:  11111110
Total bits: 48 bits
Pixels needed: 17 pixels (3 bits per pixel)
```

---

## Step 2: How Bits Are Distributed Across Pixels

Each pixel has 3 color channels: Red, Green, Blue
Each channel stores 1 bit in its LSB (Least Significant Bit)

```
Pixel 1: 010 -> R LSB=0, G LSB=1, B LSB=0
Pixel 2: 010 -> R LSB=0, G LSB=1, B LSB=0
Pixel 3: 000 -> R LSB=0, G LSB=0, B LSB=0
... (continues for 17 pixels)
```

---

## Step 3: LSB Modification at Bit Level

**How the bitwise operation works:**

### Hide bit 0:
```
Original: 218 = 11011010
Step 1: 218 & 254 = 11011010 (clear LSB)
Step 2: 11011010 | 0 = 11011010 = 218
Result: 218 -> 218 (NO visible change!)
```

### Hide bit 1:
```
Original: 218 = 11011010
Step 1: 218 & 254 = 11011010 (clear LSB)
Step 2: 11011010 | 1 = 11011011 = 219
Result: 218 -> 219 (change of +1, imperceptible!)
```

---

## Step 4: Before and After Pixel Comparison

### ORIGINAL IMAGE - First 15 Pixels:
```
Pixel #    R        G        B        LSBs
0          0        0        0        000
1          25       0        12       100
2          50       0        24       000
3          75       0        36       100
4          100      0        48       000
5          125      0        60       100
6          150      0        72       000
7          175      0        84       100
8          200      0        96       000
9          225      0        108      100
10         0        25       12       010
11         25       25       24       110
12         50       25       36       010
13         75       25       48       110
14         100      25       60       010
```

### ENCODED IMAGE - Same Pixels After Hiding "Hello":
```
Pixel #    R        G        B        LSBs
0          0        1        0        010 <- CHANGED (message bit)
1          24       1        12       010 <- CHANGED (message bit)
2          50       0        24       000 (no message bit here)
3          75       1        36       110 <- CHANGED
4          100      1        48       010 <- CHANGED
5          125      0        61       101 <- CHANGED
6          151      0        73       101 <- CHANGED
7          175      0        84       100 (no message bit here)
8          200      1        97       011 <- CHANGED
9          224      1        109      011 <- CHANGED
10         0        24       12       000 <- CHANGED
11         25       25       24       110 (no message bit here)
12         51      25       37       111 <- CHANGED
13         75      25       49       111 <- CHANGED
14         101      25       61       111 <- CHANGED
```

---

## Step 5: Pixel Change Analysis

### Comparison Results:

```
Total pixels changed: 12 out of 15
Changed by LSB only: 12 (ALL changes are imperceptible!)

Example changes:
  Pixel 0: (0, 0, 0) -> (0, 1, 0)     [only G LSB changed by 1]
  Pixel 1: (25, 0, 12) -> (24, 1, 12) [R LSB changed by 1, G LSB changed by 1]
  Pixel 6: (150, 0, 72) -> (151, 0, 73) [R and B LSB changed by 1 each]

Max pixel difference: 1
Average difference: 0.0633 per channel
```

**KEY FINDING:** All changes are **±1 in color value**, which is **INVISIBLE** to the human eye!

---

## Step 6: Message Recovery

When decoding, we extract the LSB from each pixel's RGB channels:

```python
for r, g, b in pixels:
    binary_data += str(r & 1)    # Extract LSB from R
    binary_data += str(g & 1)    # Extract LSB from G
    binary_data += str(b & 1)    # Extract LSB from B
```

**Result:** [+] Hidden message: **Hello** ✓

The message was perfectly recovered!

---

## Why This Works So Well

### 1. **Imperceptible Changes**
- Color values change by only ±1
- Human eyes cannot detect this minimal difference
- Original image and encoded image appear identical

### 2. **Large Capacity**
- 1000×1000 pixel image = 1,000,000 pixels = 3,000,000 bits = **375,000 characters**
- You can hide a small novel in a single photo!

### 3. **Reversible Process**
- LSB can be perfectly recovered
- No data loss
- Deterministic extraction (same result every time)

---

## The Answer to Your Teacher

**Q: Where does the hidden data get stored in the image?**

**A:** The data is hidden in the **Least Significant Bit (LSB)** of each pixel's Red, Green, and Blue color channels. Here's the proof:

1. **Location:** The rightmost bit (bit 0) of each color value
   - Red LSB, Green LSB, Blue LSB = 3 bits per pixel

2. **How we found it:** Compare original and encoded RGB values
   - Original Pixel 0: RGB (0, 0, 0)
   - Encoded Pixel 0: RGB (0, 1, 0)
   - Only the Green LSB changed by 1 (imperceptible!)

3. **Why it works:** 
   - Changing LSB = ±1 change in color value
   - Human vision cannot detect ±1 color changes
   - But we can extract it perfectly using bitwise operations

4. **Proof of extraction:**
   - Extract LSBs: (0, 1, 0) = binary "010"
   - Do this for all message pixels
   - Reconstruct original message: "Hello" ✓

---

## Visual Analogy

Imagine a book with **black text on white paper**:
- Each letter is written in normal black ink (visible)
- But underneath each letter, we write with a **very, very light pencil** (the LSB)
- The light pencil marks are so faint that you can't see them
- But if you use a special technique (a UV light = bitwise AND operation), you can read the pencil marks perfectly!

That's exactly what LSB steganography does with pixel color values.

---

## Files Generated

- `demo_original.png` - Original 10×10 test image
- `encoded.png` - Same image with "Hello" hidden in LSBs
- `stego_demo.py` - Full Python script demonstrating the technique

Both images look identical to the naked eye, but one contains hidden data!
