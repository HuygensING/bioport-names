# coding=utf-8
from lxml import etree 
from lxml.etree import Element, SubElement
from common import (STOP_WORDS, TUSSENVOEGSELS, ROMANS, PREFIXES,
                    serialize, remove_parenthesized, html2unicode, to_ascii,
                    POSTFIXES, fix_capitals, VOORVOEGSELS, TERRITORIALE_TITELS, 
                    coerce_to_unicode)
#from similarity import  soundexes_nl
#from plone.memoize import instance
from names.soundex import soundexes_nl
from names.common import R_ROMANS
import re
#import cPickle

wordsplit_re = re.compile('\w+')
STOP_WORDS_frozenset = frozenset(STOP_WORDS)
VOORVOEGSELS_EN_TERRITORIALE_TITELS = frozenset(VOORVOEGSELS + TERRITORIALE_TITELS)

def cached(method):
    def wrapper(*args, **kwargs):
        # only cache default calls
        if hasattr(args[0], '_cache') and len(args) == 1 and len(kwargs) == 0:
            return args[0]._cache[method.__name__]
        else:
            return method(*args, **kwargs)
    wrapper._cache_decorated_method = True
    wrapper.__name__ = method.__name__
    return wrapper

class Name(object):
    """The name of a person
    
    this class contains different functions for analyzing and printing the name
    """
    _constituents = [
        'prepositie',   #preposition
        'voornaam',     #first name
        'intrapositie', #intraposition
        'geslachtsnaam',#last name
        'postpositie',  #postposition
 #       'territoriale_titel',
    ]
   
    def __init__(self, naam=None, **args):
        self._root = None #etree.Element object met naamgegevens
        if naam:
            args['volledige_naam'] = naam
        if args:
            self.from_args(**args)
   
    def __str__(self):
        val = self.volledige_naam()
        if isinstance(val, unicode):
            return val.encode('ascii', 'replace')
        return val
    
    def __repr__(self):
        return '<Name %s>' % self.__str__()
    
    def __eq__(self, other):
        return self.to_string() == other.to_string()
    
    def x__ne__(self, other):
        return self.to_string() != other.to_string()
    
    def from_args(self, **args):
        volledige_naam = args.get('volledige_naam', '')
        self.sort_name = args.get('sort_name', None)
        #store the data as an xml Element
        ### Create an XML structure
        self._root = Element('persName')
        last_element = None
        if volledige_naam:
#            volledige_naam = html2unicode(volledige_naam)
            self._root.text = volledige_naam
#            self._insert_constituent('geslachtsnaam', args.get('geslachtsnaam'))
            for c in self._constituents:
                self._insert_constituent(c, args.get(c))
#                
            for c in ['territoriale_titel']:
                if args.get(c):
                    el = SubElement(self._root, 'name')
                    el.set('type', c)
                    el.text = args.get(c)
                    if last_element is not None:
                        last_element.tail = ',  '
                    else:
                        self._root.text +=  ', '
                    last_element = el                
        else:
            for c in self._constituents:
                if args.get(c):
                    el = SubElement(self._root, 'name')
                    el.set('type', c)
                    el.text = args.get(c)
