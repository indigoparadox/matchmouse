#!/usr/bin/env python

'''
This file is part of MatchMouse.

MatchMouse is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

MatchMouse is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more 
details.

You should have received a copy of the GNU General Public License along
with MatchMouse.  If not, see <http://www.gnu.org/licenses/>.
'''

import sqlite3

class MatchMouseStorage():

   cur = None
   db = None
   db_path = ''

   def __init__( self, db_path ):

      self.db_path = db_path
      self.db = sqlite3.connect( db_path ):

      self.cur.execute(
         'CREATE TABLE bookmarks ' + \
            '(title text, url text, tags text, path text)'
      )

