#! /usr/bin/env python    
# encoding=utf8

import unittest

from names.name import Name
from lxml import etree
from names.common import *


Naam = Name

class NaamTestCase(unittest.TestCase):

    def tearDown(self):
        pass
 
    def test_sanity(self):
        return

    def test_guess_geslachtsnaam(self):
#        assert 0, Naam()._guess_geslachtsnaam_in_string('Bec(q)-Crespin, Josina du')
        for n, wanted_result in [
            ('Jelle Gerbrandy', 'Gerbrandy'),
            ('Boudewijn (zie van der AA.)', 'Boudewijn'),
            ('Gerbrandy, Jelle', 'Gerbrandy'),
            ('C.H.Veenstra', 'Veenstra'),
            ('A.A.R. Bastiaensen CM', 'Bastiaensen CM'),
			('Yvette Marcus-de Groot', 'Marcus-de Groot'),
			('S. de Groot', 'Groot'),
            ('Willy Smit-Buit' , 'Smit-Buit' ), 
            ('Johann VII' , '' ), 
            ('Johann (Johan) VII' , '' ), 
            ('Bec(q)-Crespin, Josina du', 'Bec(q)-Crespin'), 
            ('Abraham de Heusch of Heus', 'Heus'),
            ('David Heilbron Cz.', 'Heilbron Cz.'),
            ('Arien A', 'A'),
            ('Johannes de Heer', 'Heer')
            ]:
            guessed = Naam(n).guess_geslachtsnaam()
            self.assertEqual(guessed, wanted_result, '%s "%s"-"%s"' % (n, guessed, wanted_result))

    def test_guess_normal_form(self):
        for n, wanted_result in [
             (Naam('Arien A'), 'A, Arien'),
             (Naam().from_args(geslachtsnaam='A', volledige_naam='Arien A'), 'A, Arien'),
             ]:
            guessed = n.guess_normal_form()
            self.assertEqual(guessed, wanted_result)
                                                
            
    def test_html_codes(self):
        n = Naam('W&eacute;l?')
        n.html2unicode()
        self.assertEqual( n.volledige_naam(), u'Wél?')
        
    def test_strip_tussenvoegsels(self):
        for s, result in [
            ('van de Graaf' , 'Graaf' ),
            ('in \'t Veld' , 'Veld' ),
            ('van der Graaf' , 'Graaf' ),
            ]:
            
            self.assertEqual(Naam(s)._strip_tussenvoegels(s), result)
    def test_to_xml(self):
        self.assertEqual(Naam('abc').to_string(), '<persName>abc</persName>')


    def test_from_xml(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Naam().from_string(s)
#        assert 0, etree.fromstring(s).xpath('//name[@type="geslachtsnaam"]')
        self.assertEqual(n.geslachtsnaam(), 'Gerbrandy')
        self.assertEqual(n.to_string(), s)

    def test_from_soup(self):
        #n = Naam().from_soup('Ada, gravin van Holland (1185-1223)')
        n = Naam().from_soup(u'Ada, gravin van Holland (±1185‑1223)')
        
        self.assertEqual(n.death, '1223', )
        self.assertEqual(n.birth, None,n.birth)
        self.assertEqual(n.territoriale_titel, 'gravin van Holland', n.to_string())
        self.assertEqual(n.get_volledige_naam(), 'Ada')
        
        n = Naam().from_soup('Xerxes, koning van Perzië 486‑465</territoriale_titel>')
        self.assertEqual(n.get_volledige_naam(), 'Xerxes')
        n.guess_geslachtsnaam()
        self.assertEqual(n.get_volledige_naam(), 'Xerxes')
        self.assertEqual(n.guess_normal_form(), 'Xerxes')
        
        n= Naam().from_soup(u'Aäron')
        self.assertEqual(n.guess_normal_form(), u'Aäron')
        n= Naam(u'Willem II')
        self.assertEqual(n.guess_normal_form(), u'Willem II')
        self.assertEqual(type(n.guess_normal_form()), type(u'Willem II'))
        
    def test_from_args(self):
        n = Naam().from_args(volledige_naam='Jelle Gerbrandy', geslachtsnaam='Gerbrandy')
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Naam().from_args(volledige_naam='Jelle Gerbrandy', geslachtsnaam='Gerbrandy')
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Naam(geslachtsnaam='Gerbrandy', voornaam='Jelle', intrapositie=None)
        s = '<persName><name type="voornaam">Jelle</name> <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)

        n = Naam().from_args(volledige_naam='Arien A', geslachtsnaam='A')
        s ='<persName>Arien <name type="geslachtsnaam">A</name></persName>'
        self.assertEqual(n.to_string(), s)
        
        n = Naam(volledige_naam='Gerbrandy, Jelle')
        s = '<persName>Gerbrandy, Jelle</persName>'
        self.assertEqual(n.to_string(), s)
        
    def test_diacritics(self):
        n = Naam(u'Wét')
        
        el = etree.Element('test')
        el.text = u'Wét'
        s = '<persName>Wét</persName>'
        self.assertEqual(n.to_string(), s)
        
    def test_serialize(self):
        s = '<a>a<b>b</b> c</a>'
        self.assertEqual(Naam().serialize(etree.fromstring(s)), 'ab c')
        
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        naam = Naam().from_string(s)
        self.assertEqual(serialize(naam._root), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(naam._root), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(), 'Jelle Gerbrandy')
        self.assertEqual(naam.serialize(exclude='geslachtsnaam'), 'Jelle')
        
        naam = Naam('Gerbrandy, Jelle')
        naam.guess_geslachtsnaam(change_xml=True)
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
        naam = Naam().from_string(s)
        
        self.assertEqual(naam.geslachtsnaam(), u'Gerbrandy')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Naam('Jelle Gerbrandy')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        naam.guess_geslachtsnaam()
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Naam('Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form(), u'Gerbrandy, Jelle')
        self.assertEqual(naam.guess_normal_form2(), u'Jelle Gerbrandy')

        naam = Naam(voornaam='Hendrik IV')
        self.assertEqual(naam.guess_normal_form(), u'Hendrik IV')
        self.assertEqual(naam.guess_normal_form2(), u'Hendrik IV')
        n = Naam().from_string("""<persName>
<name type="voornaam">Hendrik IV</name>
</persName>""")
        n.guess_geslachtsnaam()
        assert not n.geslachtsnaam(), n.to_string()
        self.assertEqual(n.guess_normal_form(), 'Hendrik IV')
        self.assertEqual(naam.guess_normal_form2(), u'Hendrik IV')
        
        s = """<persName>
  <name type="geslachtsnaam">Xerxes </name>
</persName>"""
        n = Naam().from_string(s)
        self.assertEqual(n.guess_normal_form(), 'Xerxes')
        
        s = '<persName><name type="geslachtsnaam">A</name>, Arien</persName>'
        n = Naam().from_string(s)
        self.assertEqual(n.guess_normal_form(), 'A, Arien')
        self.assertEqual(n.guess_normal_form2(), 'Arien A')
        
        n = Naam('A.B.J.Teulings')
        self.assertEqual(n.guess_normal_form(), 'Teulings, A.B.J.')
        self.assertEqual(n.guess_normal_form2(), 'A.B.J.Teulings')
        
        naam = Naam('JOHAN (Johann) VII')   
        self.assertEqual(naam.guess_normal_form(), 'Johan VII')
        self.assertEqual(naam.guess_normal_form2(), 'Johan VII')
        
        naam = Naam('Lodewijk XVIII')   
        self.assertEqual(naam.guess_normal_form2(), 'Lodewijk XVIII')
        
        
        s = """<persName> <name type="voornaam">Trijn</name> <name type="intrapositie">van</name> <name type="geslachtsnaam">Leemput</name></persName>"""
        naam = Naam().from_string(s)
        
        self.assertEqual(naam.guess_normal_form(), 'Leemput, Trijn van')
        self.assertEqual(naam.guess_normal_form2(), 'Trijn van Leemput')
        
        n5 = Naam('Piet Gerbrandy', geslachtsnaam='Gerbrandy')
        self.assertEqual(n5.guess_normal_form(), 'Gerbrandy, Piet')
        self.assertEqual(n5.guess_normal_form2(), 'Piet Gerbrandy')
        
        n6 = Naam('Piet Gerbrandy', geslachtsnaam='Piet')
        self.assertEqual(n6.guess_normal_form(), 'Piet Gerbrandy')
        self.assertEqual(n6.guess_normal_form2(), 'Gerbrandy Piet')
        
        n = Naam('Hermansz')
        self.assertEqual(n.guess_normal_form(), 'Hermansz')
        self.assertEqual(n.geslachtsnaam(), 'Hermansz')
        
        n = Naam('Ada, van Holland (1)')
        self.assertEqual(n.guess_normal_form(), 'Ada, van Holland')
        
    def test_volledige_naam(self):
        n = Naam(voornaam='Jelle')
        self.assertEqual(n.get_volledige_naam(),'Jelle')
        n.guess_geslachtsnaam()
        self.assertEqual(n.get_volledige_naam(),'Jelle')
        n = Naam().from_string("""<persName>
<name type="voornaam">Hendrik IV</name>
</persName>""")
        self.assertEqual(n.get_volledige_naam(), 'Hendrik IV')
        
        naam = Naam(voornaam='Hendrik IV')
        self.assertEqual(naam.get_volledige_naam(), u'Hendrik IV')
   
    def test_html2unicode(self): 
        s = u'M&ouml;törhead'
        n = Naam(s)
        self.assertEqual(n.volledige_naam(), s)
        n.html2unicode()
        self.assertEqual(n.volledige_naam(), u'Mötörhead')
        
        #this shoudl not be here, but under a separate test for the utility functions in common
        self.assertEqual(html2unicode('&eacute;'), u'é')
        self.assertEqual(html2unicode('S&atilde;o'), u'São')
    def test_sort_key(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Naam().from_string(s)
        self.assertEqual(n.sort_key()[:15], 'gerbrandy jelle')

        s ='<persName>Jelle <name type="geslachtsnaam">Éerbrandy</name></persName>'
        n = Naam().from_string(s)
        self.assertEqual(n.sort_key()[:15], 'eerbrandy jelle')

        n = Naam(u'São Paolo')
        self.assertEqual(n.geslachtsnaam(), '')
        self.assertEqual(n.sort_key().split()[0], 'sao')
        
        n = Naam(u'S&atilde;o Jo&atilde;o')
        n.html2unicode()
        self.assertEqual(n.sort_key().split()[0], 'sao')
       
        n = Naam('(Hans) Christian')
        self.assertEqual(n.sort_key().split()[0], 'christian')
        
        n =Naam(u'Løwencron')
        self.assertEqual(n.sort_key().split()[0], 'loewencron')
        
        n = Naam(u'?, Pietje')
        self.assertTrue(n.sort_key() > 'a', n.sort_key())    
        
        n = Naam("L'Hermite")    
        self.assertTrue(n.sort_key().startswith('herm'))
        
        s ='<persName>Samuel <name type="geslachtsnaam">Beckett</name></persName>'
        n1 = Naam().from_string(s)
        s ='<persName>Beckett, Samuel</persName>'
        n2 = Naam().from_string(s)
        self.assertEqual(n1.sort_key(), n2.sort_key())
    def test_spaces_in_xml(self):
        n = Naam(voornaam='Jelle', geslachtsnaam='Gerbrandy')
        s = '<persName><name type="voornaam">Jelle</name> <name type="geslachtsnaam">Gerbrandy</name></persName>'
        self.assertEqual(n.to_string(), s)

#      
    def test_initials(self):
        self.assertEqual(Naam('P. Gerbrandy').initials(), 'G P')
        self.assertEqual(Naam('Engelmann, Th.W.').initials(), 'E T W')
        self.assertEqual(Naam('Borret, Prof. Dr. Theodoor Joseph Hubert').initials(), 'B T J H')

    def test_soundex_nl(self):
        s ='<persName>Jelle <name type="geslachtsnaam">Gerbrandy</name></persName>'
        n = Naam().from_string(s)
        self.assertEqual(n.soundex_nl(length=5), ['g.rpr', 'j.l'])
        s ='<persName>Jelle <name type="geslachtsnaam">Scholten</name></persName>'
        
        #now that we have computed the soundex_nl, its value should be cached
        length=5
        group=1
        nf = n.guess_normal_form()
        n = Naam().from_string(s)
        self.assertEqual(n.soundex_nl(length=5), ['sg.lt', 'j.l'])
        
        
        self.assertEqual(Naam('janssen, hendrik').soundex_nl(group=1), ['j.ns', '.ntr'])
        self.assertEqual(Naam('aearssen-walte, lucia van').soundex_nl(group=1), ['.rs', 'f.lt', 'l.k'])
        self.assertEqual(Naam('aearssen,walte, lucia van').soundex_nl(group=1), ['.rs', 'f.lt', 'l.k'])
        self.assertEqual(Naam('XXX').soundex_nl(), ['k'])
    

    def test_init(self):
        naam = Naam(
            prepositie=None,
            voornaam=None,
            intrapositie=None,
            geslachtsnaam=None,
            postpositie=None,
            volledige_naam=None,
            )
        naam = Naam(
            prepositie=None,
            voornaam=None,
            intrapositie='van het',
            geslachtsnaam='Reve',
            postpositie=None,
            volledige_naam='Gerard van het Reve',
            )
        
        self.assertEqual(naam.volledige_naam(), 'Gerard van het Reve')
        self.assertEqual(naam.geslachtsnaam(), 'Reve')
        naam = Naam(
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
        self.assertEqual(Naam('abc. DE. F;dk. Genoeg-Van')._name_parts(), [u'abc.', u'DE.', 'F;dk.', 'Genoeg-Van'])
        
    def test_contains_initials(self):
        self.assertEqual(Naam('J.K. Rowling').guess_geslachtsnaam(), 'Rowling')
        self.assertEqual(Naam('J.K. Rowling').contains_initials(), True)
        self.assertEqual(Naam('Th.D. de Rowling').contains_initials(), True)
        self.assertEqual(Naam('Rowling, Jan').contains_initials(), False)
        self.assertEqual(Naam('Rowling, J.').contains_initials(), True)
def test_suite():
    
    return TestSuite((
        makeSuite(NaamTestCase),
        ))


if __name__=='__main__':
    test_suite = unittest.TestSuite()
    tests = [NaamTestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    unittest.TextTestRunner(verbosity=2).run(test_suite)


