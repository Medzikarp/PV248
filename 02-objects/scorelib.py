import re

class Voice:
    def __init__(self):
        self.range = ""
        self.name = ""

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
        print('Key:', self.composition().key if self.composition().key is not None else "")
        print('Composition Year:', self.composition().year if self.composition().year else "")
        print('Publication Year: ')
        print('Edition:', self.edition.name)
        print('Editor:', ''.join([str(editor) for editor in self.edition.authors]))
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
            composition.name = m.group(1)
            continue

        m = re.match(incipitPattern, line)
        if m is not None:
            composition.incipit = m.group(1).split(',')[0]
            continue

        m = re.match(keyPattern, line)
        if m is not None:
            composition.key = m.group(1).strip()
            continue

        m = re.match(genrePattern, line)
        if m is not None:
            composition.genre = m.group(1)
            continue

        m = re.match(compositionYearPattern, line)
        if m is not None:
            composition.year = m.group(1)
            continue

        m = re.match(composersPattern, line)
        if m is not None:
            composition.authors = parse_people(m.group(1))
            continue

        m = re.match(editionPattern, line)
        if m is not None:
            print_obj.edition.name = m.group(1)
            continue

        m = re.match(voicePattern, line)
        if m is not None:
            voice = Voice()
            names = []
            for voice_record in m.group(1).split(','):
                if '--' in voice_record:
                    voice.range = voice_record.strip()
                else:
                    names.append(voice_record.strip())
            voice.name = ', '.join(names)
            composition.voices.append(voice)
            continue

        m = re.match(partiturePattern, line)
        if m is not None:
            print_obj.partiture = get_boolean(m.group(1))
            continue

        m = re.match(editorPattern, line)
        if m is not None:
            edition.authors = parse_people(m.group(1))
            continue

    return print_obj


def get_boolean(string):
    if 'yes' in string:
        return True
    elif 'no' in string:
        return False
    else:
        return None


def parse_people(string):
    data = [i.strip() for i in string.split(';') if i.strip()]
    res = []
    re_year = re.compile(r'\(([0-9]{4})?--([0-9]{4})?\)')
    for auth in data:
        person = Person()
        match = re_year.search(auth)
        if match:
            if (match.group(1)):
                person.born = int(match.group(1))
            if (match.group(2)):
                person.died = int(match.group(2))
        auth = re_year.sub('', auth).strip()
        person.name = auth
        res.append(person)
    return res
