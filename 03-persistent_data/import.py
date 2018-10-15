import sqlite3
from scorelib import *


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def insert_object(conn, table, columns, record):
    question_marks = ("?, " * len(record))[:-2]
    sql_query = 'INSERT INTO %s %s VALUES (%s)' % (table, columns, question_marks)
    cursor = conn.cursor()
    cursor.execute(sql_query, record)
    return cursor.lastrowid


def update_object(connection, table, columns, record, condition):
    columns_w_qmarks = " = ?, ".join(columns) + " = ?"
    sql = 'UPDATE %s SET %s WHERE %s = ?' % (table, columns_w_qmarks, condition)
    cur = connection.cursor()
    cur.execute(sql, record)


def list_table(table):
    conn = sqlite3.connect("scorelib.dat")
    curs = conn.cursor()
    curs.execute("SELECT * FROM %s" % (table))
    rows = curs.fetchall()
    for row in rows:
        print(row)


def create_tables(conn, sqlFile):
    qry = open(sqlFile, 'r').read()
    sqlite3.complete_statement(qry)
    c = conn.cursor()
    c.executescript(qry)
    conn.commit()


def store_person(conn, author, stored_people):
    if author.name not in stored_people:
        #new record
        author_id = insert_object(conn, "person",
                                 ("born", "died", "name"),
                                 (author.born, author.died, author.name))
        stored_people[author.name] = author_id
    else:
        #already stored, just update
        author_id = stored_people[author.name]
        author_born = author.name + '_born'
        author_died = author.name + '_died'

        if (author_born not in stored_people):
            if (author_died not in stored_people):
                update_object(conn, 'person', ('born', 'died'), (author.born, author.died, author_id), 'id')
                stored_people[author_born] = author.born
                stored_people[author_died] = author_died
            else:
                update_object(conn, 'person', ('born'), (author.born, author_id), 'id')
                stored_people[author_born] = author.born

        else:
            if (author_died not in stored_people):
                update_object(conn, 'person', ('died'), (author.died, author_id), 'id')
                stored_people[author_died] = author_died
    return author_id


def store_to_db(conn, prints):
    saved_scores = {}
    stored_people = {}
    for print in prints:
        composition = print.composition()

        if (composition.name not in saved_scores):
            score_id = insert_object(conn, 'score',
                                    ('name', 'genre', 'key', 'incipit', 'year'),
                                    (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
            saved_scores[composition.name] = score_id
        else:
            score_id = saved_scores[composition.name]

        if composition.voices is not None and len(composition.voices) > 0:
            for voice  in composition.voices:
                insert_object(conn, "voice",
                              ("number", "score", "range", "name"),
                              (composition.voices.index(voice), score_id, voice.range, voice.name))

        for score_author in composition.authors:
            author_id = store_person(conn, score_author, stored_people)
            if (score_author.name + '_score' not in stored_people):
                score_author_id = insert_object(conn, 'score_author',
                                                ("score", "composer"),
                                                (score_id, author_id))
                stored_people[score_author.name + '_score'] = score_author_id

        edition = print.edition
        edition_id = insert_object(conn, 'edition',
                                 ('score', 'name', 'year'),
                                 (score_id, edition.name, composition.year))

        for edition_author in edition.authors:
            author_id = store_person(conn, edition_author, stored_people)
            if (edition_author.name + '_edition' not in stored_people):
                edition_author_id = insert_object(conn, 'edition_author',
                                                ("edition", "editor"),
                                                (edition_id, author_id))
                stored_people[edition_author.name + '_edition'] = edition_author_id


        insert_object(conn, 'print',
                     ('id', 'partiture', 'edition'),
                     (print.print_id, 'Y' if print.partiture else "N", edition_id))



conn = create_connection("scorelib.dat")
create_tables(conn, "scorelib.sql")

prints = load("scorelib.txt")
store_to_db(conn, prints)
conn.commit()

list_table("edition_author")


conn.close
print("-----------finished------------------")


