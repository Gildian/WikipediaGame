# WikipediaGame
Wikipedia Game Bot that finds the shortest path between two wikipedia articles.  
This bot requires the GloVe Wikipedia 2014 + Gigaword 5 vectors to work [download link here](https://nlp.stanford.edu/data/glove.6B.zip).
## Dependencies
As stated above the GloVe vectors are required.  
Python Dependencies:
* torch
* torchtext
* BeautifulSoup

## Running The Bot
After downloading all dependencies the first time the bot runs it will calculate the vector cache, which may take some time. There are 3 ways to run the bot:
|Arguments|Description|
|:--:|:--|
|None|Will prompt user for input|
|"random"|Will generate two random articles to solve|
|title1 title2|Will pass the titles into the bot from the command line|

## Citations
Jeffrey Pennington, Richard Socher, and Christopher D. Manning. 2014. [GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/pubs/glove.pdf).
