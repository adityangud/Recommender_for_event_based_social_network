## Recommender for Event Based Social Network(WhatTheRec) ##

Project for Information Storage and Retrieval Course 670

It is of utmost importance in today's world that an event based social network use recommenders to suggest relevant and interesting events to its users which help them choose between various events. Therefore, this is a system for recommending events to users based on their previous activities. It is based on "Context-Aware Event Recommendation in Event-based Social Networks" paper by Augusto Q. Macedo, Leandro B. Marinho and Rodrygo L. T. Santos. We have collected data from Meetup.com for four cities, namely, SanJose, Phoenix, Chicago and College Station. The main problem in working on event recommendation is the cold-start problem. We do not know which events will the user actually attend. This eliminates the use of simple collaborative filtering and latent factor models.

Hence, we are using the context knowledge to handle the cold start problem. Context knowledge can include temporal preferences, the set of groups the user can join, the users' geographic preferences and textual content of events. More specifically, we have used Social Aware, Content Aware, Location Aware, and Time Aware as features of the algorithm. Based on these we apply a Learning To Rank algorithms to obtain recommendations.

To evaluate our data, we have divided the dataset into two timelines. The first timeline will be used to train the model and the second dataset has been used to test on this data. The prediction have been compared to the actual data using Precision and Recall.

## DataSet ##
We used meetup data for 3 cities, namely, Chicago, Phoenix, and San Jose.

Data is present at following link:-
https://goo.gl/ThgVtY

Each folder corresponds to a city and contains five files.

## Video ##

https://goo.gl/2CE6Gv

## How to run Jupyter Notebook ##
Open the Jupyter Notebook and run all the code sequentially. 
Note: Please do not run this code outside the current directory. The code in this notebook calls some python code that are present in the subdirectories. 

## Dependencies to be installed ##

### sklearn 
``` 
pip install sklearn 
```
### scipy 
``` 
pip install scipy
```
### numpy
``` 
pip install numpy
```
### json 
``` 
pip install json
```

### pandas 
``` 
pip install pandas
```

## How to run the Project from console ##
python index.py --city <city_name> --algo <algo_name> --members <no. of members>

city_name can be "LSAN JOSE", "LPHOENIX" or "LCHICAGO"

This project is only python2.7 compatible.

## Website for Data Visualization ##
Website for data visualization is made which helped us a lot while writing the recommender.

http://enigmatic-earth-94392.herokuapp.com

Some of the features on it are :-
Given a user id, one can get the details of the user.
Given a event id, one can get the details of the event.
Also, one interesting feature made is one can see all events attended by user on Google maps.

## Paper that we used reference ##
http://dl.acm.org/citation.cfm?id=2800187

Special thanks to authors of this paper who provided us the dataset and such an awesome model.
