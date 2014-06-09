# I wrote this with the intention of trying to extract meaningful n-grams
# from the excerpts columns of the earmarks listed at the website
# http://earmarks.omb.gov/. Specifically from the CSV files you can download
# from i.e., http://earmarks.omb.gov/earmarks-public/2010_download.html.
# Initial results don't seem particularly insightful, but I've only looked at
# one year, and I'm not sure the measures I'm using are the best. The goal
# for this was to try to see if there are common phrases in these
# excerpts that identify them as earmarks.

import nltk
from nltk.collocations import *
import pandas as pd

# read in the csv and get the excerpts column
csv_file = 'data/2010-appropriations-earmark-extract.csv'
df = pd.read_csv(csv_file)
excerpts = df['c_f_cttn_excerpt'].astype('string')
excerpts_text = ' '.join(excerpts)
tokens = nltk.wordpunct_tokenize(excerpts_text)

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

finder = BigramCollocationFinder.from_words(tokens)

# only bigrams that appear 5+ times
finder.apply_freq_filter(5)

# return the 10 n-grams with the highest PMI
highest_pmi_bigrams = finder.nbest(bigram_measures.pmi, 10)

print highest_pmi_bigrams
