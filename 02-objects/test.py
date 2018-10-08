import scorelib

#file_path = sys.argv[1]

prints = load("scorelib.txt")
for single_print in prints:
    single_print.format()

