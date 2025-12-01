#!/usr/bin/env python3
# Test script to see what input() captures

print("Type something, backspace, correct it, then press Enter:")
ans = input("Test: ").strip()

print(f"\nYou entered: '{ans}'")
print(f"Length: {len(ans)}")
print(f"Repr: {repr(ans)}")
print(f"Bytes: {ans.encode('utf-8')}")

# Show each character
print("\nCharacter breakdown:")
for i, char in enumerate(ans):
    print(f"  [{i}] '{char}' (Unicode: U+{ord(char):04X}, code: {ord(char)})")
