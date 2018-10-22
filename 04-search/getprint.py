import sqlite3
import sys
import json


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def get_print(conn, print_number):
    curs = conn.cursor()
    sql_query = 'SELECT person.name, person.born, person.died ' \
                'FROM print ' \
                'INNER JOIN edition ON edition.id = print.edition ' \
                'INNER JOIN score_author ON score_author.score = edition.score ' \
                'INNER JOIN person ON score_author.composer = person.id ' \
                'WHERE print.id = ?'
    curs.execute(sql_query, (print_number,))
    rows = curs.fetchall()
    return rows

print_number = sys.argv[1]
conn = create_connection("scorelib.dat")
results = get_print(conn, print_number)

list = []
for result in results:
    list.append({"name": result[0],
                 "born": result[1],
                 "died": result[2]})

for author in list:
    if (author["born"]) is None: author.pop("born")
    if (author["died"]) is None: author.pop("died")
    if (author["name"]) is None: author.pop("name")
print(json.dumps(list, ensure_ascii=False, indent=1))