#                    el.text = html2unicode(args.get(c))
                    if last_element is not None:
                        last_element.tail = ' '
                    last_element = el

        return self

    def html2unicode(self):
        """convert all html-type character codes to proper unicode"""
        s = self.to_string()
        s = html2unicode(s)
        self.from_string(s)
        return self
    def _insert_constituent(self, type, s):
        """tag the substring s of volledige_naam as being of type type
        
        arguments:
            type : one of ['prepositie', 'voornaam', etc]
            s : a string (must be a substring of self.volledige_naam())
            
        e.g.:
            
        """     
        if not s:
            return
        text = self._root.text
        new_el = Element('name')
        new_el.set('type', type)
        new_el.text = s
       
        #these are candidate strings to replace
        candidate_strings = [self._root.text] + [n.tail for n in self._root]
        for i in range(len(candidate_strings)):
            text = candidate_strings[i]
            #find word starting at word boundary (i.e. as alphanumeric, and ending in space of endofline
            m = re.search(r'\b%s(?=\s)|\b%s\Z|\b%s\b' % (s,s,s), text)
            
            if m:
                before = text[:m.start()]
                after = text[m.end():]
                if i == 0:
                    self._root.text = before 
                else:
                    self._root[i-1].tail = before 
                self._root.insert(i,new_el)
                new_el.tail =  after 
                return
        msg = 'The string "%s" (of type %s) should be a part of the volledige naam %s' % (s, type, candidate_strings)
        raise Exception(msg)
    
    def from_string(self, s):
        try:
            element =  etree.fromstring(s)
        except etree.XMLSyntaxError, err:
            if 'Entity' in err.message:
                #the string contains HTML Entities (probably)
                #and we provide some robustness by converting it to unicode
                s = html2unicode(s)
                element = etree.fromstring(s)
            else:
                raise 
        self.from_xml(element)
        return self
    
    def from_soup(self, s, hints=()):
        """if the input is really messy, this function should be more forgivable"""
        self.source_string = s
        self.birth = None
        self.death = None
        s = coerce_to_unicode(s)
        s = s.strip()
        
        #gevallen als Jan klaasen (123-345)
        #kijk of er jaartallen, tussen haakjes, staan
        if s.endswith(')') and s.find('('):
            laatste_haakje = s.rfind('(')
            
            tussen_haakjes = s[laatste_haakje+1:-1]
            for splitter in ['-', '\u2011', u'‑']:
                if splitter in tussen_haakjes:
                    first, last = tussen_haakjes.split(splitter)
                    
                else:
                    first = None
                    last = tussen_haakjes
                #XXX this is not really finished
                if last.isdigit():
                    self.birth = first
                    self.death = last
                    s = s[:laatste_haakje].strip()
                for att in ['birth', 'death']:
                    d = getattr(self, att)
                    if d:
                        for c in [u'±']:
                            if d.startswith(c):
                                    d = s[len(c):]
                        if not is_date(d):
                            d = None
                    setattr(self, att, d)
        #territoriale titels
        self.territoriale_titel = None
        
        for t in TERRITORIALE_TITELS:
            if t in s:
                self.territoriale_titel = s[s.find(t):]
                self.territoriale_titel= self.territoriale_titel.strip()
                s = s[:s.find(t)]
        s = s.strip()
        for c in ',;:': 
            if s.endswith(c):
                s = s[:-len(c)]
        s = s.strip()    
        
        self.from_args(
           volledige_naam = s,
           # territoriale_titel=territoriale_titel,
            )
        self.guess_geslachtsnaam(hints=hints)
        
        return self
    
    def from_xml(self, element):
        return self.from_element(element)
    
    def from_element(self, element):
        """element is een etree.Element instance"""
        self._root = element
        return self

    def get_volledige_naam(self):
        """return a string without (XML) markup in the original order""" 
        s = self.serialize(self._root).strip()
        return s

    def volledige_naam(self):
        return self.get_volledige_naam()

    def sort_key(self):
        """this value should assign the name its proper place in the alfabet
        """
#        base = u' '.join([s for s in [
#            self.geslachtsnaam(), 
##            self.prepositie(), 
#            self.voornaam(), 
#            self.intrapositie(), 
#            self.postpositie(),
#            self.serialize(self._root),
#            ] if s])
        base = self.guess_normal_form(change_xml=False)
        base = base.replace(',', '')
        base = base.strip()
        base = base.lower()
        ignore_these = '()'
        for c in ignore_these:
            base = base.replace(c, '')
            
        for s in PREFIXES: #we also strip prefixes (so "L'Eremite, B." sorts between "Eremite, A" and "Eremite, C")
            if base.startswith(s):
                base = base[len(s):]

        ls = base.split()
        for s in TUSSENVOEGSELS:
            if ls and ls[0] == s:
                base = ' '.join(ls[1:])
                
        for s in '?.-': #if the name starts with any of these characters, it comes last (not first)
            if base.startswith(s):
                base = chr(126) + base 

        
        #XXX use "to_ascii" dictionary
        base = to_ascii(base) 

        base = base.strip()
        base = base[:40]
        return base 

    def prepositie(self):
        result = self._root.xpath('./name[@type="prepositie"]/text()')
        result = ' '.join(result)
        return result

    def voornaam(self):
        result = self._root.xpath('./name[@type="voornaam"]/text()')
        result = ' '.join(result)
        return result

    def intrapositie(self):
        result = self._root.xpath('./name[@type="intrapositie"]/text()')
        result = ' '.join(result)
        return result

    #@instance.memoize # used in similarity.ratio, our most expensive function
    # unfortunately tests won't pass with this enabled, because
    # the object changes between subsequent calls to this method,
    # and memoize gives the stale result
    def geslachtsnaam(self):
        result = self._root.xpath('./name[@type="geslachtsnaam"]/text()')
        result = u' '.join(result)  
        return result
        
    def postpositie(self):
        result = self._root.xpath('./name[@type="postpositie"]/text()')
        result = u' '.join(result)
        return result

    def territoriale_titel(self):
        result = self._root.xpath('./name[@type="territoriale_titel"]/text()')
        result = u' '.join(result)
        return result
    
    def serialize(self, n = None, exclude=[]):
        if n is None: 
            n = self._root
        return serialize(n, exclude=exclude).strip()
    
    def _guess_geslachtsnaam_in_string(self, s, hints=[]):
        """Given a string s, try to find the last name
        
        returns: 
            a substring of s
        """
        name = s
            
        #anything between brackets is NOT a last name
        #(but we leave the brackets in "Ha(c)ks")
        name = re.sub(r'(?<!\w)\(.*?\)', '', name)
        name = name.strip()
        
        if ', ' in name: #als er een komma in de name staat, dan is dat wat voor de komma staat de achter
            guessed_name = name.split(', ')[0] 
        elif ' - ' in name: #a real use case: "Hees - B.P. van"
            guessed_name = name.split(' - ')[0] 
        elif 'startswithgeslachtsnaam' in hints: #er staat geen komma (ofzo) in, maar we weten wel dat de naam
            #met een achternaam begint: dan moet het wel de hele string zijn
            guessed_name = name 
        elif re.search('[A-Z]\.', name):
            #als de naam met een initiaal begint, fitleren we alle intiitale er uit, en is de rest de achternaam
