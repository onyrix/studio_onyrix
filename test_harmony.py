from ai.harmony import extract_chords

chords = extract_chords("input.mid")

print("\n🎹 Extracted chords:\n")

for c in chords:
    print(c)