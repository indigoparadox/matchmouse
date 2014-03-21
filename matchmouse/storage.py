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
import logging

RO_SYSTEM_OPTIONS = ['version']

class MatchMouseStorage():

   cur = None
   db = None
   db_path = ''

   def __init__( self, db_path ):

      self.logger = logging.getLogger( 'matchmouse.storage' )

      self.db_path = db_path
      self.db = sqlite3.connect( db_path )
      self.cur = self.db.cursor()

      db_version = self.get_option( 'version' )

      # See if we need to setup a new DB, upgrade an existing DB, or do nothing.
      if None == db_version:
         # No database, so create the latest version.
         self.logger.debug( 'No version field detected. Setting up DB.' )
         self.cur.execute( 'CREATE TABLE system (key text, value text)' )
         self.cur.execute( 'INSERT INTO system VALUES(?, ?)', ('version', '1') )
         self.cur.execute(
            'CREATE TABLE bookmarks ' + \
               '(title text, url text, tags text, path text)'
         )
      else:
         self.logger.debug( 'Storage DB version is: {}'.format( db_version ) )

   def get_option( self, key ):

      value = None
      try:
         self.cur.execute( 'SELECT value FROM system WHERE key=?', (key,) )
         for row in self.cur.fetchall():
            value = int( row[0] )
      except sqlite3.OperationalError:
         self.logger.debug( 'Option "{}" not defined.'.format( key ) )

      return value

   def set_option( self, key, value ):

      # Don't allow arbitrarily overwriting read-only options.
      if key in RO_SYSTEM_OPTIONS:
         self.logger.error(
            'Denied attempt to set read-only option: {}'.format( key )
         )
         return 1

      # Are we inserting a new option or updating an existing option?
      if None == self.get_option( key ):
         # Inserting.
         self.cur.execute( 'INSERT INTO system VALUES(?, ?)', (key, value) )
      else:
         # Updating.
         self.cur.execute(
            'UPDATE system SET value=? WHERE key=?', (value, key)
         )

   def add_bookmark( self, title, url, tags, path ):
      pass

