import pretty_midi

from utils import get_scale_notes
from drums_bass import generate_drums, generate_bass
from harmonic_engine import generate_chords
from melody_engine import generate_melody
from global_memory import MotifMemory
from audio_render import render_to_audio
from style_engine import build_spec_from_style, get_style_list


def generate_track(spec):
    """
    Generate a MIDI track from a specification.
    
    Args:
        spec: Dictionary containing identity, time, chaos, arrangement, and style_params
    
    Returns:
        pretty_midi.PrettyMIDI: Generated MIDI object
    """
    pm = pretty_midi.PrettyMIDI()
    t = 0

    scale = get_scale_notes(
        spec["identity"]["key"],
        spec["identity"].get("scale_type", "natural_minor")
    )

    memory = MotifMemory(scale)

    for section in spec["arrangement"]["sections"]:
        t, kicks = generate_drums(pm, spec, section, t)

        generate_bass(pm, spec, section, t, kicks)
        generate_chords(pm, spec, section, t)

        motif = memory.evolve(
            spec["chaos"]["level"],
            section["type"]
        )

        generate_melody(pm, spec, section, t, kicks, motif)

    return pm


def generate_track_with_style(style_name, key="C_minor", chaos=0.3, custom_arrangement=None):
    """
    Generate a MIDI track in a specific style.
    
    Args:
        style_name: Name of the style from STYLE_LIBRARY
        key: Musical key (e.g., "C_minor", "D_major")
        chaos: Chaos/variation level (0.0-1.0)
        custom_arrangement: Optional custom arrangement to override style template
    
    Returns:
        pretty_midi.PrettyMIDI: Generated MIDI object
    """
    spec = build_spec_from_style(style_name, key, chaos, custom_arrangement)
    return generate_track(spec)


def list_available_styles():
    """Print all available music styles."""
    styles = get_style_list()
    print("\n=== Available Music Styles ===")
    for style in styles:
        print(f"  - {style}")
    print(f"\nTotal: {len(styles)} styles")
    return styles


if __name__ == "__main__":
    import sys
    
    # Default values
    style = "trap"
    key = "F_minor"
    chaos = 0.3
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        style = sys.argv[1]
    if len(sys.argv) > 2:
        key = sys.argv[2]
    if len(sys.argv) > 3:
        chaos = float(sys.argv[3])
    
    # List available styles if requested
    if style == "--list" or style == "-l":
        list_available_styles()
        sys.exit(0)
    
    print(f"\n=== Generating {style} track ===")
    print(f"Key: {key}")
    print(f"Chaos: {chaos}")
    
    # Generate using style
    try:
        pm = generate_track_with_style(style, key, chaos)
        
        # Save MIDI
        output_midi = f"output/{style}_{key}.mid"
        pm.write(output_midi)
        print(f"\nMIDI saved to: {output_midi}")
        
        # Render to audio
        output_wav = f"output/{style}_{key}.wav"
        render_to_audio(pm, output_wav)
        print(f"Audio saved to: {output_wav}")
        
    except ValueError as e:
        print(f"\nError: {e}")
        print("\nAvailable styles:")
        for s in get_style_list():
            print(f"  - {s}")

    # Example: Generate tracks in different styles
    print("\n" + "="*50)
    print("Example: Generating sample tracks in different styles...")
    print("="*50)
    
    # Uncomment below to generate multiple style examples
    """
    example_styles = ["trap", "lofi", "techno", "jazz"]
    for style_name in example_styles:
        print(f"\nGenerating {style_name}...")
        pm = generate_track_with_style(style_name, "C_minor", 0.2)
        pm.write(f"output/{style_name}_demo.mid")
        render_to_audio(pm, f"output/{style_name}_demo.wav")
        print(f"  -> {style_name}_demo.mid / .wav")
    """