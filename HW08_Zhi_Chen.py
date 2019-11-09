'''
HW08
@author 
'''

from datetime import datetime, timedelta
import os
from prettytable import PrettyTable
from collections import defaultdict

#part1: Date Arithmetic Operations
def date_arithmetic():
    """ 
    What is the date three days after Feb 27, 2000?
    What is the date three days after Feb 27, 2017?
    How many days passed between Jan 1, 2017 and Oct 31, 2017?

    """
    dt02272000 = datetime.strptime("Feb 27, 2000", "%b %d, %Y")
    dt02272017 = datetime.strptime("Feb 27, 2017", "%b %d, %Y")
    dt01012017 = datetime.strptime("Jan 1, 2017", "%b %d, %Y")
    dt10312017 = datetime.strptime("Oct 31, 2017", "%b %d, %Y")
    three_days_after_02272000 = (dt02272000 + timedelta(3)).strftime("%b %d, %Y")
    three_days_after_02272017 = (dt02272017 + timedelta(3)).strftime("%b %d, %Y")

    days_passed_01012017_10312017 = (dt10312017 - dt01012017).days

    return three_days_after_02272000, three_days_after_02272017, days_passed_01012017_10312017

#part2: field separated file reader
def file_reading_gen(path, fields, sep=',', header=False):
    """
    Reading text files with a fixed number of fields, separated by a pre-defined character, is a common task.
    """
    try:
        file = open(path, 'r')  
    except FileNotFoundError:
        print(f"Can't open {path}")
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
                    raise ValueError(f"‘{path}’ has {len(result)} fields on line {num} but expected {fields}")
                
                num += 1
                yield tuple(result)

#part3: Scanning directories and files
class FileAnalyzer:
    """ 
    FileAnalyzer that given a directory name, searches that directory for Python files

    """
    def __init__(self, directory):
        self.directory = directory  
        self.files = os.listdir(self.directory)
        self.files_summary = defaultdict(lambda: defaultdict(int))

    def analyze_files(self):
        for file in self.files:
            try:
                os.chdir(self.directory) 
                fl = open(file, 'r')
            except FileNotFoundError:
                print(f"cannot open {file}")
            else:

                if os.path.splitext(file)[1] == '.py':
                    
                    with fl:
                        for line in fl:

                            if line.startswith('class '):
                                self.files_summary[file]['class'] += 1
                            elif line.lstrip().startswith('def '):
                                self.files_summary[file]['function'] += 1

                            self.files_summary[file]['line'] += 1
                            self.files_summary[file]['char'] += len(line)
                else:
                    raise FileNotFoundError("{file} is not .py file!!")

    def pretty_print(self):
        pretty = PrettyTable(field_names=['File Name', 'Classes', 'Functions', 'Lines', 'Characters'])

        for filename in self.files_summary.keys():
            pretty.add_row([filename,
                        self.files_summary[filename]['class'],
                        self.files_summary[filename]['function'],
                        self.files_summary[filename]['line'],
                        self.files_summary[filename]['char'],
                        ])

        return pretty
