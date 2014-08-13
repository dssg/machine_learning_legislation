import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
from csv import DictReader
from dao.Student import Student
from classification.instance import Instance
from classification.pipe import Pipe
import classification.pipe as pipe
from classification.prepare_earmark_data import  serialize_instances, load_instances
from cps.feature_generators.cps_feature_generator import *
import logging
import numpy
from classification.diagnostics import do_grid_search
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from pprint import pprint

def get_students(file_path):
    students = []
    for d in DictReader(open(file_path)):
        students.append(Student(d))
    return students
    
def get_instance(student1, student2):
    class_value = 0
    if student1.NextGradeSchoolKey == student2.NextGradeSchoolKey:
        class_value = 1
    i = Instance(target_class = class_value)
    i.attributes['student1'] = student1
    i.attributes['student2'] = student2
    return i
    
def serialize_student_group(students, data_folder):
    instances = []
    for i in range(len(students)):
        for j in range(i+1, len(students), 1):
            instances.append(get_instance(students[i], students[j]))
    logging.info("Created %d instances" %(len(instances)))
    if len(instances) == 0:
        logging.warn("FAILED TO GENERATE INSTANCES!")
        return
    fgs = [IsSameFeatureGenerator(fields=['ZipCode', 'Gender', 'Language', 'HomeLanguage'
    ,'BirthCountry', 'Race', 'Food', 'ESL', 'LEP', 'SpecialED','CatchmentSchool',
    'ThisGradeSchoolKey']),
    AbsoluteDifferenceFeatureGenerator(fields=['GPA', 'EighthMathISAT', 'EighthReadingISAT', 'AttendanceRate']),
    DistanceFeatureGenerator(),
    OtherFeaturesFeatureGenerator(),
    ]
    pipe = pipe = Pipe(fgs, instances, num_processes=1)
    pipe.push_all_parallel()
    serialize_instances(pipe.instances, data_folder)
    """
    print pipe.instances[0].attributes['student1']
    print pipe.instances[0].attributes['student2']
    for grp, features in pipe.instances[0].feature_groups.iteritems():
        print grp
        for name, feature in features.iteritems():
            print feature
    print "Positive: ", len([i for i in pipe.instances if i.target_class]), len(pipe.instances)
    """

def serialize_students(students, data_folder):
    student_groups = {}
    for student in students:
        if not student_groups.has_key(student.ThisGradeSchoolKey):
            student_groups[student.ThisGradeSchoolKey] = []
        student_groups[student.ThisGradeSchoolKey].append(student)
    for grp, students in student_groups.iteritems():
        if grp == 0:
            continue
        logging.info("Processing group %d with %d students" %(grp, len(students)))
        serialize_student_group(students, os.path.join(data_folder, str(grp)))

def folder_to_scipy(folder_path, feature_space = None):
    instances = load_instances(folder_path)
    x, y, feature_space = pipe.instances_to_matrix(instances, feature_space= feature_space, dense = True)
    return x, y, feature_space

def read_instances(root_dir):
    total_feature_space = set()
    folders_list = [os.path.join(root_dir, fname) for fname in os.listdir(root_dir)]
    for folder in folders_list:
        x, y, new_fs = folder_to_scipy(folder)
        for k in new_fs:
            total_feature_space.add(k)
    feature_space = {}
    total_feature_space = list(total_feature_space)
    for i in range(len(total_feature_space)):
        feature_space[total_feature_space[i]] = i
    
    all_x_y_spc = [folder_to_scipy(folder, feature_space) for folder in folders_list]
    X = numpy.concatenate( [x for x,y,z in all_x_y_spc])
    Y = numpy.concatenate( [y for x,y,z in all_x_y_spc])
    
    """
    X, Y, new_fs = folder_to_scipy(folders_list[0], feature_space)
    i = 1
    for folder in folders_list[1:]:
        x, y, new_fs = folder_to_scipy(folder, feature_space)
        X = numpy.concatenate( (X , x))
        Y = numpy.concatenate((Y , y))
        i +=1
        logging.info("Loaded %d out of %d" %(i, len(folders_list)))
    """
    #clf = svm.LinearSVC(C = 0.01)
    #param_grid = {'C': [  0.1, 0.5, 1, 4, 10, 100, 200, 500]}
    clf = RandomForestClassifier(n_estimators=10,max_depth=None, random_state = 0,max_features = 'log2', n_jobs = 5)
    param_grid = {'n_estimators' : [10,100,500], 'max_features' : ['log2'] }
    folds = 5
    do_grid_search(X, Y, folds, clf, param_grid, "roc_auc", X_test = None, y_test = None)
    
        
def main():
    parser = argparse.ArgumentParser(description='learn distance function')
    parser.add_argument('--infile', required=True, help='infile containing students')
    parser.add_argument('--n', type = int, default = 100000, help='max number of students to train on')
    parser.add_argument('--data', required=True, help='output data of serialization')
    args = parser.parse_args()
    logging.info("pid: " + str(os.getpid()))
    #serialize_students(get_students(args.infile)[:args.n], args.data)
    read_instances(args.data)
    logging.info("Done!")
        

if __name__=="__main__":
    main()
