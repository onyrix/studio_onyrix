import pretty_midi
import soundfile as sf

def render_to_audio(pm, filename="output/output.wav"):
    audio = pm.synthesize()
    sf.write(filename, audio, 44100)