#            guessed_name = name[re.match('([A-Z]\.)+',name).end():] 
            guessed_name = re.sub('(Th\.|[A-Z]\.)+','', name) 
        elif ' ' in name:
            candidates = re.split('\s+', name)
            if candidates[-1] in ROMANS:
                #if the name ends with a roman numeral, (as in "Karel II") this is often not a geslachtsnaam
                #(note American names as well, such as "John Styuivesandt III"
                guessed_name = candidates[-2]
            elif candidates[-1].isdigit():
                guessed_name = ''
            elif candidates[-1] in POSTFIXES:
                guessed_name = ' '.join(candidates[-2:])
            else:
                guessed_name = candidates[-1]  
        else:
            guessed_name = name 
            
        #een speciaal geval zijn namen van getrouwde dames, zoals 'Angela Boter-de Groot' 
        if '-' in name:
            for tussenvoegsel in TUSSENVOEGSELS:
                if '-%s' % tussenvoegsel in name:
                    i = name.find('-%s' % tussenvoegsel)
                    if i > -1:
                        guessed_name = self._guess_geslachtsnaam_in_string(name[:i], hints) 
                        guessed_name = guessed_name + name[i:] 
        guessed_name = self._strip_tussenvoegels(guessed_name)
#        for c in '.?,':
#            if guessed_name.endswith(c): 
#                guessed_name = guessed_name[:-1]
        return guessed_name
        
    def _strip_tussenvoegels(self,s):
        s = s.strip()
        for tussenvoegsel in TUSSENVOEGSELS:
            if s.startswith(tussenvoegsel +  ' ' ):
                s = s[len(tussenvoegsel):]
                s = self._strip_tussenvoegels(s)
                break
        return s.strip()
    
     
    @cached
    def guess_geslachtsnaam(self, hints=[], change_xml=True):
        """Try to guess the geslachtsnaam, and return it
        
        arguments:
             - change_xml. 
               NOTA BENE: If True, this has a side effect that the XML is changed
             - hints: a list with one or more of the following hints: 
                 ['startswithgeslachtsnaam']
        returns:
             None if no geslachtsnaam is found
             The guessed string if such a name is found
         
        >>> name.to_string()
        '<persName>Puk, Pietje</persName>
        >>> name.guess_geslachtsnaam(change_xml=True)
        'Puk'
        >>> name.to_string()
        '<persName><name type="geslachtsnaam">Puk</name>, Pietje</persName>
             
        >>> name.fromstring('AAA BBB')
        >>> name.guess_geslachtsnaam()
        'BBB'
        >>> name.guess_geslachtsnaam(hints=['startswithgeslachtsnaam'])
        'AAA'
        """
        if self.geslachtsnaam(): #if we already have an explicitly given geslachtnaam, we dont try to guess, but return it
            return self.geslachtsnaam()
        
        elif self._root.text and self._root.text.strip(): #we only try to guess if there is text that is not marked as a part of a name
            return self._guess_geslachtsnaam(change_xml=change_xml, hints=hints)
                    
        else: #in case we did not find a last name, and return None
            return None
        
    def _guess_geslachtsnaam(self, change_xml,hints):
        """ """
        orig_naam = self._root.text
        guessed_geslachtsnaam = self._guess_geslachtsnaam_in_string(orig_naam, hints)
        if guessed_geslachtsnaam and change_xml:
            guessed_geslachtsnaam = guessed_geslachtsnaam.strip()
            el_name = SubElement(self._root, 'name')
            el_name.set('type','geslachtsnaam')
            el_name.text = guessed_geslachtsnaam
            idx = orig_naam.rfind(guessed_geslachtsnaam)
            self._root.text, el_name.tail =  orig_naam[:idx], orig_naam[idx + len(guessed_geslachtsnaam):]
            
        return guessed_geslachtsnaam
    @cached
    def guess_normal_form2(self, change_xml=True):
        """return 'normal form' of the name (prepositie voornaam intrapostie geslachstsnaam postpostie)
        
        NB: we rather simply serialize 'as is' then make a mistake, so we only change the order of the name if we are pretty sure
         
        """
        n = self._root
        last_name = self.guess_geslachtsnaam()
        result = self.serialize()
        if (list(n) and n[0].get('type') == 'geslachtsnaam' and not n.text and not (n.text and n.text.strip()))  and not R_ROMANS.search(result):
            #if the normal form thing immediate starts with the geslachtsnaam
            #serialize everything except the geslachtsnaam
            #and add the geslachtsnaam at the end
            result = serialize(n, exclude=['geslachtsnaam'])
            if result.startswith(','):
                result = result[1:].strip()
            result +=  ' '   
            result += serialize(n[0], include_tail=False)
        elif last_name and self.serialize().startswith(last_name + ','):
            result = result[len(last_name + ','):].strip() +  ' ' + last_name
        else:
            pass
            
        result = remove_parenthesized(result)
        result = fix_capitals(result)
        return result
    @cached
    def guess_normal_form(self, change_xml=True, ):
        """return 'normal form' of the name (Geslachtsnaam, prepositie voornaam intrapostie, postpostie)
        
        returns:
            a string
        
        cf. also "guess_normal_form2"
        """
        try:
            self._root
        except AttributeError:
            self.from_string(self.xml)
            
        self.guess_geslachtsnaam(change_xml=change_xml)
        
        last_name = self.geslachtsnaam()
        
        n = self._root
        if not last_name:
            s = self.serialize()
        elif (list(n) and n[0].get('type') == 'geslachtsnaam' and not n.text):
            s = self.serialize()
        else:
            rest = self.serialize(exclude=['geslachtsnaam']).strip()
            if rest:
                s = '%s, %s' % (last_name, rest)
            else:
                s = last_name
                
        s = remove_parenthesized(s)
        result = fix_capitals(s)
        return result
    @cached
    def initials(self):
        s = self.guess_normal_form2() #take ther string with first_name, last_name etc
        return u''.join(s[0] for s in wordsplit_re.findall(s)
                            if s not in STOP_WORDS_frozenset)

    def to_xml(self):
        if not hasattr(self,'_root') and hasattr(self, 'xml'):
            self.from_string(self.xml)
        return self._root

    def to_string(self):
        s = etree.tounicode(self.to_xml(), pretty_print=True)
        s = unicode(s)
        s = s.strip()
        return s
    
    @cached
    def soundex_nl(self, s=None, length=4, group=1):
        if s is None:
            s = self.guess_normal_form()
        result = soundexes_nl(s, length=length, group=group, filter_initials=True)
        return result 
    
    def _name_parts(self):
        s = self.serialize()
        return re.findall('\S+', s)
    
    @cached
    def contains_initials(self):
        """Return True if the name contains initials"""
        #all parts of the name are initials, except  "geslachtsnaam" or ROMANS or TUSSENVOEGSELS
        g = self.guess_geslachtsnaam()
        for p in self._name_parts():
            if p.endswith('.') and p not in VOORVOEGSELS_EN_TERRITORIALE_TITELS:
                return True
        return False

    def compute_attributes_to_cache(self):
        " Return a list of bound methods that were decorated with @cache"
        res = {}
        for method in self._get_methods_to_cache():
            res[method.__name__] = method()
        return res
    def _get_methods_to_cache(self):
        " Precompute values for methods decorated with @cache"
        methods_to_cache = []
        for a in dir(self):
            attribute = getattr(self, a)
            if getattr(attribute,'_cache_decorated_method', False):
                methods_to_cache.append(attribute)
        return methods_to_cache
    def set_precomputed_data(self, data):
        """ Call this method with the return value of compute_attributes_to_cache.
            After the call, all decorated methods will returned the cached values.
        """
        self._cache = data

Naam = Name #for backwards compatibility

