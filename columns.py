import pandas as pd

# Set the path to your CSV file
csv_path = "data/tariffs.csv"  # Update this if your file is elsewhere

# Load just the header
df = pd.read_csv(csv_path, nrows=0)

# Print all column names
print("CSV columns:")
for col in df.columns:
    print(f"- {col}")
