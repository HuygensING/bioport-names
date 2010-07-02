#! /usr/bin/python    
#encoding=utf-8
import unittest
from unittest import TestCase, TestSuite, main, makeSuite
from names.name import Name 
from lxml import etree
from names.common import *
from names.soundex import soundex_nl, soundexes_nl


class SoundexNLTestCase(TestCase):

    def test_soundex_nl1(self):
        def soundex_nl1(s, length=4):
            return soundex_nl(s, length, group=1)
        self.assertEqual(soundex_nl1('Scholten', length=5), 'sg.lt')
        n1 = Name('Uyl')
        n2 = Name('Uijl')
        n3 = Name('Uil')
        n4 = Name('Yl')
        self.assertEqual(n1.soundex_nl(length=5), ['.l'])
        self.assertEqual(n2.soundex_nl(length=5), ['.l'])
        self.assertEqual(n3.soundex_nl(length=5), ['.l'])
        self.assertEqual(n4.soundex_nl(length=5), ['.l'])
        
        self.assertEqual(Name('AAA').soundex_nl(), ['.'])
        self.assertEqual(Name('Quade').soundex_nl(), ['k.t'])
        self.assertEqual(Name('Quack').soundex_nl(), ['k.k'])
        self.assertEqual(Name('kwak').soundex_nl(), ['k.k'])
        self.assertEqual(Name('kwik en kwak').soundex_nl(), ['k.k', ])
        self.assertEqual(Name('rhood').soundex_nl(), ['r.t'])
        self.assertEqual(Name('zutphen').soundex_nl(), ['s.tf'])
        self.assertEqual(Name('Willem').soundex_nl(), ['f.l.'])
        self.assertEqual(soundex_nl1('xx1'), 'k')
        self.assertEqual(soundex_nl1('yyy22'), '.')
        #diacritics?
        self.assertEqual(soundex_nl1(u'wél'), 'f.l') 

    def test_soundex_nl2(self):
        def soundex_nl2(s, length=-1):
            return soundex_nl(s, length, group=2)
        # group 2 is de "fonetische soundex"       
        #c
        for s, wanted in [
            #examples of soundex expressoins
            ('Huis', 'huis'),
            ('Huys', 'huis'),
            ('XXX', 'k'),
            ('goed', 'got'),
            ('eijck', 'ik'),
            #ei, eij, ij, ey, y, i
             
            
            #
            ('ijck', 'ik'),
            ('ildt', 'ilt'), 
            ('ild', 'ilt'), 
            ('til', 'til'),
            ('buyt', 'buit'),
            ('s?t', 'st'),
            ('meijer', 'mier'),
            (u'Stámkart', 'stamkart' ),
            (u'Stáamkart', 'stamkart' ),
            ('broeksz', 'brok'), #??
            (u'æbele', 'abele'),
            ('a', 'a'),
            ('i', 'i'),
            ('I', 'i'),
            ('Heer', 'her'),
            ]:
            self.assertEqual(wanted, soundex_nl2(s), '%s - %s - %s'  % (s, wanted, soundex_nl2(s)))
            
            
        #THESE GET THE SAME SOUNDEXES
        for n1, n2 in [
            #these names shoudl generate the same soundex expression
            ('Kluyt', 'kluit'),
            ('Kluyt,', 'kluit'),
            ('Gerbrandij', 'Gerbrandy'),
            ('Eijck', 'ik'),
            ('Eijck', 'ik'),
            ('fortuin', 'fortuijn'), 
            ('fortuyn', 'fortuijn'), 
            ('kwak','quack'),
            ('quintus', 'kwintus'),
            ('riks', 'rix'),
            ('theodorus', 'teodorus'),
            ('meijer', 'meyer'),
            ('meier', 'meyer'),
            ('mijer', 'meier'),
            ('wildt', 'wild'), 
            ('wilt', 'wild'), 
            ('wilt', 'wild'), 
            (u'françois', 'fransoys'),
            (u'éé', 'e'),
            (u'ouw', u'auw'),
            (u'ou', u'au'),
            (u'haer', u'haar'),
            (u'u', u'uu'),
            #not even sure what behavior we want here for roman numerals
#            (u'VI', u'fi'),
            ]:
            s1 = soundex_nl2(n1)
            s2 = soundex_nl2(n2)
            self.assertEqual(s1, s2, '%s=>%s ::: %s=>%s' %( n1, s1, n2, s2))
   
        #THESE GET DIFFERENT SOUNDEXES
        for n1, n2 in [
            #these names shoudl generate the same soundex expression
            ('x', 'y'),
#            ('leeuwen', 'leuven'),
            ]:
            s1 = soundex_nl2(n1)
            s2 = soundex_nl2(n2)
            self.assertNotEqual(s1, s2, '%s=>%s ::: %s=>%s' %( n1, s1, n2, s2))
            
    def test_soundexes_nl(self):
        self.assertEqual(soundexes_nl('Samuel Beckett', length=-1), ['beket', 'samul'])
        self.assertEqual(soundexes_nl('don?er') , ['doner'])
        self.assertEqual(soundexes_nl('don?er', wildcards=True) , ['don?er'])
        self.assertEqual(soundexes_nl('don*er', wildcards=True) , ['don*er'])
        self.assertEqual(soundexes_nl('willem I' ) , ['i', 'filem' ])
        self.assertEqual(soundexes_nl('heer' ) , [])
        
        
if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    tests = [SoundexNLTestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    unittest.TextTestRunner(verbosity=2).run(test_suite)

    

