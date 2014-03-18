##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gerbrandy S.R.L.
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

import re

tokens_re = re.compile('(\(|\)|[\w]*[\w\!\?\*\.\']|\,|\-)(\s*)', re.UNICODE)

def tokens(s):
    """return list of pairs (word, tail)"""
    if s:
        return tokens_re.findall(s)
    else:
        return []
    

class Token:
    def __init__(self, word, ctype=None, tail=None):
        self._word = unicode(word)
        self._ctype = ctype
        self._tail = tail
        self._next = self._prev = self._index = None
        
    def __repr__(self):
        return unicode((self.word(), self.ctype()))
        return '<Token %s - %s>' % (self.word(), self.ctype())
    def next(self):
        return self._next 
    def prev(self):
        return self._prev
    def index(self):
        return self._index
    def word(self):
        return self._word
    def tail(self):
        return self._tail or ''
    def ctype(self):
        return self._ctype
    def __eq__(self, other):
        if isinstance(other, Token):
            return self._word == other._word and self._ctype == other._ctype
        elif type(other) == type((1,)):
            return self._word == other[0] and self._ctype == other[1]
        
class TokenDict(list):
    def keys(self):
        return [x.word() for x in self]
    def types(self):
        return set(x.ctype() for x in self)
    def append(self, token):
        
        if not isinstance(token, Token):
            raise
        if len(self) > 0:
            token._prev = self[-1]
            token._prev._next = token
        token._index = len(self)
        list.append(self, token)
    
    def __setitem__(self, idx, token):
        token._index = idx
        if idx > 0:
            token._prev = self[idx-1]
            token._prev._next = token 
        if idx < len(self) -1:
            token._next = self[idx + 1]
            token._next._prev = token
            
        list.__setitem__(self, idx, token)
    
    def serialize(self):
        result = ''
        for token in self:
            result += token.word() + token.tail()
        return result