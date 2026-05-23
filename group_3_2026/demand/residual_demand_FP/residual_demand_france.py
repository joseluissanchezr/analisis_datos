import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv(
    "eCO2mix_RTE_Annuel-Definitif_2024.csv",
    sep=";"
)

# Compute residual demand
df["residual_demand"] = (
    df["Consommation"]
    - df["Eolien"]
    - df["Solaire"]
)

# Display first rows
print(df[[
    "Consommation",
    "Eolien",
    "Solaire",
    "residual_demand"
]].head())

# Plot
plt.figure(figsize=(15,6))

plt.plot(
    df["Consommation"],
    label="Total Demand"
)

plt.plot(
    df["residual_demand"],
    label="Residual Demand"
)

plt.xlabel("Time Steps")
plt.ylabel("Power (MW)")
plt.title("Total Demand vs Residual Demand")
plt.legend()

plt.show()

# Statistical analysis
print("\nAverage total demand:")
print(df["Consommation"].mean())

print("\nAverage residual demand:")
print(df["residual_demand"].mean())

print("\nMaximum residual demand:")
print(df["residual_demand"].max())

print("\nMinimum residual demand:")
print(df["residual_demand"].min())

# Renewable contribution
df["renewable_share"] = (
    (df["Eolien"] + df["Solaire"])
    / df["Consommation"]
) * 100

print("\nAverage renewable share (%):")
print(df["renewable_share"].mean())