# Analisis de Datos - Group 3
A. Ortiz, N. Matte, J. Escrihuela, H. Kanza.  
All rights reserved.

# How to run the flask application ?

Requirements are in requirements.txt  
You might need to install what is missing on your computer thanks to :  
`$ pip install [extension_name]`


In a Git Bash terminal and in the "/Grupo_3/app" folder (where there is the `run.py`) :

1. define environment variable  
``$ export FLASK_APP=run.py``  
(not mandatory, but might be necessary if you get unexpected errors)

2. run the app  
``$ flask run``

The application will be available on your browser at :

http://localhost:5000/

# Demonstration

The video is available at :  

https://youtu.be/jxEO5R6Vbv4


# Guide of the website

1. The first page describes the three parts of the project. Your only option
is to click on "let's compute datamining !".

2. On the page "DataMining", you need to fill the form with the data you want to download (example data of February 2024) and, if
you want to download several consecutive months at once, you can specify n higher than 1. (example : n = 2 will download
February 2024 and January 2024).  

While the loading screen is displayed, Python will use the code of `DataExtraction.py` in order to retrieve the data.
Be careful, downloading new data erases the old ones.

You can also skip the datamining part by clicking on "Skip this part" if you have already downloaded the data you're interested in.

3. You are now on the data cleaning page. All you have to do is click on "Let's clean data".
It will use the code of ``DataCleaning.py`` in order to remove NaN and process data (from string to number for example).

4. You are now on the visualisation board. You can choose which tools you want to use to analyse data. We grouped in "Aggregated
Curves" three tools : build the aggregated curve for a specified market at a specified hour, build the evolution of the market
price this day and same for the equilibrium quantity of energy (hour after hour). For that, fill the form on the corresponding page and enjoy !  
Be careful, javascript is here to prevent you from using nonexistent files.
The code used to generate images is in `visualisation.py`

NB : All relevant .py files are in the app folder. The notebooks at the root have illustrative purpose, they show how the code was constructed and the choices made behind.