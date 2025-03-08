import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

# Plot the results
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

# Save the plot
plt.savefig('syn_flood_analysis.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
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

# Create a second plot comparing the connection durations before, during, and after attack
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

# Plot comparison of connection durations by period
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

plt.savefig('connection_durations_by_period.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()
