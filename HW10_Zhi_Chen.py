'''
HW10
@author Zhi Chen
'''

import prettytable as pt
import collections
import os

#part2: field separated file reader
def file_reading_gen(path, fields, sep=',', header=False):
    """
    Reading text files with a fixed number of fields, separated by a pre-defined character, is a common task.
    """
    try:
        file = open(path, 'r')  
    except FileNotFoundError:
        print("Can't open %s"%(path))
    else:
        num = 0  # number of line
        with file:
            for line in file:
                if header:  
                    header = False
                    num += 1
                    continue
                result = line.strip().split(sep) 
                if len(result) != fields:
                    raise ValueError("%s has %d fields on line %d but expected %d"%(path,len(result),num,fields))
                
                num += 1
                yield tuple(result)



class Repository:
    def __init__(self, root_dir=""):

        # create 4 path
        self.students_file_path = os.path.join(root_dir,"students.txt")
        self.instructors_file_path = os.path.join(root_dir,"instructors.txt")
        self.grades_file_path = os.path.join(root_dir,"grades.txt")
        self.majors_file_path = os.path.join(root_dir,"majors.txt")

        self.handle_majors_file()
        self.handle_student_instructors_file()
        self.handle_grades_file()



    def show(self):
        print('Majors Summary')
        print(self.show_majors_file())

        print('Student Summary')
        print(self.show_student_summary())

        print('Instructor Summary')
        print(self.show_instructor_summary())



    def handle_majors_file(self):
        
        self.major_dict={}
        try:
            majors_list = list(file_reading_gen(self.majors_file_path,3,sep = '\t',header = True))
        except Exception as e:
            print(e)
            return
        for (major,re,course) in majors_list:
            if major not in self.major_dict:
                # the flag has the value 'R' if the course is a required course 
                # the flag has the value 'E' if the course is an elective for that major
                self.major_dict[major]={'R':[],'E':[]}
            if re not in self.major_dict[major]:
                print('known type')
            else:
                self.major_dict[major][re].append(course)

    def show_majors_file(self):

        table_str=''
        tb = pt.PrettyTable(['Dept','Required','Electives'])
        for dept,re_dict in self.major_dict.items():
            re_dict['R'].sort()
            re_dict['E'].sort()
            tb.add_row([dept,re_dict['R'],re_dict['E']])
        table_str=str(tb)+'\n'

        return table_str

    def handle_student_instructors_file(self):

        self.students_id_dict = {}
        self.instructors_id_dict={}

        # create students dicitonary from file
        try:
            students_list = list(file_reading_gen(self.students_file_path,3,sep = ';',header = True))
        except Exception as e:
            print(e)
            return
        for (id,name,dept) in students_list:
            self.students_id_dict [id] = Student(name,dept)

        # create instructors dicitonary from file
        try:
            instructors_list = list(file_reading_gen(self.instructors_file_path,3,sep = '|',header = True))
        except Exception as e:
            print(e)
            return
        for (id,name,dept) in instructors_list:
            self.instructors_id_dict [id] = Instructor(name,dept)

    def show_student_summary(self):
        pass

        tb = pt.PrettyTable(['CWID','Name','Major','Complete Courses','Remianing Required','Remaining Electives'])

        # loop through each student
        for sid,stu in self.students_id_dict.items():
            if stu.dept in self.major_dict:
                complete_course = []
                all_r_course_set = set(self.major_dict[stu.dept]['R'])
                all_e_course_set = set(self.major_dict[stu.dept]['E'])

                # loop through each grade
                for course,grade in stu.course_grade_dict.items():
                    # Any student earning less than a 'C' must repeat the course until earning at least a 'C'
                    if grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']:
                        if course in all_r_course_set:
                            all_r_course_set.remove(course)
                        if course in all_e_course_set:
                            all_e_course_set=set()
                        complete_course.append(course)
                # list 3 kinds of list

                # a sorted list of the courses
                r_course_list = list(all_r_course_set)
                e_course_list = list(all_e_course_set)
                r_course_list.sort()
                e_course_list.sort()
                complete_course.sort()

                tb.add_row([sid,stu.name,stu.dept,complete_course if complete_course else None,r_course_list if r_course_list else None,e_course_list if e_course_list else None])

            else:
                print("unknown major %s"%stu.dept)


        ret = str(tb)+'\n'
        return ret

    def show_instructor_summary(self):

        record_list = []
        # loop through each instructor
        for iid,ins in self.instructors_id_dict.items():
            for course,lst in ins.course_studentlist_dict.items():
                record = [iid,ins.name,ins.dept,course,len(lst)]
                record_list.append(record)

        tb = pt.PrettyTable(['CWID','Name','Dept','Course','Students'])
        for record in record_list:
            tb.add_row(record)

        ret = str(tb)+'\n'
        return ret

    def handle_grades_file(self):
        try:
            grades_list = list(file_reading_gen(self.grades_file_path,4,sep = '|',header = True))
        except Exception as e:
            print(e)
            return

        # loop through all the record in grade list
        for (sid,course,grade,iid) in grades_list:
            if sid in self.students_id_dict:
                self.students_id_dict[sid].course_grade_dict[course] = grade
            else:
                print("unknown student id: %s"%sid)

            if iid in self.instructors_id_dict:                
                if course not in self.instructors_id_dict[iid].course_studentlist_dict:
                    self.instructors_id_dict[iid].course_studentlist_dict[course]=[]
                self.instructors_id_dict[iid].course_studentlist_dict[course].append(sid)
            else:
                print("unknown instructor id: %s"%iid)
        pass



class Student:
    def __init__(self,name,dept):
        self.course_grade_dict = {}
        self.name = name
        self.dept = dept

class Instructor:
    def __init__(self,name,dept):
        self.course_studentlist_dict = {}
        self.name = name
        self.dept = dept


def main():
    ''' a main() routine to run the whole thing '''

    rep = Repository()
    rep.show()


if __name__=="__main__":
    main()

