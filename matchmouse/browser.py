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

import sys
import gtk
import webkit
import logging
import syncher
import storage
from yaml import load, dump
try:
   import urllib.parse as urlparse
except:
   import urlparse

STATUSBAR_CONTEXT_LOADING = 1
STATUSBAR_CONTEXT_SYNCING = 2

class MatchMouseBrowser(): # needs GTK, Python, Webkit-GTK

   window = None
   web_view = None
   txt_url = None
   logger = None
   data = None
   syncher = None
   storage = None

   def __init__( self ):

      self.logger = logging.getLogger( 'matchmouse.browser' )

      self.window = gtk.Window()
      self.window.connect( 'delete_event', self._on_quit )

      mb = gtk.MenuBar()

      # Create the file menu.
      filemenu = gtk.Menu()
      filem = gtk.MenuItem( 'File' )
      filem.set_submenu( filemenu )

      openm = gtk.MenuItem( 'Open...' )
      openm.connect( 'activate', self._on_open )
      filemenu.append( openm )

      exitm = gtk.MenuItem( 'Exit' )
      exitm.connect( 'activate', self._on_quit )
      filemenu.append( exitm )

      mb.append( filem )

      # Create the bookmarks menu.
      bookmarksmenu = gtk.Menu()
      bookmarksm = gtk.MenuItem( 'Bookmarks' )
      bookmarksm.set_submenu( bookmarksmenu )

      mb.append( bookmarksm )

      # Create the tools menu.
      toolsmenu = gtk.Menu()
      toolsm = gtk.MenuItem( 'Tools' )
      toolsm.set_submenu( toolsmenu )

      syncm = gtk.MenuItem( 'Sync Now' )
      syncm.connect( 'activate', self._on_sync )
      toolsmenu.append( syncm )

      mb.append( toolsm )

      # Create the web controls.
      self.txt_url = gtk.Entry()
      self.txt_url.connect( 'activate', self._on_txt_url_activate )

      self.web_view = webkit.WebView()
      self.web_view.connect( 'load-started', self._on_load_started )
      self.web_view.connect( 'load-finished', self._on_load_finished )

      web_scroll = gtk.ScrolledWindow()
      web_scroll.add( self.web_view )

      # Add a status bar.
      self.statusbar = gtk.Statusbar()

      # Pack and display.
      vbox = gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      vbox.pack_start( mb, False, False, 0 )
      vbox.pack_start( self.txt_url, False, False )
      vbox.pack_start( web_scroll, True, True )
      vbox.pack_start( self.statusbar, False, False, 0 )
      self.window.add( vbox )
      self.window.show_all()

      # Setup storage.
      self.storage = storage.MatchMouseStorage( 'storage.db' )

      # TODO: Put this somewhere more sensible.
      with open( 'sync.yaml' ) as sync_config_file:
         sync_config = load( sync_config_file )
      self.syncher = syncher.MatchMouseSyncher(
         self,
         sync_config['Server'],
         sync_config['Username'],
         sync_config['Password'],
         sync_config['Key']
      )

      gtk.main()

   def open( self, url, sync_txt=True ):

      # Make sure the URL has a valid scheme.
      url_tuple = urlparse.urlparse( url )
      if '' == url_tuple.scheme:
         url = 'http://' + url

      self.logger.debug( 'Opening URL: {}'.format( url ) )

      # Only reset the URL bar if asked to.
      if sync_txt:
         self.txt_url.set_text( url )

      # Actually change the page.
      self.window.set_title( 'MatchMouse - {}'.format( url ) )
      self.web_view.open( url )

   def _on_txt_url_activate( self, entry ):
      self.open( entry.get_text(), False )

   def _on_open( self, widget ):
      pass

   def _on_load_started( self, web_view, frame ):
      self.statusbar.push(
         # TODO: Get URL.
         STATUSBAR_CONTEXT_LOADING, 'Loading {}...'.format( '' )
      )

   def _on_load_finished( self, web_view, frame ):
      self.statusbar.pop( STATUSBAR_CONTEXT_LOADING )

   def _on_sync( self, widget ):
      self.statusbar.push( STATUSBAR_CONTEXT_SYNCING, 'Syncing...' )
      self.syncher.sync()
      self.statusbar.pop( STATUSBAR_CONTEXT_SYNCING )

   def _on_quit( self, widget ):
      self.storage.shutdown()
      gtk.main_quit()

