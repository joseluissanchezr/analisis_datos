from entsoe import EntsoePandasClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#DL the module entsoe 

client = EntsoePandasClient(
    api_key='5bcf63bf-87d7-4aa5-8bfb-040cbc4c4af0'
)


##This is my token 
start = pd.Timestamp(
    '2025-01-01',
    tz='Europe/Brussels'
)

end = pd.Timestamp(
    '2025-03-01',
    tz='Europe/Brussels'
)

es = client.query_day_ahead_prices(
    'ES',
    start=start,
    end=end
)

fr = client.query_day_ahead_prices(
    'FR',
    start=start,
    end=end
)

df = pd.DataFrame({
    'Spain': es,
    'France': fr
})

print(df.head())


prices = client.query_day_ahead_prices(
    country_code='ES',
    start=start,
    end=end
)

prices = prices.to_frame(name='price')
####The day ahead prices are getting gathered

###NEGATIVE PRICE for spain

neg_prices_sp = df[df['Spain'] < 0]

print(neg_prices_sp)
#No negative price from this period
amplitude = df['Spain'].max() - df['Spain'].min()

##SPREAD GEOGRAPHIQUE / TRADING ????

# solar gen

generation = client.query_generation(
    country_code='ES',
    start=start,
    end=end,
    psr_type=None
)


solar = generation[('Solar', 'Actual Aggregated')]

solar = solar.to_frame(name='solar_mw')

df = prices.join(solar, how='inner')

# Remove Not a number values
df = df.dropna()

# =========================
# CAPTURE PRICE
# =========================

capture_price = (
    (df['price'] * df['solar_mw']).sum()
    / df['solar_mw'].sum()
)

print(f"Solar Capture Price Spain: {capture_price:.2f} €/MWh")



baseload_price = df['price'].mean()

print(f"Baseload Price: {baseload_price:.2f} €/MWh")



capture_rate = capture_price / baseload_price

print(f"Capture Rate: {capture_rate:.2%}")


negative_hours = (df['price'] < 0).sum()

print(f"Negative price hours: {negative_hours}")

solar_negative = df[df['price'] < 0]['solar_mw'].sum()

solar_total = df['solar_mw'].sum()

share_negative = solar_negative / solar_total

print(f"Solar generation during negative prices: {share_negative:.2%}")



midday = df.between_time('11:00', '15:00')

midday_avg = midday['price'].mean()
#midday solar deperssion is an environemental and energy grid pehnomenon where peak daytime
#drivex extreme power generation. Massive surge when sun sets 
#this is the moment user demand is increasing
print("Solar depression midday average")
print( midday_avg)


##Duck curve, the famous curve of demand and therefore, the lack of flexibility.

hourly_profile = df.groupby(df.index.hour)['price'].mean()

print(hourly_profile)

import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))

plt.plot(
    hourly_profile.index,
    hourly_profile.values,
    marker='o'
)

plt.xlabel('Hour of Day')
plt.ylabel('Average Price (€/MWh)')
plt.title('Average Hourly Power Price Profile - Spain')

plt.grid(True)

plt.xticks(range(0,24))

plt.show()

###evening ramp from the duck curve 

price_14h = df[df.index.hour == 14]['price']
price_20h = df[df.index.hour == 20]['price']

ramp_df = pd.DataFrame({
    'price_14h': price_14h.values,
    'price_20h': price_20h.values
}, index=price_14h.index.date)


ramp_df['evening_ramp'] = (
    ramp_df['price_20h']
    - ramp_df['price_14h']
)



avg_ramp = ramp_df['evening_ramp'].mean()

print(f"\nAverage Evening Ramp: {avg_ramp:.2f} €/MWh")

max_ramp = ramp_df['evening_ramp'].max()

print(f"Maximum Evening Ramp: {max_ramp:.2f} €/MWh")


plt.figure(figsize=(12,5))

plt.plot(
    ramp_df.index,
    ramp_df['evening_ramp']
)

plt.axhline(
    avg_ramp,
    linestyle='--'
)

plt.title('Daily Evening Ramp - Spain')
plt.ylabel('Ramp (€/MWh)')
plt.xlabel('Date')

plt.grid(True)

plt.show()

#the evening ramp si the difference between prices at 14 and 20, the goal is to actually have a simple visualisation
#to analyse how prices tend to go up during the evening.

#Potential bonus, we need to maybe analyse it furthermore is the Battery arbitrage opportunity. The goal of an arbitrage 
#is to make a profit without taking any risks

battery_mwh = 1

daily_revenue = (
    ramp_df['evening_ramp']
    * battery_mwh
)

print(daily_revenue.head())
