import pandas as pd

#Loading Spain data

spain_tables = pd.read_html(
    "data/raw/data_spain_april_to_june.xls"
)

spain_df = spain_tables[0]

print("Spain data loaded")
print(spain_df.head())


#Loading France data

france_df = pd.read_csv(
    "data/raw/France_demand_year_2024.csv",
    sep="\t",
    encoding="utf-8"
)

print("France data loaded")
print(france_df.head())


#Loading Germany data

germany_df = pd.read_csv(
    "data/raw/hourly_consumption_germany_april_june.csv",
    sep=";",
    encoding="latin1"
)

print("Germany data loaded")
print(germany_df.head())

#cleaning Spain data

#use first row as column names
spain_df.columns = spain_df.iloc[0]

#remove duplicated header row
spain_df = spain_df[1:]

#rename important columns
spain_df = spain_df.rename(columns={
    "value": "demand_mwh",
    "datetime": "datetime"
})

#clean numeric format
spain_df["demand_mwh"] = (
    spain_df["demand_mwh"]
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

#convert datetime
spain_df["datetime"] = pd.to_datetime(
    spain_df["datetime"],
    utc=True
)
#remove timezone information
spain_df["datetime"] = spain_df["datetime"].dt.tz_localize(None)

print("\nSpain cleaned")
print(spain_df.head())

#clean France data

#reset index
france_df = france_df.reset_index()

#rename shifted columns correctly
france_df = france_df.rename(columns={
    "index": "country",
    "Nature": "date",
    "Date": "time",
    "Heures": "demand_mwh"
})

#create datetime column
france_df["datetime"] = pd.to_datetime(
    france_df["date"].astype(str)
    + " "
    + france_df["time"].astype(str)
)

#remove rows with missing demand
france_df = france_df.dropna(subset=["demand_mwh"])

print("\nFrance cleaned")
print(france_df[["datetime", "demand_mwh"]].head())

#clean Germany data

#rename columns
germany_df = germany_df.rename(columns={
    "ï»¿Start date": "datetime",
    "grid load [MWh] Calculated resolutions": "demand_mwh"
})

#convert datetime
germany_df["datetime"] = pd.to_datetime(germany_df["datetime"])

#clean numeric values
germany_df["demand_mwh"] = (
    germany_df["demand_mwh"]
    .str.replace(",", "", regex=False)
    .astype(float)
)

print("\nGermany cleaned")
print(germany_df[["datetime", "demand_mwh"]].head())

#Standarizing datasets

#Keep only needed columns
spain_final = spain_df[["datetime", "demand_mwh"]].copy()
france_final = france_df[["datetime", "demand_mwh"]].copy()
germany_final = germany_df[["datetime", "demand_mwh"]].copy()

#Add country column
spain_final["country"] = "Spain"
france_final["country"] = "France"
germany_final["country"] = "Germany"

#Combine datasets
combined_df = pd.concat(
    [spain_final, france_final, germany_final],
    ignore_index=True
)


print("\nCombined dataset")
print(combined_df.head())

print("\nDataset info")
print(combined_df.info())

#Export processed data

spain_final.to_csv(
    "data/processed/spain_cleaned.csv",
    index=False
)

france_final.to_csv(
    "data/processed/france_cleaned.csv",
    index=False
)

germany_final.to_csv(
    "data/processed/germany_cleaned.csv",
    index=False
)

combined_df.to_csv(
    "data/processed/combined_demand_data.csv",
    index=False
)

print("\nProcessed datasets exported successfully")