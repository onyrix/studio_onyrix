def get_energy(section_type, bar_index, total_bars):
    if section_type == "build":
        return bar_index / total_bars
    elif section_type == "drop":
        return 1.0
    elif section_type == "intro":
        return 0.3 + 0.1 * bar_index
    else:
        return 0.5