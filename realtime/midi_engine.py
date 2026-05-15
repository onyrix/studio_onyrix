import rtmidi

class MidiEngine:
    def __init__(self):
        self.out = rtmidi.MidiOut()
        self.out.open_virtual_port("Onyrix AI Output")

    def send_note(self, note, velocity=100):
        self.out.send_message([0x90, note, velocity])

    def stop_note(self, note):
        self.out.send_message([0x80, note, 0])