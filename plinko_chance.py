import json
import matplotlib.pyplot as plt

# Load the JSON data
with open('plinko_slot_data.json', 'r') as file:
    data = json.load(file)

# Initialize variables to store total balls and slot hits
total_balls = 0
slot_hits = {str(i): 0 for i in range(17)}  # Assumes there are 17 slots, numbered 0-16

# Process each entry in the JSON file
for entry in data:
    slot_counts = entry["slot_hits"]
    # Sum the total balls for this timestamp
    total_balls += sum(slot_counts.values())
    # Sum the hits for each slot
    for slot, count in slot_counts.items():
        slot_hits[slot] += count

# Calculate probabilities for each slot
slot_probabilities = {slot: hits / total_balls for slot, hits in slot_hits.items()}

# Prepare data for plotting
slots = list(slot_probabilities.keys())
probabilities = list(slot_probabilities.values())

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(slots, probabilities, color='skyblue')
plt.xlabel('Slot Number')
plt.ylabel('Probability')
plt.title('Probability of Landing in Each Slot')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show plot
plt.show()
