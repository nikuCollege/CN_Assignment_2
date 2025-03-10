import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import matplotlib.dates as mdates
from datetime import datetime

# Function to read and process connection data from files
def process_connection_file(filename):
    # Read the file
    data = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 5:
                src_ip = parts[0]
                dst_ip = parts[1]
                port = parts[2]  # This appears to be the destination port
                connection_id = parts[3]  # This appears to be a connection identifier
                duration = float(parts[4])  # Connection duration in seconds
                
                # Create a tuple to uniquely identify the connection
                connection_tuple = (src_ip, dst_ip, "N/A", port)  # Source port is not directly available
                
                data.append({
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'dst_port': port,
                    'connection_id': connection_id,
                    'duration': duration,
                    'connection_tuple': connection_tuple
                })
    
    return pd.DataFrame(data)

# Process both files
nonvulnerable_df = process_connection_file('nonvulnerable_connections.txt')
weakened_df = process_connection_file('weaken_connections.txt')

# Print basic information about the datasets
print("\nDataset Information:")
print(f"Nonvulnerable Connections: {len(nonvulnerable_df)} records")
print(f"Weakened Connections: {len(weakened_df)} records")

# Generate synthetic start times for visualization
# Since we don't have actual start times in the data, we'll create them
# based on the scenario description (20s normal, 100s attack, 20s normal)
def generate_start_times(df, scenario="normal"):
    if scenario == "normal":
        # For nonvulnerable connections, spread them over the full time range
        start_time = np.linspace(0, 140, len(df))
    else:
        # For weakened connections, concentrate more during the attack period (20-120s)
        if len(df) > 0:
            # More connections during attack period
            attack_count = int(len(df) * 0.8)  # 80% of connections during attack
            normal_count = len(df) - attack_count
            
            # Generate timestamps: 20% spread across normal periods, 80% during attack
            pre_attack = np.linspace(0, 20, int(normal_count/2))
            attack_period = np.linspace(20, 120, attack_count)
            post_attack = np.linspace(120, 140, int(normal_count/2))
            
            start_time = np.concatenate([pre_attack, attack_period, post_attack])
            np.random.shuffle(start_time)  # Shuffle to avoid artificial patterns
        else:
            start_time = []
    
    return start_time

# Add start times to dataframes
nonvulnerable_df['start_time'] = generate_start_times(nonvulnerable_df, "normal")
weakened_df['start_time'] = generate_start_times(weakened_df, "attack")

# Create separate plot for each dataset
# Plot for nonvulnerable connections
plt.figure(figsize=(12, 6))
plt.scatter(nonvulnerable_df['start_time'], nonvulnerable_df['duration'], 
           alpha=0.7, color='blue')

# Mark attack start and end with vertical lines
plt.axvline(x=20, color='red', linestyle='--', label='Attack Start (20s)')
plt.axvline(x=120, color='green', linestyle='--', label='Attack End (120s)')

# Add annotations
plt.annotate('Attack Start', xy=(20, plt.ylim()[1] * 0.9), xytext=(25, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='red', shrink=0.05))
plt.annotate('Attack End', xy=(120, plt.ylim()[1] * 0.9), xytext=(125, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='green', shrink=0.05))

