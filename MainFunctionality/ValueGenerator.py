import random
import matplotlib.pyplot as plt

#def interpolate_with_variation(start, end, steps, weight=0.7, max_variation_factor=1.5, smoothness=1):
def interpolate_with_variation(start, end, steps, weight=0.7, max_variation_factor=1.5,
                               smoothness=1, spike_prob=0.6, spike_magnitude=2.0):
    """
    Interpolate from start to end over `steps` points (inclusive) and add smooth,
    zero-mean variation so the final value is exactly `end`.

    Approach:
    - Build a linear baseline that exactly reaches `end`.
    - Generate interior noise samples (0 at endpoints) with a bias chance
      controlled by `weight` to prefer reinforcing or opposing the baseline.
    - Subtract the interior mean from the noises so their average is zero
      (this prevents drift and guarantees the baseline end stays exact).
    - Optionally smooth the noise to make transitions less sharp.

    Args:
        start (int or float): start value
        end (int or float): end value
        steps (int): total number of points including start and end (must be >= 2)
        weight (float): probability [0..1] a noise sample reinforces the baseline
        max_variation_factor (float): multiplier for maximum noise magnitude relative to |step|
        smoothness (int): smoothing window (1 = no smoothing)

    Returns:
        List[int]: list of integer values (length == steps) that start at `start` and end at `end`
    """
    if steps < 2:
        raise ValueError("`steps` must be at least 2 (start and end)")

    # Create exact linear baseline (so start + (steps-1)*step_size == end)
    step_size = (end - start) / float(steps - 1)
    baseline = [start + i * step_size for i in range(steps)]

    # Generate interior noise (endpoints remain 0 so start/end are exact)
    noises = [0.0] * steps
    for i in range(1, steps - 1):
        # IF FUCKED CHANGE THIS: Original has a 0 as the minimum here
        mag = random.uniform(max_variation_factor * abs(step_size), max_variation_factor * abs(step_size) * 2)
        # If we want to reinforce the baseline trend, use the same sign as step_size
        sign = 1 if random.random() < weight else -1
        noises[i] = sign * mag * (1 if step_size >= 0 else -1)

    # Remove the mean from the interior noises so the overall mean is zero
    if steps > 2:
        interior_mean = sum(noises[1:-1]) / float(steps - 2)
        for i in range(1, steps - 1):
            noises[i] -= interior_mean

    # Optional smoothing (simple moving average over interior points)
    if smoothness and smoothness > 1 and steps > 2:
        smoothed = noises.copy()
        half = smoothness // 2
        for i in range(1, steps - 1):
            window_start = max(1, i - half)
            window_end = min(steps - 1, i + half) + 1
            window = noises[window_start:window_end]
            smoothed[i] = sum(window) / len(window)
        noises = smoothed

    # Optional occasional spikes: add impulsive events inside the interior
    # Keep them random and re-normalize after to avoid any net drift
    if spike_prob and spike_prob > 0 and steps > 2:
        for i in range(1, steps - 1):
            if random.random() < spike_prob:
                # Random magnitude scaled with step size and optional sign
                mag = random.uniform(0.5, 1.0) * spike_magnitude * abs(step_size)
                sign = 1 if random.random() < 0.5 else -1
                noises[i] += sign * mag * (1 if step_size >= 0 else -1)

        # Re-normalize interior noises to have zero mean so endpoints stay exact
        interior_mean = sum(noises[1:-1]) / float(steps - 2)
        for i in range(1, steps - 1):
            noises[i] -= interior_mean

    # Compose final values and ensure strict start/end equality
    values = [baseline[i] + noises[i] for i in range(steps)]
    values[0] = float(start)
    values[-1] = float(end)

    # Return integer-rounded outputs (do not round internally to avoid bias)
    return [int(round(v)) for v in values]


def plot_values(values, title="Value Interpolation Graph"):
    """
    Plot a list of values as a line graph.
    
    Args:
        values: List of numeric values to plot
        title: Title for the graph (default "Value Interpolation Graph")
    """
    plt.figure(figsize=(10, 6))
    plt.plot(values, marker='o', linestyle='-', linewidth=2, markersize=4)
    plt.title(title)
    plt.xlabel("Step")
    plt.ylabel("Value")
    plt.ylim(0, 100)  # force y-axis from 0 to 100
    plt.xlim(-2,26)
    plt.grid(True, alpha=0.3)
    plt.show()


# Example usage
if __name__ == "__main__":
    # # Default example (no spikes)
    # result = interpolate_with_variation(start=65, end=55, steps=24,
    #                                     max_variation_factor=0.8, smoothness=3,
    #                                     spike_prob=0.0)
    # print("Default (no spikes):", result)
    # plot_values(result, title="Default: subtle variation")

    # Example with occasional spikes (couple of visible peaks)
    result_spiky = interpolate_with_variation(start=65, end=55, steps=24,
                                              max_variation_factor=1.5, smoothness=1,
                                              spike_prob=1, spike_magnitude=1.5)
    print("With spikes:", result_spiky)
    plot_values(result_spiky, title="With spikes: occasional peaks")

# print(random.uniform(4, 8))
# print(random.uniform(8,4))