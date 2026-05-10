"""
Style Tests for Studio Onyrix v4 DAW
Tests: Synthwave, Chillout, Darksynth, Rock
"""
import sys, os, time

# Add the repo root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daw_engine import DAWProject, DAWPart, DAWPartGenerator, DAWMixer

# Style test configurations
STYLE_TESTS = {
    "synthwave": {
        "name": "Synthwave Groove",
        "bpm": 100,
        "root": "A",
        "scale": "natural_minor",
        "parts": [
            {"preset": "bass", "bpm": 100, "root": "A", "scale": "natural_minor", "measures": 4, "relation": "verse", "temperature": 0.7, "prompt": "synthwave bass, driving arpeggio bassline"},
            {"preset": "chords", "bpm": 100, "root": "A", "scale": "natural_minor", "measures": 4, "relation": "chorus", "temperature": 0.9, "prompt": "warm analog synth chords, 80s retro wave"},
            {"preset": "arp", "bpm": 100, "root": "A", "scale": "natural_minor", "measures": 4, "relation": "verse", "temperature": 1.0, "prompt": "arpeggiated synth, retro 80s, neon"},
            {"preset": "drums", "bpm": 100, "measures": 4, "relation": "verse", "temperature": 0.7, "prompt": "synthwave drums, gated reverb snare, electronic"},
        ]
    },
    "chillout": {
        "name": "Chillout Vibes",
        "bpm": 80,
        "root": "D",
        "scale": "major",
        "parts": [
            {"preset": "bass", "bpm": 80, "root": "D", "scale": "major", "measures": 4, "relation": "verse", "temperature": 0.6, "prompt": "chillout bass, smooth, relaxed"},
            {"preset": "chords", "bpm": 80, "root": "D", "scale": "major", "measures": 4, "relation": "chorus", "temperature": 0.8, "prompt": "soft piano chords, ambient, chill, relaxing"},
            {"preset": "drums", "bpm": 80, "measures": 4, "relation": "verse", "temperature": 0.6, "prompt": "lo-fi drums, soft, chill, relaxed groove"},
        ]
    },
    "darksynth": {
        "name": "Darksynth",
        "bpm": 130,
        "root": "D",
        "scale": "phrygian",
        "parts": [
            {"preset": "bass", "bpm": 130, "root": "D", "scale": "phrygian", "measures": 4, "relation": "verse", "temperature": 0.9, "prompt": "dark synth bass, aggressive, distorted, industrial"},
            {"preset": "drums", "bpm": 130, "measures": 4, "relation": "verse", "temperature": 0.8, "prompt": "dark techno drums, heavy kick, industrial percussion"},
            {"preset": "arp", "bpm": 130, "root": "D", "scale": "phrygian", "measures": 4, "relation": "chorus", "temperature": 1.1, "prompt": "dark synth arpeggio, minor, aggressive, horror"},
        ]
    },
    "rock": {
        "name": "Rock Anthem",
        "bpm": 120,
        "root": "E",
        "scale": "major",
        "parts": [
            {"preset": "bass", "bpm": 120, "root": "E", "scale": "major", "measures": 4, "relation": "verse", "temperature": 0.7, "prompt": "rock bass guitar, driving, distorted, energetic"},
            {"preset": "drums", "bpm": 120, "measures": 4, "relation": "verse", "temperature": 0.8, "prompt": "rock drums, powerful, driving beat, energetic"},
            {"preset": "chords", "bpm": 120, "root": "E", "scale": "major", "measures": 4, "relation": "chorus", "temperature": 0.9, "prompt": "rock power chords, distorted guitar, energetic"},
        ]
    }
}


