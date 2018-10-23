def load(file):
    f = open(file, 'r')
    lines = f.read()
    for line in lines.split("\n"):
        print(line)








load("input.txt")