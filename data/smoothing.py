import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from datetime import datetime
import csv


def peak_touch_clean(data, sigma=2.5):
    """
    Peak-touching Clean smoothing: Loose on peaks, tight on non-peaks
    Creates very smooth curves that touch all maximum values
    """
    data = np.array(data, dtype=float)
    n = len(data)
    
    # Find peak value and threshold
    peak_val = np.max(data)
    non_peak_threshold = peak_val - 1
    
    # First pass: Variable smoothing based on proximity to peak
    smooth = np.zeros(n)
    
    for i in range(n):
        weighted_sum = 0
        weight_total = 0
        
        # Adjust sigma based on whether we're near peak values
        is_near_peak = data[i] >= non_peak_threshold
        local_sigma = sigma * 1.5 if is_near_peak else sigma * 0.7
        
        for j in range(n):
            distance = abs(i - j)
            weight = np.exp(-(distance ** 2) / (2 * local_sigma ** 2))
            weighted_sum += data[j] * weight
            weight_total += weight
        
        smooth[i] = weighted_sum / weight_total
    
    # Find all peak indices
    peak_indices = np.where(data == peak_val)[0]
    
    # Second pass: Gentle lift to peaks
    for idx in peak_indices:
        if smooth[idx] < peak_val:
            lift = peak_val - smooth[idx]
            
            # Gradual approach over wider area
            for i in range(-4, 5):
                if 0 <= idx + i < n:
                    weight = np.exp(-(i ** 2) / 8)
                    target_lift = lift if i == 0 else lift * weight * 0.4
                    smooth[idx + i] += target_lift * 0.7
    
    # Third pass: Tighten non-peak areas
    for i in range(n):
        if data[i] < non_peak_threshold:
            diff = data[i] - smooth[i]
            smooth[i] += diff * 0.3
    
    # Ensure peaks are exactly touched
    for idx in peak_indices:
        smooth[idx] = peak_val
    
    # Final smoothing pass
    final_smooth = smooth.copy()
    for i in range(1, n - 1):
        if data[i] != peak_val:
            neighbors_avg = (smooth[i-1] + smooth[i+1]) / 2
            final_smooth[i] = smooth[i] * 0.7 + neighbors_avg * 0.3
    
    return final_smooth


def peak_touch_standard(data, window=7):
    """
    Peak-touching Standard smoothing: Moderate smoothing that preserves peaks
    Uses moving average with peak restoration
    """
    data = np.array(data, dtype=float)
    n = len(data)
    half = window // 2
    
    # Moving average
    smooth = np.zeros(n)
    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half + 1)
        smooth[i] = np.mean(data[start:end])
    
    # Find peak value and indices
    peak_val = np.max(data)
    peak_indices = np.where(data == peak_val)[0]
    
    # Handle multiple peaks
    if len(peak_indices) > 1:
        # Ensure smooth curve touches all peaks
        for idx in peak_indices:
            if smooth[idx] < peak_val:
                smooth[idx] = peak_val
        
        # Smooth transitions between peaks
        for i in range(len(peak_indices) - 1):
            start = peak_indices[i]
            end = peak_indices[i + 1]
            span = end - start
            
            # Keep elevation between close peaks
            if span > 1:
                for j in range(start + 1, end):
                    progress = (j - start) / span
                    min_val = peak_val - 2
                    if smooth[j] < min_val:
                        blend = 0.5 - 0.5 * np.cos(progress * np.pi)
                        smooth[j] = max(smooth[j], min_val + blend)
    else:
        # Single peak
        peak_idx = peak_indices[0]
        smooth[peak_idx] = peak_val
        
        # Blend around peak
        blend_range = 3
        for i in range(1, blend_range + 1):
            weight = 1 - (i / (blend_range + 1))
            
            if peak_idx - i >= 0:
                smooth[peak_idx - i] = smooth[peak_idx - i] * (1 - weight * 0.5) + \
                                      peak_val * weight * 0.5
            if peak_idx + i < n:
                smooth[peak_idx + i] = smooth[peak_idx + i] * (1 - weight * 0.5) + \
                                      peak_val * weight * 0.5
    
    return smooth


