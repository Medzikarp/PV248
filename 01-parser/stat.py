import sys
import re


def retrieve_centuries(matches):
    data = [0 for i in range(21)]
    for i in range(21):
        data[i] = 0
    for k, v in matches.items():
        year = re.search(r"(\d{4})", k)
        if year:
            data[int(year.group(0)[0:2])] += v
        else:
            year = re.search(r"(\d{2})th century", k)
            if year:
                data[int(year.group(1)) - 1] += v
    return data


def print_composers(data):
    s = [(k, data[k]) for k in sorted(data, key=data.get, reverse=True)]
    for k, v in s:
        print(k + ": " + str(v))


def print_centuries(data):
    for i in range(21):
        if data[i] is 0:
            continue
        print(str(i + 1) + "th century: " + str(data[i]))


if sys.argv[2] == "composer":
    r = re.compile(r"Composer: (.*)")
elif sys.argv[2] == "century":
    r = re.compile(r"Composition Year: (.*)")
else:
    exit()

matches = {}

for line in open(sys.argv[1], 'r'):
    m = r.match(line)
    if m:
        s = re.split(r"; ", m.group(1))
        for key in s:
            key = key.split("(", 1)[0]

            key = key.rstrip(", ")
            if key:
                if key not in matches:
                    matches[key] = 1
                else:
                    matches[key] += 1

if sys.argv[2] == "century":
    data = retrieve_centuries(matches)
    print_centuries(data)
else:
    print_composers(matches)
