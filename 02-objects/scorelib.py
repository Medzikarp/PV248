import re

class Voice:
    def __init__(self):
        self.range = None
        self.name = None

class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None

class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.year = None
        self.voices = []
        self.authors = []

class Edition:
    def __init__(self):
        self.composition = Composition()
        self.authors = []
        self.name = None

class Print:
    def __init__(self):
        self.edition = Edition()
        self.print_id = None
        self.partiture = False

    def composition(self):
        return self.edition.composition

    def format(self):
        return None

def load(file):
    f = open(file, 'r')
    lines = f.read()
    result_list = []
    for single_record in lines.split("\n\n"):
        result_list.append(extract_record(single_record))

    #result_list.sort(key=lambda x: int(x.print_id))
    return result_list

def extract_record(record):
    print_obj = Print()
    return print_obj


prints = load("scorelib.txt")
for printik in prints:
    print(printik.print_id)