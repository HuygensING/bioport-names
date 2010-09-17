import re
from common import *
from plone.memoize import ram
STOP_WORDS_frozenset = frozenset(STOP_WORDS)


#GROUPS1 defines the 'loose' soundex expression - many words have the same expression
GROUPS1 = (
            ('' ,['[^a-z]', 'en$', '^h']), #alleen alfabetische characters, strip h at start 
#            ('', [r'^%s' % s for s in PREFIXES + ['h']]), 

            ('.',['ah', 'eh','ij', 'a', 'e', 'i', 'o','u','y', r'\.\.\.', r'\.\.']), 
            ('s',['z', 'ss', '(?<!^)sch']), #match 'sch' except when it is the start of the string 
            ('p',['b', 'pp']), 
            ('g',['ch', 'gg']), 
            ('k',['q','kw', 'c', 'x', 'kk']),
            ('t',['d',  'tt']), #d, dt, tt, dd --> t
            ('f',['ph', 'v', 'w', 'ff']),
#            ('h',[]),
            ('l',['ll']),
            ('n',['m', 'nn']), 
            ('r',['rh', 'rr'] ), 
         #   ('', '1234567890')
)

#GROUPS2 defines a somewhat stricter soundex expression than GROUPS1 - fewer words have the same expression
GROUPS2 = (
            ('' ,['[^a-z\?\*]']), # #remove all non-alphabetical characters, 
#            ('' ,[r'\(', r'\)']),  #remove brackets (
            ('end', ['eind$',]), #are we sure we ant to do this?
            ('boom', ['baum'],), #are we sure we want to do this? 
            ('huis', ['haus'],),
            ('berg', ('burg',)),
            ('woud', ('wold',)),
            ('ng', ['(?<=i)ngk$', '(?<=i)nk$',]), 
            ('na', ['naar$',]),
            ('', ('(?<=der)s$',)),
            ('ek', ('ecque$',)),
            ('rs', ('(?<=[aeiou])(rts|rds|rdz|rtz)(?=(e|$|k))',)),
            ('mm', ('(?<=[aeiou])(mb)(?=[e])',)),
            ('s',['z', 'ss', '(?<!^)sch', 'sch(?=[mnr])',]), #match 'sch' except when it is the start of the string 
            ('', ('(?<=..[bdfgjklmnprstvwzy])en$',)), #en at the end of a word that is not too short, preceded by a consonant
            ('', ('(?<=..[bdfgjklmnprstvwzy])e$',)), #e at the aned of a word preceded by a consonant
#            ('', ('(?<=en)s$',)),
            ('', ('(?<=...)ens$',)),
            ('', ('(?<=.....)a$',)),
            ('em', ('(?<=.)um$',)),
            ('e', ['en(?=[bdfklmnpqrstvwz][^s].)',]), #tussen -n
            ('7',['uy','uij', 'ui', ]), #'(?<=[^o])oij',  '(?<=[^o])oi', ]), 
            ('6',['ouw','aauw', 'auw', 'ou', 'au',  ]), #these become 'au' 
            ('5',['ue', 'uu','uh', ]), #these become 'u'
            ('4',['oh', 'oo', 'oe' , ]), #these come 'o' 
            ('1',['ah', 'ae','aa','a']), #these become 'a' 
            ('3',['eij',  'ey', 'ij', 'ie', 'i',  'y','eei', 'ei', 'ie']), #these become 'i'
            ('2',['ee', 'eh','e', '(?<=.)a$']), #a at the and of a word longer than 1 char) these become 'e'
#            ('ei', ['eij', 'ey', 'y']), 
            ('p',['pp']), 
            ('b',['bb']), 
            ('g',['ch', 'gg', 'gh', 'ng']), 
            ('qu', ['kw']),
            ('x', ['ks'],),
            ('k',['c', 'x', 'kk', ]),
            ('t',[ 'tt', 'd$', 'dt$', 'th','d(?=s)','(?<=n)dt','(?<=n)d',]),
            ('d',[ 'dd']),
            ('f',['ph', 'v', 'w', 'ff']),
#            ('h',[]),
            ('l',['ll']),
            ('n',['nn', ]), 
            ('m',['mm']), 
            ('r',['rh', 'rr'] ), 
            ('a', '1',),
            ('e', '2'),
            ('i', '3'),
            ('o', '4'),
            ('u', '5'),
            ('au', '6'),
            ('ui', '7'),
            
#            ('', '1234567890')
)

