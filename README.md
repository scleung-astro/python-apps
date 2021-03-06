# python-apps
standalone python apps with both frontend and backend built from scratch

## Introduction
This folder contains some recent development of python apps using PyGame 
and Tkinter as GUI libraries. I developed both the frontend and backend
from scratch. The apps can be run standalone except for weatherapp, where
an api key and the city-list are necessary to start the app. 

### forex_hist.py
This is an app for fetching historical forex exchange rates for some 
important pairs I used to check. The app also plot the data with several
indicators, such as exponential moving average and Bollinger's band. 

### portfolio_management.py
This is a small app using StreamLit to develop a webpage interface for 
portfolio optimization. Based on the given choices of stocks and their
ratio, the app calcaultes the annual return in last five years. Then
it generates the optimized model based on Sharpe ratio in the efficient
frontier analysis.

### othello.py
This is an extension of my tic-tac-toe app that it runs as a game of 
Othello with a decision-tree based AI as an opponent. There are three
dificulties available. 

### saint-saens.py
This is a mini app using StreamLit to develop a query webpage. Based on 
the given gener and composition title, or the opus number, the page
returns the candidate composition. 

### tictactoe.py
This is the first open-source PyGame app I developed. The simple tic-tac-toe
provides an excellent place for me to develop the decision-tree from scratch
without going through tedious details about the game logic. There are two
difficulties available, which refer to different depths of decision tree.

### weatherapp.py
This is my first api-based app which fetch the real time weather data from
OpenWeatherMap. The app allows the users to choose the cities they want to 
check, and the app provides the real time weather details with illustration
based on the current weather. 





