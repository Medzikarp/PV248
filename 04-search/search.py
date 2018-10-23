import sqlite3
import sys
import json

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def get_prints(curs, person_id):
    prints_info = curs.execute('SELECT print.id, score.name, score.genre, score.key, score.incipit, score.year, edition.name, score.id, edition.id, print.partiture FROM person '
                               'JOIN score ON score.id = score_author.score '
                               'JOIN edition ON edition.score = score_author.score '
                               'JOIN print ON edition.id = print.edition '
                               'JOIN score_author ON person.id = score_author.composer '
                               'WHERE score_author.composer = ?', (person_id,)).fetchall()
    prints = []
    for print_info in prints_info:
        print = {}
        if print_info[0]:
            print["Print Number"] = print_info[0]
        if print_info[1]:
            print["Title"] = print_info[1]
        if print_info[2]:
            print["Genre"] = print_info[2]
        if print_info[3]:
            print["Key"] = print_info[3]
        if print_info[4]:
            print["Incipit"] = print_info[4]
        if print_info[5]:
            print["Composition Year"] = print_info[5]
        if print_info[6]:
            print["Edition"] = print_info[6]

        composers_info = curs.execute('SELECT * FROM person '
                                      'JOIN score_author ON person.id = score_author.composer '
                                      'WHERE score_author.score=?', (print_info[7],)).fetchall()
        if composers_info:
            composers = []
            for composer_info in composers_info:
                composer = {}
                composer["name"] = composer_info[3]
                if composer_info[1] is not None:
                    composer["born"] = composer_info[1]
                if composer_info[2] is not None:
                    composer["died"] = composer_info[2]
                composers.append(composer)
            print["Composer"] = composers


        editors_info = curs.execute('SELECT * FROM person '
                                'JOIN edition_author ON person.id = edition_author.editor '
                                'WHERE edition_author.edition=?', (print_info[8],)).fetchall()
        if editors_info:
            editors = []
            for editor_info in editors_info:
                editor = {}
                editor["name"] = editor_info[3]
                if editor_info[1] is not None:
                    editor["born"] = editor_info[1]
                if editor_info[2] is not None:
                    editor["died"] = editor_info[2]
                editors.append(editor)
            print["Editor"] = editors




        voices_info = curs.execute('SELECT * FROM voice '
                                      'WHERE score=?', (print_info[7],)).fetchall()
        if voices_info:
            voices = {}
            for voice_info in voices_info:
                voice = {}
                if voice_info[3] is not None:
                    voice["range"] = voice_info[3]
                if voice_info[4] is not None:
                    voice["name"] = voice_info[4]
                voices[voice_info[1]] = voice
            print["Voices"] = voices



            if print_info[9] == 'Y':
                print["Partiture"] = True
            else:
                print["Partiture"] = False

        prints.append(print)

    return prints

conn = create_connection("scorelib.dat")
name = sys.argv[1]

results = conn.execute("SELECT person.id, person.name "
                       "FROM person "
                       "WHERE person.name LIKE ? ", ('%'+name+'%',)).fetchall()

out = {}
for result in results:
    out[result[1]] = get_prints(conn.cursor(), result[0])

print(json.dumps(out, ensure_ascii=False, indent=4))