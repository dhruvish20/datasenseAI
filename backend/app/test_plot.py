import pandas as pd
import matplotlib.pyplot as plt

# ---- CHANGE THIS ----
csv_path = "test.csv"  # or any CSV path you used in your agent
output_file = "output_plot.png"

# Load CSV
df = pd.read_csv(csv_path)

# Ensure 'Order Date' is datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])

df = df.sort_values("Order Date")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df["Order Date"], df["Profit"], label="Profit over Time")
plt.xlabel("Order Date")
plt.ylabel("Profit")
plt.title("Profit Over Time")
plt.grid(True)
plt.tight_layout()
plt.legend()

# Save
plt.savefig(output_file)
print(f"Plot saved to: {output_file}")