def parse_time_data(filename):
    """
    Parse CSV file with time and temperature data
    Expected format: time,am/pm,temperature
    """
    times = []
    temps = []
    
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                time_str = f"{row[0]} {row[1]}"
                temp = float(row[2])
                times.append(time_str)
                temps.append(temp)
    
    return times, temps


def smooth_temperature_data(data, method='both'):
    """
    Apply peak-touching smoothing to temperature data
    
    Parameters:
    data: list or array of temperature values
    method: 'clean', 'standard', or 'both'
    
    Returns:
    dict with smoothed data
    """
    results = {'original': np.array(data)}
    
    if method in ['clean', 'both']:
        results['clean'] = peak_touch_clean(data)
    
    if method in ['standard', 'both']:
        results['standard'] = peak_touch_standard(data)
    
    return results


def plot_smoothed_data(times, results, title="Temperature Smoothing"):
    """
    Visualize original and smoothed data
    """
    plt.figure(figsize=(14, 8))
    
    # Plot each dataset
    x = np.arange(len(times))
    
    for label, data in results.items():
        if label == 'original':
            plt.plot(x, data, 'o-', linewidth=2, markersize=6, 
                    label=label.capitalize(), alpha=0.7)
        else:
            plt.plot(x, data, '-', linewidth=2.5, 
                    label=f'Peak-Touch {label.capitalize()}')
    
    # Mark peak points
    peak_val = np.max(results['original'])
    peak_indices = np.where(results['original'] == peak_val)[0]
    plt.scatter(peak_indices, [peak_val] * len(peak_indices), 
               color='red', s=100, zorder=5, label=f'Peak: {peak_val}')
    
    # Formatting
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Temperature', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Rotate x labels if many time points
    if len(times) > 20:
        plt.xticks(x[::2], times[::2], rotation=45, ha='right')
    else:
        plt.xticks(x, times, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


def calculate_stats(data):
    """
    Calculate statistics for the data
    """
    peak_val = np.max(data)
    peak_indices = np.where(data == peak_val)[0]
    
    stats = {
        'peak_value': peak_val,
        'peak_count': len(peak_indices),
        'peak_indices': peak_indices.tolist(),
        'min_value': np.min(data),
        'mean': np.mean(data),
        'std': np.std(data),
        'range': np.max(data) - np.min(data)
    }
    
    return stats


# Example usage
if __name__ == "__main__":
    # Example 1: Simple data array
    print("Example 1: Simple temperature data")
    temps = [21, 22, 21, 21, 22, 22, 23, 22, 23, 21, 21, 20]
    
    # Apply smoothing
    results = smooth_temperature_data(temps)
    
    # Print results
    print(f"Original: {temps}")
    print(f"Clean:    {[round(x, 1) for x in results['clean']]}")
    print(f"Standard: {[round(x, 1) for x in results['standard']]}")
    
    # Calculate stats
    stats = calculate_stats(temps)
    print(f"\nStats: Peak={stats['peak_value']} (occurs {stats['peak_count']} times)")
    
    # Example 2: From CSV file
    print("\n\nExample 2: From CSV file")
    # Uncomment to use with actual file:
    # times, temps = parse_time_data('temperature_data.csv')
    # results = smooth_temperature_data(temps)
    # plot_smoothed_data(times, results)
    
    # Example 3: Multiple separated peaks
    print("\n\nExample 3: Multiple separated peaks")
    temps2 = [22, 23, 22, 21, 22, 23, 22, 21, 20]
    results2 = smooth_temperature_data(temps2)
    
    print(f"Original: {temps2}")
    print(f"Clean:    {[round(x, 1) for x in results2['clean']]}")
    print(f"Standard: {[round(x, 1) for x in results2['standard']]}")
    
    # Example 4: Export smoothed data
    def export_smoothed_csv(times, results, output_file):
        """Export smoothed data to CSV"""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Original', 'Clean', 'Standard'])
            
            for i in range(len(times)):
                row = [times[i], results['original'][i]]
                if 'clean' in results:
                    row.append(round(results['clean'][i], 1))
                if 'standard' in results:
                    row.append(round(results['standard'][i], 1))
                writer.writerow(row)
        
        print(f"Exported to {output_file}")
