
import prettytable as pt
import collections


class Repository:
    def __init__(self):
        self.students_list = []
        self.instructors_list = []
        self.grades_list = []

class Student:
    def __init__(self,name,dept):
        self.course_grade_dict = collections.OrderedDict()
        self.name = name
        self.dept = dept

class Instructor:
    def __init__(self,name,dept):
        self.course_numstudents_dict = collections.OrderedDict()
        self.name = name
        self.dept = dept


def read_file(filename):
    row_list = []
    file = open(filename,'r')
    for line in file:
        words = line.strip().split('\t')
        row_list.append(words)
    return row_list


def handle(directory_path):
    students_list = read_file(directory_path + 'students.txt')
    instructors_list = read_file(directory_path + 'instructors.txt')
    grades_list = read_file(directory_path + 'grades.txt')

    students_dict = collections.OrderedDict()
    instructors_dict = collections.OrderedDict()

    # create student info dict
    for row in students_list:
        [id,name,dept] = row
        students_dict[id] = Student(name,dept)

    # create instructor info dict
    for row in instructors_list:
        [id,name,dept] = row
        instructors_dict[id] = Instructor(name,dept)

    # add grades int student info dict and instructor info dict
    for row in grades_list:
        [stu_id,course_name,grade,ins_id]=row
        students_dict[stu_id].course_grade_dict[course_name] = grade

        if course_name not in instructors_dict[ins_id].course_numstudents_dict:
            instructors_dict[ins_id].course_numstudents_dict[course_name]=0
        instructors_dict[ins_id].course_numstudents_dict[course_name] += 1


    res = ''
    # show student info table
    tb = pt.PrettyTable(['CWID','Name','Completed Courses'])
    for id,stu in students_dict.items():
        complete_courses_list = [course for course in stu.course_grade_dict]
        tb.add_row([id,stu.name,complete_courses_list])
    #print(tb)
    res += str(tb)+'\n'

    # show instructor info table
    tb = pt.PrettyTable(['CWID','Name','Dept','Course','Students'])
    for ins_id,ins in instructors_dict.items():
        for course,numstudents in instructors_dict[ins_id].course_numstudents_dict.items():
            tb.add_row([ins_id,ins.name,ins.dept,course,numstudents])

    #print(tb)
    res += str(tb)+'\n'

    return res


if __name__ == '__main__':

    result = handle('')
    print(result)



