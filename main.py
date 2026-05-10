import pretty_midi
import sys

from utils import get_scale_notes
from drums_bass import generate_drums, generate_bass
from harmonic_engine import generate_chords
from melody_engine import generate_melody
from global_memory import MotifMemory
from audio_render import render_to_audio
from style_engine import build_spec_from_style, get_style_list

# Import AI generator (optional - will work without it)
try:
    from ai_midi_generator import HybridMIDIGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI modules not available. Running in rule-based mode only.")


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


def generate_track_with_style(style_name, key="C_minor", chaos=0.3, custom_arrangement=None, use_ai=False):
    """
    Generate a MIDI track in a specific style.
    
    Args:
        style_name: Name of the style from STYLE_LIBRARY
        key: Musical key (e.g., "C_minor", "D_major")
        chaos: Chaos/variation level (0.0-1.0)
        custom_arrangement: Optional custom arrangement to override style template
        use_ai: Whether to use AI generation (if available)
    
    Returns:
        pretty_midi.PrettyMIDI: Generated MIDI object
    """
    if use_ai and AI_AVAILABLE:
        print(f"\n=== Generating with AI + Rule-Based Hybrid ===")
        generator = HybridMIDIGenerator()
        # Get BPM from style
        from style_engine import get_style_bpm
        bpm = get_style_bpm(style_name)
        # Generate hybrid track
        midi = generator.generate_hybrid(
            style=style_name,
            key=key,
            bpm=bpm,
            chaos=chaos,
            bars=16,  # Default, can be customized
            use_ai=True
        )
        return midi
    else:
        if use_ai and not AI_AVAILABLE:
            print("Warning: AI requested but not available. Using rule-based generation.")
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
    # Default values
    style = "trap"
    key = "F_minor"
    chaos = 0.3
    use_ai = False
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Check for --ai flag
    if "--ai" in args:
        use_ai = True
        args.remove("--ai")
    
    # Check for --list flag
    if "--list" in args or "-l" in args:
        list_available_styles()
        sys.exit(0)
    
    # Parse positional arguments
    if len(args) > 0:
        style = args[0]
    if len(args) > 1:
        key = args[1]
    if len(args) > 2:
        chaos = float(args[2])
    
    print(f"\n=== Generating {style} track ===")
    print(f"Key: {key}")
    print(f"Chaos: {chaos}")
    if use_ai:
        print(f"AI Mode: Enabled")
        if not AI_AVAILABLE:
            print("Warning: AI modules not installed. Install with: pip install torch midibert-remi diffmidi")
    
    # Generate using style
    try:
        pm = generate_track_with_style(style, key, chaos, use_ai=use_ai)
        
        # Create output directory if it doesn't exist
        import os
        os.makedirs("output", exist_ok=True)
        
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
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

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