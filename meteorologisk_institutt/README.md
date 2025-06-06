Examen de Maja Åsmul

This script retrieves and visualizes daily wind speed data from the Norwegian Frost API, that gives access to "MET Norway's archive of historical weather and climate data"
The user is guided through the following steps:

1. All weather stations in Norway are retrieved.
2. Only stations that measure wind are kept.
3. The user selects a county and then a weather station within that county.
4. The user provides a date range for which to retrieve data.
5. The script fetches the daily maximum wind speed for the selected station and period, as well as the mean wind speed

The data is:
Displayed in a time series line plot
Shown in a bar chart (if the period is 31 days or shorter), for both max wind speed and mean wind speed
Saved as a CSV file named Frost_output in the user's Documents folder
