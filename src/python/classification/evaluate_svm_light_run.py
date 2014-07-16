import os, sys

USAGE = "python %s <gold-standard-file> <predictions-file>" %(sys.argv[0])

class Evaluation:
    def __init__(self):
        self.correct = 0
        self.incorrect = 0
        self.precision = 0
        self.recall = 0
        self.tpr = 0
        self.fpr = 0
        self.fmeasure = 0

def evaluate_run(gold, predicted):
    positive = Evaluation()
    negative = Evaluation()
    if len(gold) != len(predicted):
        raise Exception("gold and predicted are not of the same size")
    for item in zip(gold,predicted):
        if item[0][0] == '-' and  item[1][0] == '-':
            #correctly predicted negative class
            negative.correct += 1
        elif item[0][0] != '-' and item[1][0] != '-':
            #correctly predicted positive class
            positive.correct += 1
        elif item[0][0] == '-' and item[1][0] != '-':
            #negative class, that was mistaken as positive
            negative.incorrect += 1
        else:
            positive.incorrect += 1

    print "positive.correct=%d\tpositive.incorrect=%d\tnegative.correct=%d\tnegative.incorrect=%d" %(positive.correct, positive.incorrect, negative.correct, negative.incorrect)
    if positive.correct > 0:
        # by default it's zero, so only change it if there are correct predictions
        positive.precision = positive.correct / float(positive.correct + negative.incorrect)
    positive.recall = positive.correct / float( positive.correct + positive.incorrect)
    if positive.correct > 0:
        positive.fmeasure = 2 * positive.precision * positive.recall / (positive.precision + positive.recall)
    if negative.correct > 0:
        negative.precision = negative.correct / float(negative.correct + positive.incorrect)
    negative.recall = negative.correct / float(negative.correct + negative.incorrect)
    if negative.correct > 0:
        negative.fmeasure = 2 * negative.precision * negative.recall / (negative.precision + negative.recall)
    positive.tpr = positive.correct / float(positive.correct + positive.incorrect)
    positive.fpr = negative.incorrect / float (negative.incorrect + negative.correct )
    negative.tpr = negative.correct / float( negative.correct + negative.incorrect )
    negative.fpr = positive.incorrect / float ( positive.correct + positive.incorrect )
    return positive, negative


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print USAGE
    else:
        gold = [line.strip() for line in open(sys.argv[1]).readlines() ]
        predicted = [line.strip() for line in open(sys.argv[2]).readlines()]
        positive, negative = evaluate_run(gold, predicted)
        print "TPR\tFPR\tPrec\tRecall\tFMeas\tClass "
        print "%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s" %(positive.tpr, positive.fpr, positive.precision, positive.recall, positive.fmeasure, "Positive")
        print "%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s" %(negative.tpr, negative.fpr, negative.precision, negative.recall, negative.fmeasure, "Negative")
        print "WSS: %.3f" %(float(negative.correct + positive.incorrect) / len(gold) - (1- positive.recall)  )
