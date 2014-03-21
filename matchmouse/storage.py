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
import json

RO_SYSTEM_OPTIONS = ['version']

class MatchMouseStorage():

   cur = None
   db = None
   db_path = ''

   def __init__( self, db_path ):

      self.logger = logging.getLogger( 'matchmouse.storage' )

      self.db_path = db_path
      self.db = sqlite3.connect( db_path )

      self.db.row_factory = sqlite3.Row

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
               '(id text, title text, url text, tags text, keyword text, ' + \
               'parent text, type text)'
         )
         self.cur.execute( 'CREATE UNIQUE INDEX id ON bookmarks (id)' )
      else:
         self.logger.debug( 'Storage DB version is: {}'.format( db_version ) )

      self.db.commit()

   def commit( self ):
      self.db.commit()

   def close( self ):
      self.db.close()

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

   def _list_bookmarks_children( self, folder_id ):

      bookmarks_branch = []
      try:
         self.cur.execute(
            'SELECT * FROM bookmarks WHERE parent=?', (folder_id,)
         )
         for row in self.cur.fetchall():
            # Use a proper dict we can manipulate.
            row = dict( row )

            if 'folder' == row['type']:
               # Recursively fetch children.
               row['children'] = self._list_bookmarks_children( row['id'] )

            # Add the whole mess to the tree.
            bookmarks_branch.append( row )
      except sqlite3.OperationalError:
         pass

      return bookmarks_branch

   def list_bookmarks( self ):

      bookmarks_root = self._list_bookmarks_children( 'menu' )

      return bookmarks_root

   def get_bookmark( self, bm_id ):
      
      try:
         self.cur.execute( 'SELECT * FROM bookmarks WHERE id=?', (bm_id,) )
         for row in self.cur.fetchall():
            return row
      except sqlite3.OperationalError:
         self.logger.debug( 'Bookmark "{}" not found.'.format( bm_id ) )

      return None

   def set_bookmark( self, bm_id, title, url, tags, keyword, parent, bm_type ):

      # Are we inserting a new bookmark or updating an existing bookmark?
      if None == self.get_bookmark( bm_id ):
         # Inserting.
         self.cur.execute(
            'INSERT INTO bookmarks ' + \
               '(id, title, url, tags, keyword, parent, type) ' + \
               'VALUES(?, ?, ?, ?, ?, ?, ?)',
            (bm_id, title, url, json.dumps( tags ), keyword, parent, bm_type)
         )
      else:
         # Updating.
         self.cur.execute(
            'UPDATE bookmarks ' + \
               'SET title=?, url=?, tags=?, keyword=?, parent=?, type=? ' + \
               'WHERE id=?',
            (title, url, json.dumps( tags ), keyword, parent, bm_type, bm_id)
         )

   def delete_bookmark( self, bm_id ):
      pass

