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

import base64
import requests

class MatchMouseSyncher():

   browser = None
   server = ''
   username = ''
   password = ''
   key = ''

   def __init__( self, browser, server='', username='', password='', key='' ):
      self.browser = browser
      self.server = server
      self.username = username
      self.password = password
      self.key = key

   def _encode_username( username ):
      return base64.b32encode( hashlib.sha1( username ).digest() ).lower()

   def _request_node( self ):
      url = '{}/user/1/{}/node/weave'.format( self.server, self.username )
      r = requests.get( url, auth=(self.username, self.password) )
      return r.read()

   def sync( self ):
      pass

