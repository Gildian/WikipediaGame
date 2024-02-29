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
After downloading all dependencies simply running the `main.py` file will start the bot. The first time the bot runs it will calculate the vector cache, which may take some time. After it is done the bot will prompt for input.

## Citations
Jeffrey Pennington, Richard Socher, and Christopher D. Manning. 2014. [GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/pubs/glove.pdf).
