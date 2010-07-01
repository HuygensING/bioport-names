#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import re
import difflib
from difflib import SequenceMatcher
import Levenshtein
from names.soundex import soundexes_nl, soundex_nl
from common import PREFIXES, coerce_to_unicode, to_ascii,remove_stopwords, STOP_WORDS

def split(s):
    return re.split('[ |\-]*', s)

def average_distance(l1, l2, distance_function=None):
        """the average distance of the words in l1 and l2
        use the distance function to compute distances between words in l1 and l2
        return the average distance of the highest scores for each of the words from both lists
       
        @arguments:
            l1 is a list of strings
            l2 is a list of strings
            
        i.e.: 
        average_disatnce(['n1a', 'n1b'], ['n2'])
        is the average of :
            max(d(n1a, n2))
            max(d(n1b, n2))
            max(d(n2, n1a), d(n2,n1b))
        
        average_disatnce(['n1a', 'n1b'], ['n2a', 'n2b'])
        is the average of:
            max(d(n1a, n2a), d(n1a, n2b))
            max(d(n1b, n2a), d(n1b, n2b))
            max(d(n1a, n2a), d(n1b, n2a))
            max(d(n1a, n2b), d(n1b, n2a))
        
        """ 
        if not distance_function:
            distance_function = levenshtein_ratio
        counter = 0.0
        numerator = 0.0
        
        #compute array of values
#        if not l1 or not l2:
#            return 1.0
        #make l1 the shortes
        l1, l2 = len(l1)<len(l2) and (l1, l2) or (l2, l1)
        
        #compute the distrances
        distances = []
        for s1 in l1:
            distances += [(distance_function(s1, s2), s1, s2) for s2 in l2]
#            ls.sort(reverse=True)
#            distances.append((ls, s1))
        distances.sort(reverse=True)
        #compute maxima for each colum and each row
        done = []
        for d, s1, s2 in distances:
            if s1 not in done and s2 not in done:
                done.append(s1)
                done.append(s2) 
                counter += d
                numerator += 1
                
        #if there is a difference in length, we penalize for each item 
        for i in range(len(l2) - len(l1)):
            counter += .9
            numerator += 1
        try:
            return counter/numerator                
        except ZeroDivisionError:
            return 1.0
def levenshtein_ratio(a,b):
    "Calculates the Levenshtein distance between a and b."
    return Levenshtein.ratio(a,b)
class Similarity(object):
    def __init__(self):
        pass



    def levenshtein_ratio2(self, a, b):
        d = Levenshtein.distance(a, b)
        return 1.0 - (float(d)/10.0)
#    def to_ascii(self, s):
#        d = to_ascii
#        s = unicode(s)
#        for k in d.keys():
#            s = s.replace(k, d[k])
#        return s

    def average_distance(self, l1, l2, distance_function=None): 
        
        return average_distance(l1, l2, distance_function)

    def ratio(self,n1,n2, explain=0, optimize=False):
        """Combine several parameters do find a similarity ratio
        
        if optimize is True, skip some parts of the algorithm for speed (and sacrifice precision)"""
        weight_normal_form =  5.0 #distance between soundexes of normal form
        weight_normal_form_if_one_name_is_in_initials = weight_normal_form / 4 #distance between soundexes of normal form
        weight_normal_form_soundex =  9.0 #average distance between soundexes of normal form
        weight_normal_form_soundex_if_one_name_is_in_initials =weight_normal_form_soundex /4 #distance between soundexes of normal form
        weight_geslachtsnaam1 = 7.0 #distance between soundexes of geslachtsnamen
        weight_geslachtsnaam2 = 7.0 #distance between geslachtsnaam
        weight_initials =  2 #distance between initials
        weight_initials_if_one_name_is_in_initials =  weight_initials * 2 #distance between initials if one of the names is in intials
            #(for example, "A.B Classen")
        
        
        #normal form of the name 
        nf1 = n1.guess_normal_form()
        nf2 = n2.guess_normal_form()
        #remove diacritics
        nf1 = to_ascii(nf1)
        nf2 = to_ascii(nf2)
        