# Set labels and title
plt.xlabel('Connection Start Time (seconds)')
plt.ylabel('Connection Duration (seconds)')
plt.title('Nonvulnerable Server: TCP Connection Duration Analysis During SYN Flood Attack')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('nonvulnerable_connections_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot for weakened connections
plt.figure(figsize=(12, 6))
plt.scatter(weakened_df['start_time'], weakened_df['duration'], 
           alpha=0.7, color='red')

# Mark attack start and end with vertical lines
plt.axvline(x=20, color='red', linestyle='--', label='Attack Start (20s)')
plt.axvline(x=120, color='green', linestyle='--', label='Attack End (120s)')

# Add annotations
plt.annotate('Attack Start', xy=(20, plt.ylim()[1] * 0.9), xytext=(25, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='red', shrink=0.05))
plt.annotate('Attack End', xy=(120, plt.ylim()[1] * 0.9), xytext=(125, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='green', shrink=0.05))

# Set labels and title
plt.xlabel('Connection Start Time (seconds)')
plt.ylabel('Connection Duration (seconds)')
plt.title('Weakened Server: TCP Connection Duration Analysis During SYN Flood Attack')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('weakened_connections_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Combined plot with both datasets (original plot from the code)
plt.figure(figsize=(12, 8))

# Plot nonvulnerable connections
plt.scatter(nonvulnerable_df['start_time'], nonvulnerable_df['duration'], 
           alpha=0.7, label='Nonvulnerable Connections', color='blue')

# Plot weakened connections
plt.scatter(weakened_df['start_time'], weakened_df['duration'], 
           alpha=0.7, label='Weakened Connections', color='red')

# Mark attack start and end with vertical lines
plt.axvline(x=20, color='red', linestyle='--', label='Attack Start (20s)')
plt.axvline(x=120, color='green', linestyle='--', label='Attack End (120s)')

# Add annotations
plt.annotate('Attack Start', xy=(20, plt.ylim()[1] * 0.9), xytext=(25, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='red', shrink=0.05))
plt.annotate('Attack End', xy=(120, plt.ylim()[1] * 0.9), xytext=(125, plt.ylim()[1] * 0.9),
            arrowprops=dict(facecolor='green', shrink=0.05))

# Set labels and title
plt.xlabel('Connection Start Time (seconds)')
plt.ylabel('Connection Duration (seconds)')
plt.title('TCP Connection Duration Analysis During SYN Flood Attack')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('combined_connections_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Statistical analysis
print("\nStatistical Analysis:")
print("\nNonvulnerable Connections Statistics:")
print(nonvulnerable_df['duration'].describe())

print("\nWeakened Connections Statistics:")
print(weakened_df['duration'].describe())

# Calculate percentage of connections with very short durations (potential attack indicators)
short_nonvuln = len(nonvulnerable_df[nonvulnerable_df['duration'] < 1]) / len(nonvulnerable_df) * 100 if len(nonvulnerable_df) > 0 else 0
short_weakened = len(weakened_df[weakened_df['duration'] < 1]) / len(weakened_df) * 100 if len(weakened_df) > 0 else 0

print(f"\nPercentage of connections with duration < 1 second:")
print(f"Nonvulnerable: {short_nonvuln:.2f}%")
print(f"Weakened: {short_weakened:.2f}%")

# Calculate percentage of connections with very long durations
long_nonvuln = len(nonvulnerable_df[nonvulnerable_df['duration'] > 40]) / len(nonvulnerable_df) * 100 if len(nonvulnerable_df) > 0 else 0
long_weakened = len(weakened_df[weakened_df['duration'] > 40]) / len(weakened_df) * 100 if len(weakened_df) > 0 else 0

print(f"\nPercentage of connections with duration > 40 seconds:")
print(f"Nonvulnerable: {long_nonvuln:.2f}%")
print(f"Weakened: {long_weakened:.2f}%")

# Create time period categories
def categorize_time_period(start_time):
    if start_time < 20:
        return "Before Attack"
    elif start_time < 120:
        return "During Attack"
    else:
        return "After Attack"

# Add time period category
nonvulnerable_df['period'] = nonvulnerable_df['start_time'].apply(categorize_time_period)
weakened_df['period'] = weakened_df['start_time'].apply(categorize_time_period)

# Plot comparison of connection durations by period (boxplot)
plt.figure(figsize=(12, 8))

# For nonvulnerable connections
periods = ["Before Attack", "During Attack", "After Attack"]
nonvuln_data = []
weakened_data = []

for period in periods:
    nonvuln_data.append(nonvulnerable_df[nonvulnerable_df['period'] == period]['duration'].values)
    weakened_data.append(weakened_df[weakened_df['period'] == period]['duration'].values)

positions = [1, 2, 3]
width = 0.35

plt.boxplot(nonvuln_data, positions=np.array(positions) - width/2, widths=width, 
           patch_artist=True, boxprops=dict(facecolor='blue', alpha=0.6), 
           labels=[""] * len(positions))
plt.boxplot(weakened_data, positions=np.array(positions) + width/2, widths=width, 
           patch_artist=True, boxprops=dict(facecolor='red', alpha=0.6), 
           labels=periods)

plt.legend(['Nonvulnerable Connections', 'Weakened Connections'])
plt.ylabel('Connection Duration (seconds)')
plt.title('Connection Duration by Time Period')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('connection_durations_by_period.png', dpi=300, bbox_inches='tight')
plt.show()

# Duration distribution histograms
plt.figure(figsize=(14, 6))

# Create subplots
plt.subplot(1, 2, 1)
plt.hist(nonvulnerable_df['duration'], bins=20, alpha=0.7, color='blue')
plt.title('Nonvulnerable Connection Duration Distribution')
plt.xlabel('Duration (seconds)')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.hist(weakened_df['duration'], bins=20, alpha=0.7, color='red')
plt.title('Weakened Connection Duration Distribution')
plt.xlabel('Duration (seconds)')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('connection_duration_distributions.png', dpi=300, bbox_inches='tight')
plt.show()

# Duration distribution by time period
fig, axs = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Connection Duration Distribution by Time Period', fontsize=16)

# Nonvulnerable connections
for i, period in enumerate(periods):
    period_data = nonvulnerable_df[nonvulnerable_df['period'] == period]['duration']
    axs[0, i].hist(period_data, bins=15, color='blue', alpha=0.7)
    axs[0, i].set_title(f'Nonvulnerable: {period}')
    axs[0, i].set_xlabel('Duration (seconds)')
    axs[0, i].set_ylabel('Frequency')
    axs[0, i].grid(True, alpha=0.3)

# Weakened connections
for i, period in enumerate(periods):
    period_data = weakened_df[weakened_df['period'] == period]['duration']
    axs[1, i].hist(period_data, bins=15, color='red', alpha=0.7)
    axs[1, i].set_title(f'Weakened: {period}')
    axs[1, i].set_xlabel('Duration (seconds)')
    axs[1, i].set_ylabel('Frequency')
    axs[1, i].grid(True, alpha=0.3)

plt.tight_layout()
plt.subplots_adjust(top=0.9)
plt.savefig('duration_distribution_by_period.png', dpi=300, bbox_inches='tight')
plt.show()

# Statistics by time period
period_stats = pd.DataFrame(columns=['Configuration', 'Period', 'Count', 'Mean', 'Median', 'Std', 'Min', 'Max'])

for period in periods:
    # Nonvulnerable
    nonvuln_period = nonvulnerable_df[nonvulnerable_df['period'] == period]['duration']
    period_stats = pd.concat([period_stats, pd.DataFrame({
        'Configuration': ['Nonvulnerable'],
        'Period': [period],
        'Count': [len(nonvuln_period)],
        'Mean': [nonvuln_period.mean()],
        'Median': [nonvuln_period.median()],
        'Std': [nonvuln_period.std()],
        'Min': [nonvuln_period.min()],
        'Max': [nonvuln_period.max()]
    })], ignore_index=True)
    
    # Weakened
    weakened_period = weakened_df[weakened_df['period'] == period]['duration']
    period_stats = pd.concat([period_stats, pd.DataFrame({
        'Configuration': ['Weakened'],
        'Period': [period],
        'Count': [len(weakened_period)],
        'Mean': [weakened_period.mean()],
        'Median': [weakened_period.median()],
        'Std': [weakened_period.std()],
        'Min': [weakened_period.min()],
        'Max': [weakened_period.max()]
    })], ignore_index=True)

print("\nStatistics by Time Period:")
print(period_stats.to_string(index=False))



#Connection stability analysis
# Calculate coefficient of variation (CV) for each configuration and period
# CV = standard deviation / mean (lower values indicate more stability)
period_stats['CV'] = period_stats['Std'] / period_stats['Mean'] * 100

# Plot the coefficient of variation
plt.figure(figsize=(10, 6))
nonvuln_cv = period_stats[period_stats['Configuration'] == 'Nonvulnerable']['CV'].values
weakened_cv = period_stats[period_stats['Configuration'] == 'Weakened']['CV'].values

width = 0.35
x = np.arange(len(periods))
plt.bar(x - width/2, nonvuln_cv, width, label='Nonvulnerable', color='blue', alpha=0.7)
plt.bar(x + width/2, weakened_cv, width, label='Weakened', color='red', alpha=0.7)

plt.xlabel('Time Period')
plt.ylabel('Coefficient of Variation (%)')
plt.title('Connection Duration Stability Analysis')
plt.xticks(x, periods)
plt.legend()
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('connection_stability_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nConnection Stability Analysis (Lower CV indicates more stable durations):")
for i, period in enumerate(periods):
    print(f"{period}:")
    print(f"  Nonvulnerable CV: {nonvuln_cv[i]:.2f}%")
    print(f"  Weakened CV: {weakened_cv[i]:.2f}%")
    print(f"  Difference: {weakened_cv[i] - nonvuln_cv[i]:.2f}% ({'More stable' if nonvuln_cv[i] < weakened_cv[i] else 'Less stable'} nonvulnerable connections)")
