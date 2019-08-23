import xml.etree.ElementTree as ET
import pprint as pp
import random, string

rnd = lambda length=10 : ''.join(random.choices(list(string.ascii_letters), k=length))
toText = lambda items : list(map(lambda item : item.text, items))

# Constant Namespace Types
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'
SUBJECT = '{http://purl.org/dc/elements/1.1/}subject'
DESCRIPTION = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'
DESCRIPTION_LOWER = '{http://purl.org/dc/elements/1.1/}description'
ALT = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Alt'
LI = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'
BAG = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'

class XMPParser(object):
    def __init__(self, path):
        # Root tag area
        self.path = path
        self.xmp = ET.parse(path)
        self.root = self.xmp.getroot()
        self.root = self.root.find(RDF)
        self.root = self.root.find(DESCRIPTION)

        # Description Tag
        # self._ready_descrition()
        # self.description = self.root.find(DESCRIPTION_LOWER)
        # if self.description:
        #     self.description = self.description.find(ALT)
        #     self.description = self.description.find(LI)
    
        # Keyword Tag
        self._ready_keywords()
        self.keywords = self.root.find(SUBJECT)
        self.keywords = self.keywords.find(BAG)

    def _ready_keywords(self):
        subject = self.root.find(SUBJECT)
        if subject:
            bag = subject.find(BAG)
            if bag:
                self.keywords = bag
            else:
                subject.append(ET.Element(BAG))
        else:
            subject = ET.Element(SUBJECT)
            subject.append(ET.Element(BAG))
            self.root.append(subject)
    
    def save(self, outpath=None):
        self.xmp.write(outpath or self.path)

    def add_keywords(self, keywords):
        elements = [ET.Element(LI) for key in keywords]
        for i, key in enumerate(elements):
            key.text = keywords[i]
        self.keywords.extend(elements)

    def add_keyword(self, keyword):
        self.add_keywords([keyword])