import pretty_midi
from drums_bass import generate_drums, generate_bass
from style_library import DRUM_STYLE_CONFIGS

print('=== Diagnostic Test: Drum Velocities ===')

pm = pretty_midi.PrettyMIDI()
spec = {
    'identity': {'style': 'trap', 'key': 'C_minor'},
    'time': {'bpm': 140},
    'style_params': {'drum_density': 0.8}
}
section = {'type': 'verse', 'bars': 2, 'intensity': 0.7}

end_time, kicks = generate_drums(pm, spec, section, 0)

if pm.instruments and pm.instruments[0].notes:
    inst = pm.instruments[0]
    print(f'Total drum notes: {len(inst.notes)}')
    velocities = [n.velocity for n in inst.notes]
    print(f'Min velocity: {min(velocities)}')
    print(f'Max velocity: {max(velocities)}')
    print(f'Avg velocity: {sum(velocities)/len(velocities):.1f}')
    
    # Count by type
    kicks = [n for n in inst.notes if n.pitch == 36]
    snares = [n for n in inst.notes if n.pitch == 38]
    hihats = [n for n in inst.notes if n.pitch == 42]
    
    if kicks:
        print(f'Kick notes: {len(kicks)}, avg vel: {sum(n.velocity for n in kicks)/len(kicks):.1f}')
    if snares:
        print(f'Snare notes: {len(snares)}, avg vel: {sum(n.velocity for n in snares)/len(snares):.1f}')
    if hihats:
        print(f'Hihat notes: {len(hihats)}, avg vel: {sum(n.velocity for n in hihats)/len(hihats):.1f}')
else:
    print('NO DRUM NOTES GENERATED!')
    config = DRUM_STYLE_CONFIGS.get('trap', {})
    print(f'Available patterns: {list(config.get("patterns", {}).keys())}')
    print(f'Velocities config: {config.get("velocities", {})}')