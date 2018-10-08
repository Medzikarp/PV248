from scorelib import *
import sys


file_path = sys.argv[1]

prints = load(file_path)
for single_print in prints:
    single_print.format()

