import pandas as pd
import matplotlib.pyplot as plt

# Load Spain dataset
df = pd.read_csv(
    "generation_spain.csv",
    sep=","
)


# Rename first column
df = df.rename(columns={"Title": "technology"})

# Remove metadata rows
df = df.iloc[4:]

# Set technology names as index
df = df.set_index("technology")

# Convert values to numeric
df = df.replace(",", ".", regex=True)

df = df.apply(
    pd.to_numeric,
    errors="coerce"
)

# Renewable productions
wind = df.loc["Wind"]
solar_pv = df.loc["Solar photovoltaic"]
solar_thermal = df.loc["Thermal solar"]
hydro = df.loc["Hydro"]

# Approximate total generation
total_generation = df.sum(axis=0)

# Residual demand
residual_demand = (
    total_generation
    - wind
    - solar_pv
    - solar_thermal
    - hydro
)

# Build final dataframe
result = pd.DataFrame({
    "total_generation": total_generation,
    "wind": wind,
    "solar_pv": solar_pv,
    "solar_thermal": solar_thermal,
    "hydro": hydro,
    "residual_demand": residual_demand
})

# Display first rows
print(result.head())

# Plot
plt.figure(figsize=(15,6))

plt.plot(
    result["total_generation"].values,
    label="Total Generation"
)

plt.plot(
    result["residual_demand"].values,
    label="Residual Demand"
)

plt.xlabel("Days")
plt.ylabel("Energy (GWh)")
plt.title("Spain Residual Demand Analysis")

plt.legend()

plt.show()

# Statistics
print("\nAverage total generation:")
print(result["total_generation"].mean())

print("\nAverage residual demand:")
print(result["residual_demand"].mean())

# Renewable share
renewable_share = (
    (
        result["wind"]
        + result["solar_pv"]
        + result["solar_thermal"]
        + result["hydro"]
    )
    / result["total_generation"]
) * 100

print("\nAverage renewable share (%):")
print(renewable_share.mean())