#_GROUPS1 = [(k, '|'.join(ls)) for k, ls in GROUPS1]
#_GROUPS2 = [(k, '|'.join(ls)) for k, ls in GROUPS2]
#GROUPS1_SINGLEREGEXP = re.compile('|'.join(["(%s)" % v for k, v in _GROUPS1]))
#GROUPS2_SINGLEREGEXP = re.compile('|'.join(["(%s)" % v for k, v in _GROUPS2]))
#GROUPS1_LOOKUP = dict((i+1, k) for (i, (k,v)) in enumerate(GROUPS1))
#GROUPS2_LOOKUP = dict((i+1, k) for (i, (k,v)) in enumerate(GROUPS2))
GROUPS1 = [(k, re.compile('|'.join(ls))) for k, ls in GROUPS1]
GROUPS2 = [(k, re.compile('|'.join(ls))) for k, ls in GROUPS2]

def dict_sub(d, text): 
  """ Replace in 'text' non-overlapping occurences of REs whose patterns are keys
  in dictionary 'd' by corresponding values (which must be constant strings: may
  have named backreferences but not numeric ones). The keys must not contain
  anonymous matching-groups.
  Returns the new string.""" 

  # Create a regular expression  from the dictionary keys
  regex = re.compile("|".join("(%s)" % k for k in d))
  # Facilitate lookup from group number to value
  lookup = dict((i+1, v) for i, v in enumerate(d.itervalues()))

  # For each match, find which group matched and expand its value
  return regex.sub(lambda mo: mo.expand(lookup[mo.lastindex]), text)

           
def multiple_replace(dict, text): 
    """ Replace in 'text' all occurences of any key in the given
    dictionary by its corresponding value.  Returns the new tring.""" 
    
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 
    
def soundexes_nl(s, length=-1, group=2, 
     filter_stop_words=True, 
     filter_initials=False, 
     filter_custom=[], #a list of words to ignore
     wildcards=False):
    """return a list of soundexes for each of the words in s
    
    filter_stop_words : filter stop words such as "van" en "of" 
    wildcards: if True, leave '?' and '*' in place
    """
    
    #splits deze op punten, spaties, kommas, etc
    #ls = re.split('[ \-\,\.]', s.lower())
    s = s.lower()
    ls = re.findall('[\w\?\*]+', s, re.UNICODE)
    
    #filter een aantal stopwoorden
    if filter_stop_words:
        ls = [s for s in ls if s not in STOP_WORDS_frozenset]
    if filter_custom:
        ls = [s for s in ls if s not in filter_custom]
    #filter initialen er uit, behalve eerste en laate, want die kunnen nog wel de achternaam zijn
    if filter_initials and  len(ls) > 1:
        ls =[s for s in ls[:] if len(s) > 1]

    result  = [soundex_nl(s, length=length, group=group, wildcards=wildcards) for s in ls] 
    result = list(set(result)) #remove duplicates
    return result

def _cache_key(funcobj, s, length=4, group=1, wildcards=False):
    return "%s%i%i%i" % (s.encode('utf8'), length, group, wildcards)
    
@ram.cache(_cache_key)
def soundex_nl(s, length=4, group=1, wildcards=False):
    """
    return a string of length representing a phonetical canonical form of s
    
    arguments:
        s : a string
        length : an integer. Length=-1 transforms the whole string
        group : an integer [1, 2]
        wildcards : if True, wildcard element (?, *) remain in place
    stab at giving names a simplified canonical form based on Dutch phonetics and spelling conventions
    
    There are two groups:
        - group 1: identify lots
        - groep 2: identify somewhat less (stay close to actual phonetics)
        
    """
    #ignore Romans
    if s in ROMANS:
        return s
    
    s = s.lower()
    s = to_ascii(s)
    if not wildcards:
        #remove 'wildcard' characters
        s = re.sub('[\?\*]', '', s)


    #strip of certain prefixes
    #XXX this shoudl be in the regular expression specs
    for x in PREFIXES:
        if s.startswith(x):
            s = s[len(x):]


    if group == 1:
        groups = GROUPS1
    elif group == 2:
        groups = GROUPS2 
 
    else:
        raise Exception('"group" argument must be either 1 or 2')
    for k, regexp in groups:
        s = regexp.sub(k, s)
        while regexp.search(s):
            s = regexp.sub(k, s)
                
#
#    if group == 1:
#         s = GROUPS1_SINGLEREGEXP.sub(lambda mo: mo.expand(GROUPS1_LOOKUP[mo.lastindex]), s)
#    elif group == 2:
#         s = GROUPS2_SINGLEREGEXP.sub(lambda mo: mo.expand(GROUPS2_LOOKUP[mo.lastindex]), s)
#    else:
#        raise Exception('"group" argument must be either 1 or 2')

    if s.endswith('.'): 
        s = s[:-1]
    if not s: 
        s = '.'
    if length > 0:
        s = s[:length]
    s = unicode(s)
    return s

 
