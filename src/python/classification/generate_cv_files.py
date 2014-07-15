# generates cross validation files for svm_light dataset with stratification
import os, sys
import random

USAGE = "python %s <input-svm-light-file> <output-folder> <num-folds>" %(sys.argv[0])

def prepare_folds(positive_examples,negative_examples, nfolds):
    folds = []
    for i in range(nfolds):
        folds.append([])
    if len(positive_examples) < len(negative_examples):
        smaller = positive_examples
        bigger = negative_examples
    else:
        smaller = negative_examples
        bigger = positive_examples
    random.shuffle(smaller)
    random.shuffle(bigger)
    for i in range(len(smaller)):
        folds[i % nfolds].append(smaller[i])
    for i in range(len(bigger)):
        folds[i % nfolds].append(bigger[i])
    for i in range(nfolds):
        random.shuffle(folds[i])
    return folds

def write_folds(folder, folds):
    for i in range(len(folds)):
        f = open(folder + "fold%d.train"%(i),'w')
        for j in range(len(folds)):
            if j == i: continue ;
            [f.write(line + '\n') for line in folds[j]]
        f.close()
        f = open(folder + "fold%d.test"%(i), 'w' )
        [f.write(line+ '\n') for line in folds[i]]
        f.close()

if __name__=="__main__":
    if (len(sys.argv) < 3 ):
        print USAGE
    else:
        examples = [line.strip() for line in open(sys.argv[1]).readlines() ]
        positive = [e for e in examples if e[0] =='1' ]
        negative = [e for e in examples if e[0] == '-' ]
        numfolds = int(sys.argv[3])
        outfolder = sys.argv[2]
        if not outfolder.endswith('/'):
            outfolder += "/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        folds = prepare_folds(positive, negative, numfolds)
        write_folds(outfolder, folds)
        
