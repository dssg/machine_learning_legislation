import os, sys

class Student:
    def __init__(self, row_dictionary, average_gpa=2, average_math=40, average_reading=40):
        self.StudentKey = int(row_dictionary['StudentKey'])
        self.ZipCode = self.try_set(row_dictionary['ZipCode'], int, 0)
        self.Gender = row_dictionary['Gender'] == 'Male'
        self.Language = row_dictionary['Language']
        self.HomeLanguage = row_dictionary['HomeLanguage']
        self.BirthCountry = row_dictionary['BirthCountry']
        self.Race = row_dictionary['Race']
        self.Food = row_dictionary['Food'] == 'Yes'
        self.ESL = row_dictionary['ESL'] == 'Yes'
        self.LEP = row_dictionary['LEP'] == 'Yes'
        self.SpecialED = row_dictionary['SpecialED'] == 'Yes'
        self.GPA = self.try_set(row_dictionary['GPA'], float, average_gpa)
        self.CatchmentSchool = self.try_set(row_dictionary['CatchmentSchool'], int, 0)
        self.ThisGradeSchoolKey = self.try_set(row_dictionary['ThisGradeSchoolKey'], int, 0)
        self.NextGradeSchoolKey = self.try_set(row_dictionary['NextGradeSchoolKey'], int, 0)
        self.EighthMathISAT = self.try_set(row_dictionary['EighthMathISAT'], int, average_math)
        self.EighthReadingISAT = self.try_set(row_dictionary['EighthReadingISAT'], int, average_math)
        self.StudentID = row_dictionary['StudentID']
        self.Latitude = self.try_set(row_dictionary['Latitude'], float,1)
        self.Longitude = self.try_set(row_dictionary['Longitude'], float, 1)
        self.AttendanceRate = self.try_set(row_dictionary['AttendanceRate'], float, 0.6)
                
    def try_set(self,variable, cast_func, default_value):
        try:
            return cast_func(variable)
        except:
            return default_value
            
    def __str__(self):
        return self.StudentID
            
        
        
        
        
        
