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
import hashlib
import json
import logging
import hmac
# FIXME: Find a python-3 solution.
from M2Crypto.EVP import Cipher

SYNC_API = '1.0'

class MatchMouseSyncher():

    logger = None
    browser = None
    server = ''
    username = ''
    password = ''
    local_key = ''
    #node = ''
    priv_key = ''
    priv_hmac = ''

    def __init__( self, browser, server='', username='', password='', key='' ):

        # Setup member fields.
        self.logger = logging.getLogger( 'matchmouse.syncher' )
        self.browser = browser
        self.server = server
        self.userhash = self._encode_username( username )
        self.password = password
        #self.node = self._request_node().rstrip( '/' )
        self.local_key = self._digest_key( key )

        #self.logger.debug( 'Node set to: {}'.format( self.node ) )

        default_key = self._decrypt_key( self.local_key )
        self.priv_key = default_key[0].decode( 'base64' )
        self.priv_hmac = default_key[1].decode( 'base64' )

    def _digest_key( self, key ):

        # Strip out/replace invalid characters.
        normalized_key = \
            key.replace( '-', '' ).replace( '8', 'l' ).replace( '9', 'o' ).upper()
        padding = (8-len(normalized_key) % 8) % 8
        normalized_key += '=' * padding
        normalized_key = base64.b32decode( normalized_key )

        # Return key digest.
        return hmac.new(
            normalized_key,
            '{}{}\x01'.format( 'Sync-AES_256_CBC-HMAC256', self.userhash ),
            hashlib.sha256
        ).digest()

    def _decrypt( self, payload, key ):

        ''' Decrypt payload fetched from server. '''

        ciphertext = payload['ciphertext'].decode( 'base64' )
        iv = payload['IV'].decode( 'base64' )

        # Perform the actual decryption.
        cipher = Cipher( alg='aes_256_cbc', key=key, iv=iv, op=0 )
        v = cipher.update( ciphertext )
        v = v + cipher.final()
        del cipher

        return json.loads( v )
        
    def _decrypt_key( self, key ):

        ''' Decrypt server-side key with our local key. '''

        data = self._request_path( 'storage/crypto/keys' )
        payload = json.loads( data['payload'] )
        return self._decrypt( payload, key )['default']

    def _encode_username( self, username ):
        return base64.b32encode( hashlib.sha1( username ).digest() ).lower()

    def _request_node( self ):

        # TODO: What is the node even for? Just returns "1" all the time.

        url = '{}/user/1.0/{}'.format( self.server, self.userhash )
        r = requests.get( url, auth=(self.userhash, self.password) )
        return r.text

    def _request_path( self, path ):
        url = '/'.join( (self.server, SYNC_API, self.userhash, path ) )
        r = requests.get( url, auth=(self.userhash, self.password) )
        return json.loads( r.text )

    def request_bookmark( self, id ):
        data = self._request_path( 'storage/bookmarks/{}'.format( id ) )
        payload = json.loads( data['payload'] )
        return self._decrypt( payload, self.priv_key )

    def list_bookmarks( self, last_sync=None, force_full=False ):

        if force_full or None == last_sync:
            return self._request_path( 'storage/bookmarks' )
        else:
            return self._request_path(
                'storage/bookmarks?newer={}'.format( last_sync )
            )

