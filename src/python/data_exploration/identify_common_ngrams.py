import nltk
from nltk.collocations import *
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Evaluate earmarks csv.')
parser.add_argument('--file', action='store', dest='file_location')
parser.add_argument('--measure', action='store', dest='measure_type',
        help='bigram measure to use in rankings.')
parser.add_argument('--freq', action='store', type=int, dest='freq_filter')
parser.add_argument('--n', action='store', type=int, dest='ngram',
        help='use bigrams or trigrams.')
results = parser.parse_args()

# read in the csv and get the excerpts column
df = pd.read_csv(results.file_location)
excerpts = df['c_f_cttn_excerpt'].astype('string')
excerpts_text = ' '.join(excerpts)
tokens = nltk.wordpunct_tokenize(excerpts_text)

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

if results.ngram == 2:
    finder = BigramCollocationFinder.from_words(tokens)
else:
    finder = TrigramCollocationFinder.from_words(tokens)

# only bigrams that appear 5+ times
finder.apply_freq_filter(results.freq_filter)

# TODO: not sure this use of eval makes sense, but works
if results.ngram == 2:
    collocs = finder.nbest(eval('bigram_measures.' + results.measure_type), 10)
    finder = BigramCollocationFinder.from_words(tokens)
else:
    collocs = finder.nbest(eval('trigram_measures.' + results.measure_type), 10)

print collocs
