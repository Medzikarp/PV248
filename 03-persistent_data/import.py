import sqlite3
from scorelib import *
import sys


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

    author_born = author.name + '_born'
    author_died = author.name + '_died'

    if author.name not in stored_people:
        #new record
        author_id = insert_object(conn, "person",
                                  ("born", "died", "name"),
                                  (author.born, author.died, author.name))
        stored_people[author.name] = author_id
        if author.born:
            stored_people[author_born] = author.born
        if author.died:
            stored_people[author_died] = author_died
    else:
        #already stored, just update
        author_id = stored_people[author.name]

        if (author_born not in stored_people and author.born is not None):
            if (author_died not in stored_people and author.died is not None):
                update_object(conn, 'person', ('born', 'died'), (author.born, author.died, author_id), 'id')
                stored_people[author_born] = author.born
                stored_people[author_died] = author_died
            else:
                update_object(conn, 'person', ('born',), (author.born, author_id), 'id')
                stored_people[author_born] = author.born

        else:
            if (author_died not in stored_people and author.died is not None):
                update_object(conn, 'person', ('died',), (author.died, author_id), 'id')
                stored_people[author_died] = author_died
    return author_id


def same_voices(curs, voices, score_id) :
    curs.execute("SELECT number, range, name FROM voice "
                 "WHERE score = (?) ORDER BY number", (score_id, ))
    stored_voices = curs.fetchall()
    if len(stored_voices) != len(voices):
        return False
    for i in range(0, len(voices)):
        if stored_voices[i][1] != voices[i].range or stored_voices[i][2] != voices[i].name:
            return False
    return True





def store_score(conn, name, genre, key, incipit, year, voices, authors):

    curs = conn.cursor()
    curs.execute('SELECT id, genre, key, incipit, year FROM score '
                 'WHERE score.name = ? ', (name, ))

    stored_score = curs.fetchall()
    if stored_score:
        for score in stored_score:
            if score[1] == genre and score[2] == key and score[3] == incipit and score[4] == year:
                if same_voices(curs, voices, score[0]) and same_score_authors(curs, authors, score[0]):
                    return score[0]
    return insert_object(conn, 'score',
                         ('name', 'genre', 'key', 'incipit', 'year'),
                         (name, genre, key, incipit, year))


def store_edition(conn, score_id, name, editors):
    curs = conn.cursor()
    curs.execute("SELECT id, name FROM edition WHERE score = (?)", (score_id, ))
    editions = curs.fetchall()
    if editions is not None:
        for edition in editions:
            if name == edition[1] and same_edition_authors(curs, editors, edition[0]):
                return edition[0]

    return insert_object(conn, 'edition',
                         ('score', 'name', 'year'),
                         (score_id, name, None))

def same_edition_authors(curs, authors, editor_id):
    sql_query = 'SELECT name FROM edition_author INNER JOIN person ON edition_author.editor = person.id WHERE edition = (?)'
    curs.execute(sql_query , (editor_id, ))
    authors_names = [i[0] for i in curs.fetchall()]
    return same_authors(authors_names, authors)


def same_score_authors(curs, authors, score_id):
    sql_query = 'SELECT name FROM score_author INNER JOIN person ON score_author.composer = person.id WHERE score = (?)'
    curs.execute(sql_query , (score_id, ))
    authors_names = [i[0] for i in curs.fetchall()]
    return same_authors(authors_names, authors)

def same_authors(authors_names, authors):
    if len(authors_names) != len(authors):
        return False
    self_authors_names = []
    for a in authors:
        self_authors_names.append(a.name)
    return sorted(self_authors_names) == sorted(authors_names)


def store_to_db(conn, prints):
    stored_people = {}
    for print in prints:
        composition = print.composition()

        score_id = store_score(conn, composition.name, composition.genre, composition.key, composition.incipit, composition.year, composition.voices, composition.authors)


        if composition.voices is not None and len(composition.voices) > 0:
            for voice in composition.voices:
                insert_object(conn, "voice",
                              ("number", "score", "range", "name"),
                              (composition.voices.index(voice) + 1, score_id, voice.range, voice.name))

        for score_author in composition.authors:
            author_id = store_person(conn, score_author, stored_people)
            insert_object(conn, 'score_author',
                          ("score", "composer"),
                          (score_id, author_id))

        edition = print.edition
        edition_id = store_edition(conn, score_id, edition.name, edition.authors)


        for edition_author in edition.authors:
            author_id = store_person(conn, edition_author, stored_people)
            insert_object(conn, 'edition_author',
                            ("edition", "editor"),
                            (edition_id, author_id))


        insert_object(conn, 'print',
                     ('id', 'partiture', 'edition'),
                     (print.print_id, 'Y' if print.partiture else "N", edition_id))



conn = create_connection(sys.argv[2])
create_tables(conn, "scorelib.sql")
prints = load(sys.argv[1])
store_to_db(conn, prints)
conn.commit()
conn.close