#        ratio_normal_form = self.levenshtein_ratio(nf1, nf2)
        ratio_normal_form = self.average_distance(split(nf1), split(nf2))        
        #create a simkplified soundex set for this name
        #remove stopwords
        nf1 = remove_stopwords( nf1)
        nf2 = remove_stopwords( nf2)
        
        #we use the soundex_nl property of the name, so the property gets cached
        se1 = n1.soundex_nl(nf1, group=2, length=-1)
        se2 = n2.soundex_nl(nf2, group=2, length=-1)
        ratio_normal_form_soundex = self.average_distance( se1, se2)
        
        #gelachtsnaam wordt op twee manieren met elkaar vergeleken
        g1 = n1.geslachtsnaam() #or n1.get_volledige_naam()
        g2 = n2.geslachtsnaam() #or n2.get_volledige_naam()
        g1 = to_ascii(g1)
        g2 = to_ascii(g2)
        if not optimize:
            #de soundexes van de achternaam worden meegewoen
            g1_soundex = n1.soundex_nl(g1, group=2, length=-1)
            g2_soundex = n2.soundex_nl(g2, group=2, length=-1)
            ratio_geslachtsnaam1 = self.average_distance(g1_soundex, g2_soundex)
        else:
            ratio_geslachtsnaam1 = 1 
            weight_geslachtsnaam1 = 0
        #n de afstand van de woorden in de achtenraam zelf
        ratio_geslachtsnaam2 = self.average_distance(
             re.split('[ \.\,\-]', g1.lower()),
             re.split('[ \.\,\-]', g2.lower()),
             levenshtein_ratio)

        #count initials only if we have more than one
        #(or perhaps make this: if we know the first name)
        if len(n1.initials()) == 1 or len(n2.initials()) == 1:
            #initials count much less if there is only one
            weight_initials = 0
            ratio_initials = .5
        elif n1.contains_initials() or n2.contains_initials():
            try:
                ratio_initials = levenshtein_ratio(n1.initials().lower(), n2.initials().lower())
            except:
                import pdb;pdb.set_trace() 
                raise
            weight_initials = weight_initials_if_one_name_is_in_initials
        elif len(n1.initials()) > 1 and len(n2.initials()) > 1:
            ratio_initials = levenshtein_ratio(n1.initials().lower(), n2.initials().lower())
        else:
            ratio_initials = 0.7
            
        if n1.contains_initials() or n2.contains_initials():
            weight_normal_form = weight_normal_form_if_one_name_is_in_initials 
            weight_normal_form_soundex = weight_normal_form_soundex_if_one_name_is_in_initials
            
        try:
            counter = ratio_normal_form * weight_normal_form +  ratio_normal_form_soundex * weight_normal_form_soundex+ ratio_geslachtsnaam1*weight_geslachtsnaam1 + ratio_geslachtsnaam2*weight_geslachtsnaam2 +  ratio_initials*weight_initials
            numerator =  weight_normal_form  +  weight_normal_form_soundex + weight_initials + weight_geslachtsnaam1 + weight_geslachtsnaam2
            final_ratio = counter/numerator

        except ZeroDivisionError:
            return 0.0
        
        if explain:
#            d = [
#                ('ratio_normal_form',ratio_normal_form,),
#                ('weight_normal_form',weight_normal_form, ),
#                ('ratio_geslachtsnaam1 (soundex)', ratio_geslachtsnaam1, ),
#                ('weight_geslachtsnaam1', weight_geslachtsnaam1, ),
#                ('ratio_geslachtsnaam2 (letterlijke geslachtsnaam)', ratio_geslachtsnaam2, ),
#                ('weight_geslachtsnaam2', weight_geslachtsnaam2, ),
#                ('ratio_initials', ratio_initials, ),
#                ('weight_initials', weight_initials, ),
#                ('final_ratio', final_ratio,),
#                ('counter',counter,),
#                ('numerator', numerator,),
#            ]
            s = '-' * 100 + '\n'
            s += 'Naam1: %s [%s] [%s] %s\n' % (n1, n1.initials(), n1.guess_normal_form(), se1)
            s += 'Naam2: %s [%s] [%s] %s\n' % (n2, n2.initials(), n2.guess_normal_form(), se2)
            s += 'Similarity ratio: %s\n' % final_ratio
            s += '--- REASONS'  + '-' * 30 + '\n'
            format_s = '%-30s | %-10s | %-10s | %-10s | %-10s | %s-10s\n'
            s += format_s % ('\t  property', '  ratio', '  weight','relative_weight',  '  r*w', 'r * relative_w')
            s += '\t' + '-' * 100 + '\n'
            format_s = '\t%-30s | %-10f | %-10f | %-10f | %-10f | %-10f\n'
            s += format_s % (' normal_form', ratio_normal_form, weight_normal_form,weight_normal_form/counter, ratio_normal_form * weight_normal_form, ratio_normal_form * weight_normal_form/counter)
            s += format_s % ('soundex van normal_form', ratio_normal_form_soundex, weight_normal_form_soundex,weight_normal_form_soundex/counter, ratio_normal_form_soundex* weight_normal_form_soundex, ratio_normal_form_soundex * weight_normal_form_soundex/counter)
            s += format_s % ('soundex van geslachtsnaam1', ratio_geslachtsnaam1, weight_geslachtsnaam1,weight_geslachtsnaam1/counter, ratio_geslachtsnaam1 * weight_geslachtsnaam1, ratio_geslachtsnaam1 * weight_geslachtsnaam1/counter)
            s += format_s % ('geslachtsnaam', ratio_geslachtsnaam2, weight_geslachtsnaam2,weight_geslachtsnaam2/counter,  ratio_geslachtsnaam2 *weight_geslachtsnaam2 , ratio_geslachtsnaam2 * weight_geslachtsnaam2/counter)
            s += format_s % ('initials', ratio_initials, weight_initials, weight_initials/counter, ratio_initials *weight_initials, ratio_initials * weight_initials/counter)
            s += '\tTOTAL  (numerator)                                       | %s (counter = %s)\n' %  (counter, numerator)
            
            return s
        return final_ratio

    def explain_ratio(self, n1, n2):
        return self.ratio(n1, n1, explain=1) 