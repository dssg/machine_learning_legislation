#! /bin/sh
SVM_LIGHT="/home/mkhabsa/code/cohen-paper/classification/svm_light/"
Eval_Script="/home/mkhabsa/code/cohen-paper/classification/evaluate_svm_light_run.py"
Folder=$1
$SVM_LIGHT/svm_learn -v 0 "$Folder/fold0.train" "$Folder/fold0.model"
$SVM_LIGHT/svm_learn -v 0 "$Folder/fold1.train" "$Folder/fold1.model"
$SVM_LIGHT/svm_classify -v 0 "$Folder/fold0.test" "$Folder/fold0.model" "$Folder/fold0.model.eval"
$SVM_LIGHT/svm_classify -v 0 "$Folder/fold1.test" "$Folder/fold1.model" "$Folder/fold1.model.eval"
echo "Evaluating results on model0"
python $Eval_Script $Folder/fold0.test $Folder/fold0.model.eval
echo "Evaluating results on model1"
python $Eval_Script $Folder/fold1.test $Folder/fold1.model.eval