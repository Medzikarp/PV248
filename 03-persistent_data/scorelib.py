import re


class Voice:
    def __init__(self):
        self.range = None
        self.name = None

    def __str__(self):
        voiceRange = (self.range if self.range else '')
        voiceSeparator = (', ' if self.range and self.name else '')
        voiceName = (self.name if self.name else '')
        return voiceRange + voiceSeparator + voiceName


class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None

    def __str__(self):
        age = ""
        if self.born is not None:
            if self.died is not None:
                age = ' ({born}--{died})'.format(born = self.born, died = self.died)
            else:
                age = ' ({born}--)'.format(born = self.born)
        else:
            if self.died is not None:
                age = ' (--{died})'.format(died = self.died)
        return self.name + age


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

    def format(self):
        print('Print Number:', self.print_id)
        print('Composer:', '; '.join([str(composer) for composer in self.composition().authors]))
        print('Title:', self.composition().name)
        print('Genre:', self.composition().genre)
        print('Key:', self.composition().key if self.composition().key else "")
        print('Composition Year:', self.composition().year if self.composition().year else "")
        print('Publication Year: ')
        print('Edition:', self.edition.name)
        print('Editor:', ', '.join([str(editor) for editor in self.edition.authors]))
        for i,voice in enumerate(self.composition().voices):
            print('Voice ', str(i+1), ': ', voice, sep='')
        partiture = ""
        if self.partiture is not None:
            partiture = "yes" if self.partiture else "no"
        print('Partiture:', partiture)
        print('Incipit:', self.composition().incipit)
        print("")

    def composition(self):
        return self.edition.composition


def load(file):
    f = open(file, 'r')
    lines = f.read()
    result_list = []
    for single_record in lines.split("\n\n"):
        # filter out records without Print number
        if 'Print Number' in single_record:
            result_list.append(extract_record(single_record))

    result_list.sort(key=lambda x: int(x.print_id))
    return result_list


def extract_record(record):

    printNumberPattern = re.compile(r'Print Number: (\d*)', re.IGNORECASE)
    composersPattern = re.compile(r'Composer: (.*)', re.IGNORECASE)
    titlePattern = re.compile(r'Title: (.*)', re.IGNORECASE)
    genrePattern = re.compile(r'Genre: (.*)', re.IGNORECASE)
    keyPattern = re.compile(r'Key: (.*)', re.IGNORECASE)
    compositionYearPattern = re.compile(r'Composition Year.*(\d\d\d\d)', re.IGNORECASE)
    editionPattern = re.compile(r'Edition: (.*)', re.IGNORECASE)
    editorPattern = re.compile(r'Editor: (.*)', re.IGNORECASE)
    voicePattern = re.compile("Voice.*:(.*)", re.IGNORECASE)
    partiturePattern = re.compile(r'Partiture: (.*)', re.IGNORECASE)
    incipitPattern = re.compile(r'Incipit: (.*)', re.IGNORECASE)

    print_obj = Print()
    composition = Composition()
    edition = Edition()
    edition.composition = composition
    print_obj.edition = edition

    for line in record.split("\n"):
        m = re.match(printNumberPattern, line)
        if m is not None:
            print_obj.print_id = int(m.group(1))
            continue

        m = re.match(titlePattern, line)
        if m is not None:
            composition.name = m.group(1).strip()
            continue

        m = re.match(incipitPattern, line)
        if m is not None:
            if m.group(1):
                composition.incipit = m.group(1).strip()
            continue

        m = re.match(keyPattern, line)
        if m is not None:
            if m.group(1):
                composition.key = m.group(1).strip()
            continue

        m = re.match(genrePattern, line)
        if m is not None:
            if m.group(1):
                composition.genre = m.group(1).strip()
            continue

        m = re.match(compositionYearPattern, line)
        if m is not None:
            if m.group(1):
                composition.year = m.group(1)
            continue

        m = re.match(composersPattern, line)
        if m is not None:
            composition.authors = parse_composers(m.group(1))
            continue

        m = re.match(editionPattern, line)
        if m is not None:
            if m.group(1).strip():
                print_obj.edition.name = m.group(1).strip()
            continue

        m = re.match(voicePattern, line)
        if m is not None:
            voice_string = m.group(1).replace('; ', ', ')
            voice = Voice()
            names = []
            for voice_record in voice_string.split(','):
                if (voice_record.strip()):
                    if '--' in voice_record and voice.range is None:
                        voice.range = voice_record.strip()
                    else:
                        names.append(voice_record.strip())
            if len(names) > 0:
                voice.name = ', '.join(names)
            composition.voices.append(voice)
            continue

        m = re.match(partiturePattern, line)
        if m is not None:
            print_obj.partiture = get_boolean(m.group(1))
            continue

        m = re.match(editorPattern, line)
        if m is not None:
            edition.authors = parse_editors(m.group(1))
            continue

    return print_obj


def get_boolean(string):
    if 'yes' in string:
        return True
    elif 'no' in string:
        return False
    else:
        return None


def parse_composers(string):
    composers = []
    data = [i.strip() for i in string.split(';') if i.strip()]
    re_year = re.compile(r'(.*?)--?(.*)')
    for auth in data:
        person = Person()
        #match name
        m1 = re.match(r"(.*) \((.*)\)", auth)
        m2 = None
        if m1:
            name = m1.group(1).rstrip()
            m2 = re_year.search(m1.group(2))
        else:
            name = auth.rstrip()
        #match year
        if m2:
            if (m2.group(1)):
                person.born = int(m2.group(1)) if len(m2.group(1)) == 4 else None
            if (m2.group(2)):
                person.died = int(m2.group(2)) if len(m2.group(2)) == 4 else None
        else:
            if m1:
                born_match = re.match(r"\*(\d*)", m1.group(2))
                died_match = re.match(r"\+(\d*)", m1.group(2))
                person.born = int(born_match.group(1)) if not born_match is None and len(born_match.group(1)) == 4 else None
                person.died = int(died_match.group(1)) if not died_match is None and len(died_match.group(1)) == 4 else None
        person.name = name
        composers.append(person)
    return composers




def parse_editors(string):
    editors = []
    if string is None or not string:
        return editors
    string = string.strip(", ")
    s = re.split(r", ", string)

    for i in range(len(s)):
        ss = s[i].split("(")[0]
        s[i] = ss.rstrip()

    skip = False
    for i in range(len(s)):
        if skip:
            skip = False
            continue
        person = Person()
        if s[i].find(" ") != -1:
            person.name = s[i]
            editors.append(person)
        else:
            person.name = s[i] + ((", " + s[i + 1]) if i + 1 < len(s) else "")
            editors.append(person)
            skip = True
    return editors