def run_style_test(style_name: str, config: dict, generator: DAWPartGenerator) -> dict:
    """Run a full style test."""
    print(f"\n{'='*70}")
    print(f"  TESTING: {style_name.upper()} - {config['name']}")
    print(f"  BPM: {config['bpm']}, Key: {config['root']} {config['scale']}")
    print(f"{'='*70}")
    
    project = DAWProject(
        name=config['name'],
        bpm=config['bpm'],
        root=config['root'],
        scale=config['scale'],
    )
    
    results = []
    for i, part_cfg in enumerate(config['parts']):
        print(f"\n  --- Part {i+1}/{len(config['parts'])}: {part_cfg['preset']} ---")
        
        # Build the part
        part = DAWPart(
            bpm=part_cfg['bpm'],
            root=part_cfg.get('root', config['root']),
            scale=part_cfg.get('scale', config['scale']),
            measures=part_cfg['measures'],
            instrument=part_cfg['instrument'] if 'instrument' in part_cfg else {
                'bass': 'synth_bass',
                'drums': 'drums_full',
                'chords': 'synth_pad',
                'arp': 'pluck_arp',
                'melody': 'synth_lead',
            }.get(part_cfg['preset'], 'synth_pad'),
            instrument_class={
                'bass': 'bass',
                'drums': 'drums',
                'chords': 'pad',
                'arp': 'arpeggio',
                'melody': 'lead',
            }.get(part_cfg['preset'], 'pad'),
            relation=part_cfg['relation'],
            temperature=part_cfg.get('temperature', 1.0),
            extra_prompt=part_cfg.get('prompt', ''),
        )
        
        project.add_part(part)
        
        # Generate
        start = time.time()
        result = generator.generate_part(part, output_dir=f"output/{style_name}")
        elapsed = time.time() - start
        
        if result['success']:
            res = {
                'preset': part_cfg['preset'],
                'duration': part.duration,
                'analysis': result['analysis'],
                'elapsed': elapsed,
                'audio_path': result['path'],
            }
            results.append(res)
            print(f"  ✓ {part_cfg['preset']} - {part.duration:.1f}s - {elapsed:.0f}s generation time")
            if 'tempo' in result.get('analysis', {}):
                print(f"    Tempo: {result['analysis']['tempo']:.0f} BPM (requested: {part_cfg['bpm']})")
        else:
            print(f"  ✗ {part_cfg['preset']} - FAILED")
    
    # Save project
    project.save(f"output/{style_name}/project.json")
    
    return {
        'style': style_name,
        'config': config,
        'results': results,
        'project': project,
    }


def print_summary(all_results: dict):
    """Print test summary."""
    print(f"\n\n{'='*70}")
    print("  STYLE TEST SUMMARY")
    print(f"{'='*70}")
    
    for style_name, result in all_results.items():
        print(f"\n  [{style_name.upper()}]")
        config = result['config']
        print(f"    BPM: {config['bpm']}, Key: {config['root']} {config['scale']}")
        
        for r in result['results']:
            bpm_match = ""
            if 'tempo' in r.get('analysis', {}):
                detected = r['analysis']['tempo']
                ratio = detected / config['bpm']
                if 0.8 <= ratio <= 1.2:
                    bpm_match = "✓ BPM match"
                else:
                    bpm_match = f"⚠ BPM diff: {detected:.0f} vs {config['bpm']} requested"
            
            aud = os.path.basename(r['audio_path']) if r['audio_path'] else "N/A"
            print(f"    {r['preset']:<12s} {r['duration']:5.1f}s  {r['elapsed']:4.0f}s gen  {bpm_match:<25s} {aud}")


if __name__ == "__main__":
    import time
    
    print(f"Studio Onyrix v4 - Style Tests")
    print(f"Testing: Synthwave, Chillout, Darksynth, Rock")
    
    # Initialize generator (once, reused)
    generator = DAWPartGenerator(model_size='small')
    
    if not generator.musicgen.available:
        print("MusicGen not available. Cannot run tests.")
        sys.exit(1)
    
    all_results = {}
    
    for style_name, config in STYLE_TESTS.items():
        result = run_style_test(style_name, config, generator)
        all_results[style_name] = result
    
    print_summary(all_results)
    
    print(f"\n\nTests complete! Output in output/ subdirectories.")