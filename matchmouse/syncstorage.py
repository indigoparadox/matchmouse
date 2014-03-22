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

import threading
import time
import logging
try:
   import storage
   import syncher
except ImportError:
   import matchmouse.storage as storage
   import matchmouse.syncher as syncher
from yaml import load, dump

SYNC_BM_KEYS = ['id', 'title', 'bmkUri', 'tags', 'keyword', 'parentid', 'type']

class MatchMouseSyncStorage( threading.Thread ):

   browser = None
   syncher_config_path = ''

   def __init__( self, browser, syncher_config_path ):
      self.browser = browser
      self.syncher_config_path = syncher_config_path
      threading.Thread.__init__( self )

   def run( self ):

      logger = logging.getLogger( 'matchmouse.syncstorage' )
      
      # Create storage/syncher instances in this thread.
      my_storage = storage.MatchMouseStorage()
      with open( self.syncher_config_path ) as sync_config_file:
         sync_config = load( sync_config_file )
      my_syncher = syncher.MatchMouseSyncher(
         self,
         sync_config['Server'],
         sync_config['Username'],
         sync_config['Password'],
         sync_config['Key']
      )

      # See if we can even do a partial sync.
      last_sync = my_storage.get_option( 'last_sync' )
      this_sync = time.time()

      try:
         for bookmark_id_iter in my_syncher.list_bookmarks( last_sync ):
            # TODO: Check if bookmark exists in storage and add/remove it
            #       accordingly.
            bookmark_iter = my_syncher.request_bookmark( bookmark_id_iter )
            if 'deleted' in bookmark_iter.keys() and bookmark_iter['deleted']:
               # Delete bookmark if it exists.
               my_storage.delete_bookmark( bookmark_iter['id'] )
            else:
               
               # Make sure each bookmark/item is valid.
               for key_iter in SYNC_BM_KEYS:
                  if key_iter not in bookmark_iter.keys() \
                  or None == bookmark_iter[key_iter]:
                     bookmark_iter[key_iter] = ''

               # Perform the update.
               my_storage.set_bookmark(
                  bookmark_iter['id'],
                  bookmark_iter['title'],
                  bookmark_iter['bmkUri'],
                  bookmark_iter['tags'],
                  bookmark_iter['keyword'],
                  bookmark_iter['parentid'],
                  bookmark_iter['type']
               )
         # This is inside the try so it should only record on success.
         my_storage.set_option( 'last_sync', str( int( this_sync ) ) )

      except Exception as e:
         logger.error( 'Unable to complete sync: {}'.format( e ) )
      
      finally:
         my_storage.commit()
         my_storage.close()
         self.browser.on_sync_complete()

