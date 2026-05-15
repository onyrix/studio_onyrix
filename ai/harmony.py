from music21 import converter
from music21 import chord


# ----------------------------
# TIMELINE CHORD EXTRACTION
# ----------------------------
def extract_chord_timeline(midi_path):

    try:
        score = converter.parse(midi_path)

        chordified = score.chordify()

        timeline = []

        for element in chordified.flat.notes:

            if isinstance(element, chord.Chord):

                try:
                    root = element.root()

                    if root is None:
                        continue

                    offset = float(element.offset)

                    chord_name = root.name

                    timeline.append({
                        "time": offset,
                        "chord": chord_name
                    })

                except Exception:
                    continue

        # remove duplicates
        cleaned = []

        prev = None

        for item in timeline:

            if item["chord"] != prev:

                cleaned.append(item)

                prev = item["chord"]

        return cleaned

    except Exception as e:
        print(f"❌ Harmony extraction failed: {midi_path}")
        print(e)

        return []