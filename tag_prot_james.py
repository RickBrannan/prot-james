import regex as re
from dataclasses import dataclass
from greek_normalisation.normalise import Normaliser
from unicodedata import normalize
import spacy
from morph_maps import *
import requests


@dataclass
class MorphUnit:
    bcv: str
    pos: str
    parse_code: str
    text: str
    word: str
    normalized: str
    lemma: str
    lang: str
    source: str


# MorphGNT SBLGNT
# retrieve directly from git to ensure we get the latest
github_raw_morphgnt = 'https://raw.githubusercontent.com/MorphGNT/sblgnt/master/'
morphgnt_files = ['61-Mt-morphgnt.txt', '62-Mk-morphgnt.txt', '63-Lk-morphgnt.txt', '64-Jn-morphgnt.txt',
                  '65-Ac-morphgnt.txt', '66-Ro-morphgnt.txt', '67-1Co-morphgnt.txt', '68-2Co-morphgnt.txt',
                  '69-Ga-morphgnt.txt', '70-Eph-morphgnt.txt', '71-Php-morphgnt.txt', '72-Col-morphgnt.txt',
                  '73-1Th-morphgnt.txt', '74-2Th-morphgnt.txt', '75-1Ti-morphgnt.txt', '76-2Ti-morphgnt.txt',
                  '77-Tit-morphgnt.txt', '78-Phm-morphgnt.txt', '79-Heb-morphgnt.txt', '80-Jas-morphgnt.txt',
                  '81-1Pe-morphgnt.txt', '82-2Pe-morphgnt.txt', '83-1Jn-morphgnt.txt', '84-2Jn-morphgnt.txt',
                  '85-3Jn-morphgnt.txt', '86-Jud-morphgnt.txt', '87-Re-morphgnt.txt']

# output dir
root_dir = "c:/git/RickBrannan/prot-james/"
source_dir = f"{root_dir}data/text/"
output_dir = f"{root_dir}data/morph/"

# nlp
# greek_model = "grc_proiel_sm"
greek_model = "grc_proiel_lg"
nlp = spacy.load(greek_model)

# first read in morphgnt words
morph_units = {}
word_data = {}
for filename in morphgnt_files:
    print("Processing " + filename)
    abbrev = re.sub(r'\.txt$', '', filename).split('-')[1]
    # open the file as a list of lines
    morphgnt_response = requests.get(github_raw_morphgnt + filename)
    lines = morphgnt_response.text.split('\n')
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        cols = line.split(' ')
        # word = normalize('NFKC', cols[5].strip())
        word = normalize('NFKC', cols[4].strip())
        word = re.sub(r'’$', "", word)
        morph = MorphUnit(cols[0], cols[1], cols[2], cols[3], normalize('NFKC', cols[4]), cols[5], cols[6],
                          "grc", "MorphGNT")
        morph_units[morph.bcv] = morph
        if morph.word not in word_data:
            word_data[morph.word] = {}
        key = f"{morph.pos}|{morph.parse_code}|{morph.lemma}"
        if key not in word_data[morph.word]:
            word_data[morph.word][key] = 0
        word_data[morph.word][key] += 1

# ok, let's read us some AF and slap some very provisional data together.
normalise = Normaliser().normalise
pj_counts = {'total': 0, 'tagged': 0, 'untagged': 0}
missed_words = {}
pj_filename = "prot-james.txt"
print("Processing " + pj_filename)
pj_morph_units = []
# remove first four chars and .txt extension
# open the file as a list of lines
with open(source_dir + pj_filename, "r", encoding="utf8") as f:
    pj_response = f.read()
    lines = pj_response.split('\n')
    for line in lines:
        # each line is a verse
        # remove leading and trailing whitespace
        line = line.strip()
        if line == "":
            continue
        line = re.sub(r'  +', ' ', line)
        tokens = line.split(' ')
        bcv = tokens[0]
        # run nlp on the line to get lemmatized word
        # assuming tokens in doc line up with split on space
        doc = nlp(re.sub(r"[.,;()\[\]··;’?:]", "", line))

        # crasis messes stuff up. also, if it is Latin, it could be hosed as well
        if len(doc[1:]) != len(tokens[1:]):
            print(f"{bcv}: Token count mismatch: {len(doc[1:])} vs {len(tokens[1:])}")
            for token in doc[1:]:
                print(f"{token.text} {token.lemma_} {token.pos_} {token.tag_}")

        n = 0
        for token in tokens[1:]:
            text = normalize("NFKC", token)
            n += 1
            if n < len(doc):
                nlp_token = doc[n]
            else:
                nlp_token = doc[-1]
            # removing punctuation does too much (it removes crasis)
            base_word = re.sub(r"[.,;()\[\]··;?:]", '', text)
            word = normalise(base_word)[0]
            pj_counts['total'] += 1
            if base_word in word_data:
                popular_key = lambda x: max(word_data[base_word], key=word_data[base_word].get)
                (pos, parse_code, lemma) = popular_key(word).split('|')
                auto_morph = convert_morph(nlp_token.morph)
                morph = MorphUnit(bcv, pos, parse_code, text, base_word, word, lemma, "grc", "MorphGNT")
                pj_morph_units.append(morph)
                pj_counts['tagged'] += 1
            else:
                lemma = normalize("NFKC", nlp_token.lemma_)
                if nlp_token.pos_ in pos_map:
                    pos = pos_map[nlp_token.pos_]
                    if re.search(r"^R", pos):
                        pos = get_pronoun_type(pos, nlp_token.morph)
                else:
                    pos = '??'
                    print(f"Unknown pos: {nlp_token.pos_} (from: {bcv} {base_word})")
                if nlp_token.text != base_word:
                    print(f"Greek mismatch: {bcv} {base_word} {nlp_token.text}")
                    # n += 1 # bump the token
                auto_morph = convert_morph(nlp_token.morph)
                # print(f"Word not found in MorphGNT: {word} (lemma: {lemma}, pos {pos} "
                #       f"({nlp_token.pos_}, morph {morph}))")
                morph = MorphUnit(bcv, pos, auto_morph, text, base_word, word, lemma,
                                  "grc", greek_model)
                pj_morph_units.append(morph)
                pj_counts['untagged'] += 1
                if morph.normalized not in missed_words:
                    missed_words[morph.normalized] = 0
                missed_words[morph.normalized] += 1
    # write out the morph units for this book
    with open(output_dir + pj_filename, "w", encoding="utf8") as f:
        for morph in pj_morph_units:
            f.write(f"{morph.bcv} {morph.pos} {morph.parse_code} {morph.text} {morph.word} {morph.normalized} "
                    f"{morph.lemma} {morph.lang} {morph.source}\n")

# report missed words sorted by frequency
# for key in sorted(missed_words, key=missed_words.get, reverse=True):
#     print(f"{key}\t{missed_words[key]}")

# report book_word_counts
for key in pj_counts:
    print(f"{key}\t{pj_counts[key]}")
print(f"Unique missed words: {len(missed_words)}")
