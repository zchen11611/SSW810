"""
HW11
@author Zhi Chen
"""

import os
import sqlite3
from collections import defaultdict
from prettytable import PrettyTable

class Major:

    def __init__(self, dept, directory):
        self.dept = dept
        rep = Repository(directory)

        try:
            required = rep.info_major[self.dept]["required"]
            electives = rep.info_major[self.dept]["electives"]
        except KeyError:
            raise KeyError(f"{dept} doesn't have required or electives")
        else:
            self.required = sort_courses(required)
            self.electives = sort_courses(electives)

class Student:

    def __init__(self, cwid, directory):
        self.cwid = cwid
        rep = Repository(directory)

        try:
            self.name = rep.info_student[self.cwid]["name"]
            self.dept = rep.info_student[self.cwid]["dept"]
        except KeyError:
            raise KeyError(f"{cwid} doesn't have name or dept")

        courses = list()

        for list_ in rep.info_grade:

            if self.cwid in list_:
                courses.append(list_[1])

        self.courses = sort_courses(courses)
        major = Major(self.dept, directory)
        required = major.required
        electives = major.electives
        self.remaining_required = remaining_courses(required, self.courses)

        if electives:
            self.remaining_electives = "None"

def remaining_courses(all_need, completed):
    result = list()

    for course in all_need:

        if course not in completed:
            result.append(course)

    if not result:  # if result is empty
        return "None"

    return result

def sort_courses(a_list):
    numbers = defaultdict(str)

    for course in a_list:
        numbers[int(course.split()[-1])] = course

    sorted_numbers = list(numbers.keys())
    sorted_numbers.sort()
    new_courses = list()

    for i in sorted_numbers:

        for j in numbers.keys():

            if i == j:
                new_courses.append(numbers[j])

    return new_courses

class Instructor:
    def __init__(self, cwid, directory):
        self.cwid = cwid
        rep = Repository(directory)
        self.name = rep.info_instructor[self.cwid]["name"]
        self.dept = rep.info_instructor[self.cwid]["dept"]
        self.course_student_dict = self.count_students(rep.info_grade)

    def count_students(self, a_list):
        course_students = defaultdict(int)

        for small_list in a_list:

            if self.cwid in small_list:
                course_name = small_list[1]
                course_students[course_name] += 1

        return course_students

class Repository:
    def __init__(self, directory):
        #constructor
        self.info_grade = list()
        self.info_student = defaultdict(lambda: dict())
        self.info_instructor = defaultdict(lambda: dict())
        self.info_major = defaultdict(lambda: defaultdict(list))
        self.files_summary = defaultdict(lambda: defaultdict(str))

        try:
            self.file_list = os.listdir(self.directory)
        except FileNotFoundError:
            raise FileNotFoundError(f"not found {self.directory}")

        self.analyze_files()

    def instructor_table_db(self, path):
        db = sqlite3.connect(path)
        query = "select CWID, Instructor, Dept, Course, count(*) as Students " \
                "from instructors join grades on CWID=InstructorCWID group by Course"
        pt_instructors = PrettyTable(field_names=["CWID", "Name", "Dept", "Course", "Students"])

        for cwid, name, dept, course, students in db.execute(query):
            pt_instructors.add_row([cwid, name, dept, course, students])

        print("Instructor Summary for HW10")
        print(pt_instructors)

    def analyze_files(self):
        if not {"grades.txt", "instructors.txt", "students.txt", "majors.txt"} <= set(self.file_list):
            raise FileNotFoundError("illegal input")

        os.chdir(self.directory)

        try:
            file = "students.txt"
            fp = open(file, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"cannot open {file}")
        else:
            with fp:

                for line in fp:

                    if line.startswith("CWID"):
                        continue
                    list_line = line.strip().split("\t")

                    if len(list_line) == 3:
                        cwid = list_line[0]
                        name = list_line[1]
                        dept = list_line[2]
                        self.info_student[cwid]["name"] = name
                        self.info_student[cwid]["dept"] = dept

                    else:
                        raise ValueError(f"illegal input in {file}, the line is {line}")

        try:
            file = "instructors.txt"
            fp = open(file, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"cannot open {file}")
        else:
            with fp:
                for line in fp:

                    if line.strip().startswith("CWID"):
                        continue

                    list_line = line.strip().split('\t')

                    if len(list_line) == 3:
                        cwid = list_line[0]
                        name = list_line[1]
                        dept = list_line[2]
                        self.info_instructor[cwid]["name"] = name
                        self.info_instructor[cwid]["dept"] = dept

                    else:
                        raise ValueError(f"illegal input in {file}, the line is {line}")

        try:
            file = "grades.txt"
            fp = open(file, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"not found {file}")
        else:
            all_students_cwids = list(self.info_student.keys())
            all_instructor_cwids = list(self.info_instructor.keys())
            with fp:

                for line in fp:

                    if line.startswith("StudentCWID"):
                        continue

                    list_line = line.strip().split('\t')

                    if len(list_line) == 4 and list_line[0] in all_students_cwids and \
                        list_line[-1] in all_instructor_cwids and \
                        list_line[-2] in ['A', 'A+', 'A-', 'B', 'B+', 'B-', 'C',
                                          'C+', 'C-', 'D', 'D+', 'D-', 'F']:
                        self.info_grade.append(list_line)
                    else:

                        if list_line[0] not in all_students_cwids:
                            raise ValueError(f"in {file}, unknow student")
                        elif list_line[-1] not in all_instructor_cwids:
                            raise ValueError(f"in {file}, unknow instructor")

        try:
            file = "majors.txt"
            fp = open(file, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"cannot open {file}")
        else:
            with fp:

                for line in fp:

                    if line.startswith("Major\t"):
                        continue
                    
                    list_line = line.strip().split('\t')

                    if len(list_line) == 3:

                        if list_line[1] == 'R':
                            self.info_major[list_line[0]]["required"].append(list_line[-1])
                        elif list_line[1] == 'E':
                            self.info_major[list_line[0]]["electives"].append(list_line[-1])
                        else:
                            raise ValueError(f"illegal input in {file}, the line is {line}")

                    else:
                        raise ValueError(f"illegal input in {file}, the line is {line}")

def pretty_print(directory):
    #pretty print students
    rep = Repository(directory)
    students = PrettyTable(field_names=["CWID", "Name", "Major", "Completed Courses", "Remaining Required", "Remaining Electives"])
    instructors = PrettyTable(field_names=["CWID", "Name", "Dept", "Course", "Students"])
    majors = PrettyTable(field_names=["Dept", "Required", "Electives"])

    for dept in rep.info_major.keys():
        m = Major(dept, directory)
        majors.add_row([m.dept, m.required, m.electives])

    for cwid in rep.info_student.keys():
        s = Student(cwid, directory)
        students.add_row([s.cwid, s.name, s.dept, s.courses, s.remaining_required, s.remaining_electives])

    for cwid in rep.info_instructor.keys():
        ins = Instructor(cwid, directory)

        for course in ins.course_student_dict.keys():
            instructors.add_row([ins.cwid, ins.name, ins.dept, course, ins.course_student_dict[course]])

    print("Majors Summary")
    print(majors)
    print("Student Summary")
    print(students)
    print("Instructor Summary")
    print(instructors)

def main():
    rep = Repository("/Users/chenzhi/Desktop/OneDrive - stevens.edu/SSW810/My_Code/HW11")
    rep.instructor_table_db("/Users/chenzhi/Desktop/OneDrive - stevens.edu/SSW810/My_Code/810_startup.db")

if __name__ == '__main__':
    main()
