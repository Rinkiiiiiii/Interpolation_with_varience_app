import numpy as np


def get_hardcoded_values():
    """Returns a pair of (x_points, y_points) for demo purposes."""
    return [0, 1, 2, 3, 4], [5, 10, 15, 20, 7]


def process(values):
    """Return (x_out, y_out) suitable for plotting.
    If `values` is provided it will interpolate across indices 0..n-1.
    Otherwise it will return an interpolation of the hardcoded demo points.
    """
    if values:
        n = len(values)
        x_out = np.linspace(0, n - 1, 200)
        y_out = np.interp(x_out, np.arange(n), np.array(values))
        return get_hardcoded_values()
    else:
        x_pts, y_pts = get_hardcoded_values()
        x_out = np.linspace(min(x_pts), max(x_pts), 200)
        y_out = np.interp(x_out, x_pts, y_pts)
        return get_hardcoded_values()


if __name__ == "__main__":
    process()