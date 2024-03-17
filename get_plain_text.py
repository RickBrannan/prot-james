'''
Code to retrieve plain-text of ProtJames from OpenText.org's "Base" XML.
OpenText.org Base XML for ProtJames: https://raw.githubusercontent.com/OpenText-org/non_NT_annotation/master/proto-james/base/proto-james.xml
Rick Brannan 2024-03-17
'''
import regex as re
from dataclasses import dataclass
from lxml import etree
from greek_normalisation.normalise import Normaliser
from unicodedata import normalize
import requests


@dataclass
class Word:
    bcv: str
    word: str
    before: str
    after: str

base_dir = "C:/git/RickBrannan/prot-james/data/"

# use requests so if others use they'll just get the correct file and I won't have to host it.
response = requests.get('https://raw.githubusercontent.com/OpenText-org/non_NT_annotation/master/proto-james/base/proto-james.xml')

# Parse the XML
prot_james_xml = etree.fromstring(response.content)
# prot_james_root = prot_james_xml.getroot()
with open(base_dir + "text/prot-james.txt", "w", encoding="utf-8") as outfile:
    for chapter in prot_james_xml.xpath('.//chapter'):
        chapter_num = chapter.get('num')
        for verse in chapter.xpath('.//verse'):
            verse_num = verse.get('num')
            bcv = "PJ." + chapter_num + "." + verse_num
            words = []
            print(f"Processing {bcv}")
            for item in verse.xpath('./*'):
                if item.tag == "w":
                    word_num = re.sub(r"^.*\.w(\d+)$", r"\1", item.get('id'))
                    word_text = item.xpath("./wf")[0].text
                    if word_text is None:
                        continue
                    # print(f"{bcv} {word_num}: {word_text}")
                    word_text = re.sub(r"^ *᾽(.)", r'\1' + '̓', word_text)
                    word_text = re.sub(r"᾽$", r"’", word_text)
                    word_text = normalize("NFKC", word_text)
                    word = Word(bcv, word_text, "", " ")
                    words.append(word)
                elif item.tag == "punc":
                    words[-1].after = item.text + " "
                elif item.tag == "mark":
                    if item.text == "(":
                        words[-1].before = item.text
                    elif item.text == ")":
                        words[-1].after = item.text + " "
                    else:
                        print(f"Unknown mark: {item.text}")
                else:
                    print(f"Unknown tag: {item.tag}")
            # write out as plain text
            outfile.write(bcv + " ")
            for word in words:
                outfile.write(f"{word.before}{word.word}{word.after}")
            outfile.write("\n")
print("Done")


