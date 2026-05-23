Objective: Analyze electricity demand behavior.
Suggested indicators:
 demand ramps,
 demand peaks,
 variability,
 residual demand,
 flexibility index.
Deliverable:
src/demand/ 

The project structure will be:
data/raw
data/processed
src/
notebooks/
Data files must not be uploaded to the repository through the appropriate customization of
the .gitignore file.
The whole project will consist of building a tool capable of extracting, processing, analyzing, and
visualizing information from different European electricity markets for the following countries:
 Spain (ES)
 France (FR)
 Germany (DE_LU)
using official APIs and public datasets.
Country Recommended Source Useful Data
Spain ESIOS / REE + OMIE prices, demand, generation, renewables
France RTE / éCO2mix consumption, production, exchanges, electricity mix
Germany SMARD / Bundesnetzagentur prices, generation, demand, exchanges
