import base64
import io
import os
import sys
import wave

# Test decoding a base64 string with data URL prefix
test_data = "data:audio/wav;base64,ZHVtbXkgYXVkaW8gZGF0YQ=="
print("Test data:", test_data)

# Extract base64 part after the prefix
if "base64," in test_data:
    base64_data = test_data.split("base64,")[1]
    print("Extracted base64:", base64_data)

    # Decode base64
    decoded = base64.b64decode(base64_data)
    print("Decoded data:", decoded)
else:
    print("No base64 prefix found")

print("\nChecking app.py audio_chunk handling...")
# Simulate what happens in app.py
test_chunk = {"audio_chunk": "ZHVtbXkgYXVkaW8gZGF0YQ=="}
decoded = base64.b64decode(test_chunk["audio_chunk"])
print("Decoded chunk:", decoded)
