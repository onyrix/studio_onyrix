class MidiEvent:
    def __init__(self, type, note=None, velocity=0, time=0, channel=0):
        self.type = type
        self.note = note
        self.velocity = velocity
        self.time = time
        self.channel = channel