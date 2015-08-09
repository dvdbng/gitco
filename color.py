import curses

DEFAULT_FOREGROUND = curses.COLOR_WHITE
DEFAULT_BACKGROUND = curses.COLOR_BLACK
COLOR_PAIRS = {10: 0}

def get_color(fg, bg):
    """Returns the curses color pair for the given fg/bg combination."""
    key = (fg, bg)
    if key not in COLOR_PAIRS:
        size = len(COLOR_PAIRS)
        try:
            curses.init_pair(size, fg, bg)
        except:
            # If curses.use_default_colors() failed during the initialization
            # of curses, then using -1 as fg or bg will fail as well, which
            # we need to handle with fallback-defaults:
            if fg == -1:  # -1 is the "default" color
                fg = DEFAULT_FOREGROUND
            if bg == -1:  # -1 is the "default" color
                bg = DEFAULT_BACKGROUND
            curses.init_pair(size, fg, bg)
        COLOR_PAIRS[key] = size

    return COLOR_PAIRS[key]

