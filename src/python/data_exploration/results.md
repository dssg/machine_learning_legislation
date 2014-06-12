`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure pmi --freq 10 --n 2`
('air', 'traffic'), ('control', 'facilities'), ('facilities', 'replacement'), ('traffic', 'control'), ('Marcus', 'Autism'), ('Pro', 'Marcus'), ('emergency', 'prepare'), ('surface', 'transportation'), ('transportation', 'emergency'), ('UJA', 'Federation')

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure likelihood_ratio --freq 10 --n 2`
>('With', 'regard'), ('specific', 'programs'), (')', 'With'), ('pro', 'Sec'), ('Provided', 'further'), ('in', 'this'), ('a', ')'), ('(', 'a'), ('regard', 'to'), ('appropriated', 'in')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure raw_freq --freq 10 --n 2`
>(',', '000'), ('in', 'this'), ('Sec', '.'), ('to', 'the'), ('.', '('), ('(', 'a'), ('a', ')'), (')', 'With'), (',', 'pro'), ('.', '8006')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure pmi --freq 20 --n 2`
>('As', 'soon'), ('practicable', 'after'), ('Instrument', 'landing'), ('Federal', 'Building'), ('advanced', 'materials'), ('materials', 'research'), ('instrument', 'l'), ('History', 'Day'), ('l', 'Instrument'), ('landing', 'system')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure likelihood_ratio --freq 20 --n 2`
>('With', 'regard'), ('specific', 'programs'), (')', 'With'), ('pro', 'Sec'), ('Provided', 'further'), ('in', 'this'), ('a', ')'), ('(', 'a'), ('regard', 'to'), ('appropriated', 'in')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure raw_freq --freq 20 --n 2`
>(',', '000'), ('in', 'this'), ('Sec', '.'), ('to', 'the'), ('.', '('), ('(', 'a'), ('a', ')'), (')', 'With'), (',', 'pro'), ('.', '8006')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure pmi --freq 10 --n 3`
>('air', 'traffic', 'control'), ('control', 'facilities', 'replacement'), ('traffic', 'control', 'facilities'), ('Pro', 'Marcus', 'Autism'), ('Terminal', 'air', 'traffic'), ('surface', 'transportation', 'emergency'), ('transportation', 'emergency', 'prepare'), ('Disaster', 'Preparedness', 'Train'), ('hel', 'Parents', 'Anonymous'), ('national', 'parent', 'hel')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure likelihood_ratio --freq 10 --n 3`
>(',', '000', ','), (',', 'That', ','), (',', 'of', 'the'), (',', '268', ','), (',', '223', ','), (',', '095', ','), (',', '843', ','), (',', '507', ','), (',', '889', ','), (',', '295', ',')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure raw_freq --freq 10 --n 3`
>('(', 'a', ')'), ('.', '(', 'a'), (')', 'With', 'regard'), ('.', '8006', '.'), ('8006', '.', '('), ('Sec', '.', '8006'), ('With', 'regard', 'to'), ('a', ')', 'With'), ('list', 'of', 'specific'), ('of', 'specific', 'programs')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure pmi --freq 20 --n 3`
>('advanced', 'materials', 'research'), ('instrument', 'l', 'Instrument'), ('l', 'Instrument', 'landing'), ('Instrument', 'landing', 'system'), ('landing', 'system', 'establishment'), ('National', 'History', 'Day'), ('explanatory', 'statement', 'referenced'), ('not', 'less', 'than'), ('There', 'is', 'hereby'), ('any', 'other', 'provision')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure likelihood_ratio --freq 20 --n 3`
>(',', '000', ','), (',', 'That', ','), (',', 'of', 'the'), (',', '268', ','), (',', '223', ','), (',', '095', ','), (',', '843', ','), (',', '507', ','), (',', '889', ','), (',', '295', ',')]

`python identify_common_ngrams.py --file 2010-appropriations-earmark-extract.csv --measure raw_freq --freq 20 --n 3`
>('(', 'a', ')'), ('.', '(', 'a'), (')', 'With', 'regard'), ('.', '8006', '.'), ('8006', '.', '('), ('Sec', '.', '8006'), ('With', 'regard', 'to'), ('a', ')', 'With'), ('list', 'of', 'specific'), ('of', 'specific', 'programs')]
