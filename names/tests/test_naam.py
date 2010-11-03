#! /usr/bin/env python    
# encoding=utf8

import unittest

from names.name import Name
from lxml import etree
from names.common import *

class NameTestCase(unittest.TestCase):

    def tearDown(self):
        pass
 
    def test_guess_geslachtsnaam(self):
        for n, wanted_result in [
            ('Jelle Gerbrandy', 'Gerbrandy'),
            ('Boudewijn (zie van der AA.)', 'Boudewijn'),
            ('Gerbrandy, Jelle', 'Gerbrandy'),
            ('C.H.Veenstra', 'Veenstra'),
            ('A.A.R. Bastiaensen CM', 'Bastiaensen CM'),
            ('Yvette Marcus-de Groot', 'Marcus-de Groot'),
            ('S. de Groot', 'Groot'),
            ('Willy Smit-Buit' , 'Smit-Buit' ), 
            ('Hendrik', 'Hendrik'),
            ('Bec(q)-Crespin, Josina du', 'Bec(q)-Crespin'), 
            ('Abraham de Heusch of Heus', 'Heus'),
            ('David Heilbron Cz.', 'Heilbron Cz.'),
            ('Arien A', 'A'),
            ('Johannes de Heer', 'Heer'),
            ('Johann VII' , 'Johann' ), 
            ('Johann (Johan) VII' , 'Johann' ), 
            ('koning Willem III' , 'Willem' ), 
            ('Bonnet-Broederhart. A.G.' , 'Bonnet-Broederhart.' ), 
            ('III' , 'III' ), 
            ('Th.W. Engelmann', 'Engelmann'),
            ('A Algra', 'Algra'),
#            ('Auger O' , 'Auger' ), 
            ]:
            guessed = Name(n).guess_geslachtsnaam()
            self.assertEqual(guessed, wanted_result, '%s "%s"-"%s"' % (n, guessed, wanted_result))

    def test_guess_normal_form(self):
        for n, wanted_result in [
             (Name('Arien A'), 'A, Arien'),
             (Name().from_args(geslachtsnaam='A', volledige_naam='Arien A'), 'A, Arien'),
             (Name('Brugse Meester van 1493'), 'Brugse Meester van 1493'),
             (Name('Th.W. Engelmann'), 'Engelmann, Th.W.'),
             (Name('A. Algra'), 'Algra, A.'),
#             (Name().from_string('<persName>A. Algra</persName>'), 'Algra A.')
             (Name('(G. Morton)'), 'G. Morton'),
            ]:
            guessed = n.guess_normal_form()
            self.assertEqual(guessed, wanted_result)
        n1 = etree.fromstring('<persName>Kees van Dongen</persName>')
        n1 = Name().from_xml(n1)
        self.assertEqual(n1.guess_geslachtsnaam(), 'Dongen')
        self.assertEqual(n1.guess_normal_form(), 'Dongen, Kees van')

        n1 = etree.fromstring('<persName>Dongen, Kees van</persName>')
        n1 = Name().from_xml(n1)
        self.assertEqual(n1.guess_normal_form(), 'Dongen, Kees van')
        
    def test_html_codes(self):
        n = Name('W&eacute;l?')
        n.html2unicode()
        self.assertEqual( n.volledige_naam(), u'Wél?')
        
    def test_strip_tussenvoegsels(self):
        for s, result in [
            ('van de Graaf' , 'Graaf' ),
            ('in \'t Veld' , 'Veld' ),
            ('van der Graaf' , 'Graaf' ),
            ]:
            
            self.assertEqual(Name(s)._strip_tussenvoegels(s), result)
    def test_to_xml(self):
        self.assertEqual(Name('abc').to_string(),
            u'<persName><name type="geslachtsnaam">abc</name></persName>')


    def test_from_xml(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Name().from_string(s)
#        assert 0, etree.fromstring(s).xpath('//name[@type="geslachtsnaam"]')
        self.assertEqual(n.geslachtsnaam(), 'Gerbrandy')
        self.assertEqual(n.to_string(), s)

#    def test_from_soup(self):
#        #n = Name().from_soup('Ada, gravin van Holland (1185-1223)')
#        n = Name().from_soup(u'Ada, gravin van Holland (±1185‑1223)')
#        
#        self.assertEqual(n.death, '1223', )
#        self.assertEqual(n.birth, None,n.birth)
#        self.assertEqual(n.territoriale_titel, 'gravin van Holland', n.to_string())
#        self.assertEqual(n.get_volledige_naam(), 'Ada')
#        
#        n = Name().from_soup('Xerxes, koning van Perzië 486‑465</territoriale_titel>')
#        self.assertEqual(n.get_volledige_naam(), 'Xerxes')
#        n.guess_geslachtsnaam()
#        self.assertEqual(n.get_volledige_naam(), 'Xerxes')
#        self.assertEqual(n.guess_normal_form(), 'Xerxes')
#        
#        n= Name().from_soup(u'Aäron')
#        self.assertEqual(n.guess_normal_form(), u'Aäron')
#        n= Name(u'Willem II')
#        self.assertEqual(n.guess_normal_form(), u'Willem II')
#        self.assertEqual(type(n.guess_normal_form()), type(u'Willem II'))
        
    def test_from_args(self):
        n = Name().from_args(volledige_naam='Jelle Gerbrandy', geslachtsnaam='Gerbrandy')
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Name().from_args(volledige_naam='Jelle Gerbrandy', geslachtsnaam='Gerbrandy')
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Name(geslachtsnaam='Gerbrandy', voornaam='Jelle', intrapositie=None)
        s = '<persName><name type="voornaam">Jelle</name> <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)

        n = Name().from_args(volledige_naam='Arien A', geslachtsnaam='A')
        s ='<persName>Arien <name type="geslachtsnaam">A</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Name(volledige_naam='Gerbrandy, Jelle')
        s = '<persName><name type="geslachtsnaam">Gerbrandy</name>, Jelle</persName>'
        self.assertEqual(n.to_string(), s)
        
         
    def test_diacritics(self):
        n = Name(u'Wét')
        el = etree.Element('test')
        el.text = u'Wét'
        s = u'<persName><name type="geslachtsnaam">W\xe9t</name></persName>'
        self.assertEqual(n.to_string(), s)

    def test_serialize(self):
        s = '<a>a<b>b</b> c</a>'
        self.assertEqual(Name().serialize(etree.fromstring(s)), 'ab c')

        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        naam = Name().from_string(s)
        self.assertEqual(serialize(naam._root), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(naam._root), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(exclude='geslachtsnaam'), 'Jelle')

        naam = Name('Gerbrandy, Jelle')
        naam.guess_geslachtsnaam()
        naam.store_guessed_geslachtsnaam()
        self.assertEqual(naam.to_string(), '<persName><name type="geslachtsnaam">Gerbrandy</name>, Jelle</persName>')

        self.assertEqual(naam.serialize(exclude=['geslachtsnaam']), ', Jelle')

    def test_idempotence(self):
        
        #calling the guessing functions more than one time should not make any difference
        name = Name('Jelle Gerbrandy')
        name.guess_normal_form()
        xml1 = name.to_string()
        name.guess_normal_form()
        xml2 = name.to_string()
        name.guess_geslachtsnaam()
        xml3 = name.to_string()
        self.assertEqual(xml1, xml2)
        self.assertEqual(xml1, xml3)
        
    def test_normal_form(self):

        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        naam = Name().from_string(s)
        
        self.assertEqual(naam.geslachtsnaam(), u'Gerbrandy')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Name('Jelle Gerbrandy')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        naam.guess_geslachtsnaam()
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Name('Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Name(voornaam='Hendrik IV')
        self.assertEqual(naam.geslachtsnaam(), '')
        self.assertEqual(naam.guess_normal_form(), u'Hendrik IV')
        self.assertEqual(naam.guess_normal_form2(), u'Hendrik IV')
        n = Name().from_string("""<persName>
<name type="voornaam">Hendrik IV</name>
</persName>""")
        n.guess_geslachtsnaam()
        assert not n.geslachtsnaam(), n.to_string()
        self.assertEqual(n.guess_normal_form(), 'Hendrik IV')
        self.assertEqual(naam.guess_normal_form2(), u'Hendrik IV')
        
        s = """<persName>
  <name type="geslachtsnaam">Xerxes </name>
</persName>"""
        n = Name().from_string(s)
        self.assertEqual(n.guess_normal_form(), 'Xerxes')
        
        s = '<persName><name type="geslachtsnaam">A</name>, Arien</persName>'
        n = Name().from_string(s)
        self.assertEqual(n.guess_normal_form(), 'A, Arien')
        self.assertEqual(n.guess_normal_form2(), 'Arien A')
        
        n = Name('A.B.J.Teulings')
        self.assertEqual(n.guess_normal_form(), 'Teulings, A.B.J.')
        self.assertEqual(n.guess_normal_form2(), 'A.B.J.Teulings')
        
        naam = Name('JOHAN (Johann) VII')   
        self.assertEqual(naam.guess_normal_form(), 'Johan VII')
        
        naam = Name().from_string('<persName><name type="geslachtsnaam">Dirk</name>, VI, Theodericus</persName>')  
        self.assertEqual(naam.guess_normal_form(), 'Dirk, VI, Theodericus')
        
        naam = Name('Lodewijk XVIII')   
        self.assertEqual(naam.guess_normal_form2(), 'Lodewijk XVIII')
        
        s = """<persName> <name type="voornaam">Trijn</name> <name type="intrapositie">van</name> <name type="geslachtsnaam">Leemput</name></persName>"""
        naam = Name().from_string(s)
        
        self.assertEqual(naam.guess_normal_form(), 'Leemput, Trijn van')
        self.assertEqual(naam.guess_normal_form2(), 'Trijn van Leemput')
        
        n5 = Name('Piet Gerbrandy', geslachtsnaam='Gerbrandy')
        self.assertEqual(n5.guess_normal_form(), 'Gerbrandy, Piet')
        self.assertEqual(n5.guess_normal_form2(), 'Piet Gerbrandy')
        
        n6 = Name('Piet Gerbrandy', geslachtsnaam='Piet')
        self.assertEqual(n6.guess_normal_form(), 'Piet Gerbrandy')
        self.assertEqual(n6.guess_normal_form2(), 'Gerbrandy Piet')
        
        n = Name('Hermansz')
        self.assertEqual(n.guess_normal_form(), 'Hermansz')
        self.assertEqual(n.geslachtsnaam(), 'Hermansz')
        
        n = Name('Ada, van Holland (1)')
        self.assertEqual(n.guess_normal_form(), 'Ada, van Holland')
       
        n = Name('Hees - B.P. van') 
        self.assertEqual(n.guess_normal_form(), 'Hees - B.P. van')
        
        n = Name('Hees - B.P. van (1234-1235)') 
        self.assertEqual(n.guess_normal_form(), 'Hees - B.P. van')
        
    def test_volledige_naam(self):
        n = Name(voornaam='Jelle')
        self.assertEqual(n.get_volledige_naam(),'Jelle')
        n.guess_geslachtsnaam()
        self.assertEqual(n.get_volledige_naam(),'Jelle')
        n = Name().from_string("""<persName>
<name type="voornaam">Hendrik IV</name>
</persName>""")
        self.assertEqual(n.get_volledige_naam(), 'Hendrik IV')
        
        naam = Name(voornaam='Hendrik IV')
        self.assertEqual(naam.get_volledige_naam(), u'Hendrik IV')
   
    def test_fix_capitals(self):
        self.assertEqual(fix_capitals('Jean-Jules'), 'Jean-Jules')
        self.assertEqual(fix_capitals('Johan VIII'), 'Johan VIII')
        self.assertEqual(fix_capitals('Johan III'), 'Johan III')
        self.assertEqual(fix_capitals('Fabricius/Fabritius'), 'Fabricius/Fabritius')
        self.assertEqual(fix_capitals("L'OYSELEUR") , "l'Oyseleur")
        
    def test_html2unicode(self): 
        s = u'M&ouml;törhead'
        n = Name(s)
        self.assertEqual(n.volledige_naam(), s)
        n.html2unicode()
        self.assertEqual(n.volledige_naam(), u'Mötörhead')
        
        #this shoudl not be here, but under a separate test for the utility functions in common
        self.assertEqual(html2unicode('&eacute;'), u'é')
        self.assertEqual(html2unicode('S&atilde;o'), u'São')
    def test_sort_key(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Name().from_string(s)
        self.assertEqual(n.sort_key()[:15], 'gerbrandy jelle')

        s ='<persName>Jelle <name type="geslachtsnaam">Éerbrandy</name></persName>'
        n = Name().from_string(s)
        self.assertEqual(n.sort_key()[:15], 'eerbrandy jelle')

        n = Name(u'São Paolo')
        self.assertEqual(n.geslachtsnaam(), 'Paolo') # Automatically guessed
        self.assertEqual(n.sort_key().split()[0], 'paolo')
        
        n = Name('(Hans) Christian')
        self.assertEqual(n.sort_key().split()[0], 'christian')
        
        n =Name(u'Løwencron')
        self.assertEqual(n.sort_key().split()[0], 'loewencron')
        
        n = Name(u'?, Pietje')
        self.assertTrue(n.sort_key() > 'a', n.sort_key())    
        
        n = Name("L'Hermite")    
        self.assertTrue(n.sort_key().startswith('herm'))
        
        n = Name("La Hermite")    
        self.assertTrue(n.sort_key().startswith('herm')), n.sort_key()
        
        n = Name(u'Löwel')
        self.assertTrue(n.sort_key().startswith('lo')), n.sort_key()
        
        s ='<persName>Samuel <name type="geslachtsnaam">Beckett</name></persName>'
        n1 = Name().from_string(s)
        s ='<persName>Beckett, Samuel</persName>'
        n2 = Name().from_string(s)
        self.assertEqual(n1.sort_key(), n2.sort_key())
        
    def test_spaces_in_xml(self):
        n = Name(voornaam='Jelle', geslachtsnaam='Gerbrandy')
        s = '<persName><name type="voornaam">Jelle</name> <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)

#      
    def test_initials(self):
        self.assertEqual(Name('P. Gerbrandy').initials(), 'PG')
        self.assertEqual(Name('Engelmann, Th.W.').initials(), 'TWE')
        self.assertEqual(Name('Borret, Prof. Dr. Theodoor Joseph Hubert').initials(), 'TJHB')

    def test_soundex_nl(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Name().from_string(s)
        self.assertEqual(set(n.soundex_nl(length=5)), set(['g.rpr', 'j.l']))
        s ='<persName>Jelle <name type="geslachtsnaam">Scholten</name></persName>'
        
        #now that we have computed the soundex_nl, its value should be cached
        length=5
        group=1
        nf = n.guess_normal_form()
        n = Name().from_string(s)
        
        self.assertEqual(n.soundex_nl(length=5), ['sg.lt', 'j.l'])
        self.assertEqual(set(Name('janssen, hendrik').soundex_nl(group=1)), set(['j.ns', '.tr.']))
        self.assertEqual(Name('aearssen-walte, lucia van').soundex_nl(group=1), ['.rs', 'f.lt', 'l.k'])
        self.assertEqual(Name('aearssen,walte, lucia van').soundex_nl(group=1), ['.rs', 'f.lt', 'l.k'])
        self.assertEqual(Name('Jhr. Mr. K').soundex_nl(), ['k'])
    

    def test_init(self):
        naam = Name(
            prepositie=None,
            voornaam=None,
            intrapositie=None,
            geslachtsnaam=None,
            postpositie=None,
            volledige_naam=None,
            )
        naam = Name(
            prepositie=None,
            voornaam=None,
            intrapositie='van het',
            geslachtsnaam='Reve',
            postpositie=None,
            volledige_naam='Gerard van het Reve',
            )
        
        self.assertEqual(naam.volledige_naam(), 'Gerard van het Reve')
        self.assertEqual(naam.geslachtsnaam(), 'Reve')
        naam = Name(
            prepositie='dhr.',
            voornaam='Gerard',
            intrapositie='van het',
            geslachtsnaam='Reve',
            postpositie='schrijver',
            volledige_naam='dhr. Gerard van het Reve, schrijver',
            )
        
        self.assertEqual(naam.prepositie(), 'dhr.')
        self.assertEqual(naam.voornaam(), 'Gerard')
        self.assertEqual(naam.intrapositie(), 'van het')
        self.assertEqual(naam.geslachtsnaam(), 'Reve')
        self.assertEqual(naam.postpositie(), 'schrijver')
        self.assertEqual(naam.geslachtsnaam(), 'Reve')
    
    def test_name_parts(self):
        name_parts = Name('abc. DE. F;dk. Genoeg-Van')._name_parts()
        self.assertEqual(name_parts, [u'abc.', u'DE.', 'F;dk.', 'Genoeg-Van'])

    def test_geslachtsnaam_guess(self):
        problematic_names = ['abc. DE. F;dk. Genoeg-Van']
        for namestr in problematic_names:
            name = Name(namestr)
            should_be = re.sub('<[^>]+>', '', name.to_string())
            self.assertEqual(namestr, should_be)


    def test_contains_initials(self):
        self.assertEqual(Name('J.K. Rowling').guess_geslachtsnaam(), 'Rowling')
        self.assertEqual(Name('J.K. Rowling').contains_initials(), True)
        self.assertEqual(Name('Th.D. de Rowling').contains_initials(), True)
        self.assertEqual(Name('Rowling, Jan').contains_initials(), False)
        self.assertEqual(Name('Rowling, J.').contains_initials(), True)
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(NameTestCase),
        ))

if __name__=='__main__':
    unittest.main()


