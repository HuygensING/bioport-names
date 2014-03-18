#!/usr/bin/env python    
# encoding=utf8

##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gebrandy S.R.L.
# 
# This file is part of bioport.
# 
# bioport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
##########################################################################


import unittest

from names.tokens import *

class TokensTestCase(unittest.TestCase):
    """test methods from common.py"""
    def test_tokens(self):
        s = 'Abc d? 1 d223r! (xxx)  *  --- \nMercier-Camier'
        t = tokens(s)
        self.assertEqual(''.join(['%s%s' % (word, tail) for word, tail in t]), s)
        
        self.assertEqual(tokens('H.P.'),[('H.', ''), ('P.', '')])
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TokensTestCase),
        ))

if __name__=='__main__':
    unittest.main()

        
