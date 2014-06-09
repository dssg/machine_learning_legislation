# identify_common_ngrams.py 

> I wrote this with the intention of trying to extract meaningful n-grams
> from the excerpts columns of the earmarks listed at the website
> http://earmarks.omb.gov/. Specifically from the CSV files you can download
> from i.e., http://earmarks.omb.gov/earmarks-public/2010_download.html.
> Initial results don't seem particularly insightful, but I've only looked at
> one year, and I'm not sure the measures I'm using are the best. The goal
> for this was to try to see if there are common phrases in these
> excerpts that identify them as earmarks.

Example usage:
`python identify_common_ngrams.py --file data/2010-appropriations-earmark-extract.csv --measure pmi --freq 10`

