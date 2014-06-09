import nltk
from nltk.collocations import *
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Evaluate earmarks csv.')
parser.add_argument('--file', action='store', dest='file_location')
parser.add_argument('--measure', action='store', dest='measure_type',
        help='bigram measure to use in rankings.')
parser.add_argument('--freq', action='store', type=int, dest='freq_filter',
        help='minimum number of times n-gram must appear to be considered.')
results = parser.parse_args()

# read in the csv and get the excerpts column
df = pd.read_csv(results.file_location)
excerpts = df['c_f_cttn_excerpt'].astype('string')
excerpts_text = ' '.join(excerpts)
tokens = nltk.wordpunct_tokenize(excerpts_text)

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

finder = BigramCollocationFinder.from_words(tokens)

# only bigrams that appear 5+ times
finder.apply_freq_filter(results.freq_filter)

# return the 10 n-grams with the highest PMI
# TODO: not sure this use of eval makes sense, but works
highest_pmi_bigrams = finder.nbest(eval('bigram_measures.' + results.measure_type), 10)

print highest_pmi_bigrams
