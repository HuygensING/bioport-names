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

from plone.memoize import volatile
from plone.memoize.ram import RAMCacheAdapter
from zope.app.cache import ram


global_cache = ram.RAMCache()
global_cache.update(maxAge=86400)
global_cache.update(maxEntries=100000)
global_cache.update(cleanupInterval=86400)

def store_in_cache(fun, *args, **kwargs):
    key = '%s.%s' % (fun.__module__, fun.__name__)
    return RAMCacheAdapter(global_cache, globalkey=key)

def cache(get_key):
    return volatile.cache(get_key, get_cache=store_in_cache)

