import random

class MotifMemory:
    def __init__(self, scale):
        self.base = [random.choice(scale) for _ in range(8)]

    def evolve(self, chaos, section_type):
        new = self.base.copy()

        for i in range(len(new)):
            prob = chaos * 0.3

            if section_type == "drop":
                prob *= 0.5  # più stabile
            elif section_type == "build":
                prob *= 1.5  # più variazione

            if random.random() < prob:
                new[i] += random.choice([-1,1])

        self.base = new
        return new