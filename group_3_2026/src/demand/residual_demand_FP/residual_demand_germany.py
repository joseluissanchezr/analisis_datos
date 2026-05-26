import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv(
    "generation_germany.csv",
    sep=";"
)

# Production columns
cols = df.columns[2:]

# Remove commas and convert to numeric
for col in cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Total wind generation
df["wind_total"] = (
    df["Wind offshore [MWh] Calculated resolutions"]
    + df["Wind onshore [MWh] Calculated resolutions"]
)

# Solar generation
df["solar_total"] = (
    df["Photovoltaics [MWh] Calculated resolutions"]
)

# Approximate total demand
df["total_generation"] = df[cols].sum(axis=1)

# Residual demand
df["residual_demand"] = (
    df["total_generation"]
    - df["wind_total"]
    - df["solar_total"]
)

# Display first rows
print(df[[
    "total_generation",
    "wind_total",
    "solar_total",
    "residual_demand"
]].head())

# Plot
plt.figure(figsize=(15,6))

plt.plot(
    df["total_generation"],
    label="Approximate Demand"
)

plt.plot(
    df["residual_demand"],
    label="Residual Demand"
)

plt.xlabel("Time Steps")
plt.ylabel("Energy (MWh)")
plt.title("Germany Residual Demand Analysis")

plt.legend()

plt.show()

# Statistics
print("\nAverage total generation:")
print(df["total_generation"].mean())

print("\nAverage residual demand:")
print(df["residual_demand"].mean())

print("\nAverage renewable share (%):")

df["renewable_share"] = (
    (df["wind_total"] + df["solar_total"])
    / df["total_generation"]
) * 100

print(df["renewable_share"].mean())