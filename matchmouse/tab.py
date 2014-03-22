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

import gtk
import webkit
import browser
try:
   import urllib.parse as urlparse
except:
   import urlparse

class MatchMouseBrowserTab( gtk.Frame ):

   browser = None
   txt_url = None
   img_icon = None
   web_view = None
   label = None
   close = None
   tab_close = -1

   def __init__( self, browser, label=None, close=None, url=None ):
      gtk.Frame.__init__( self ) 

      self.browser = browser
      self.label = label
      self.close = close

      # Create the web controls.
      self.txt_url = gtk.Entry()
      self.txt_url.connect( 'activate', self._on_txt_url_activate )

      self.web_view = webkit.WebView()
      self.web_view.connect( 'load-started', self._on_load_started )
      self.web_view.connect( 'load-finished', self._on_load_finished )

      web_scroll = gtk.ScrolledWindow()
      web_scroll.add( self.web_view )

      self.img_icon = gtk.Image()
      self.img_icon.set_from_stock(
         gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_SMALL_TOOLBAR
      )

      hbox_txt = gtk.HBox()
      hbox_txt.pack_start( self.img_icon, False, False, 0 )
      hbox_txt.pack_start( self.txt_url, True, True )

      vbox = gtk.VBox( spacing=5 )
      vbox.set_border_width( 0 )
      vbox.pack_start( hbox_txt, False, False )
      vbox.pack_start( web_scroll, True, True )
      self.add( vbox )
      #self.show_all()

      if url:
         self.open( url, True )

   def _on_txt_url_activate( self, entry ):
      self.open( entry.get_text(), False )

   def _on_load_started( self, web_view, frame ):
      self.browser.statusbar.push(
         # TODO: Get URL.
         browser.STATUSBAR_CONTEXT_LOADING, 'Loading {}...'.format( '' )
      )

      self.img_icon.set_from_stock(
         gtk.STOCK_REFRESH, gtk.ICON_SIZE_SMALL_TOOLBAR
      )

   def _on_load_finished( self, web_view, frame ):
      self.browser.statusbar.pop( browser.STATUSBAR_CONTEXT_LOADING )

      # TODO: Change the icon depending on load/SSL status.
      self.img_icon.set_from_stock(
         gtk.STOCK_OK, gtk.ICON_SIZE_SMALL_TOOLBAR
      )

   def open( self, url, sync_txt=True ):

      # Make sure the URL has a valid scheme.
      url_tuple = urlparse.urlparse( url )
      if '' == url_tuple.scheme:
         url = 'http://' + url

      #self.logger.debug( 'Opening URL: {}'.format( url ) )

      # Only reset the URL bar if asked to.
      if sync_txt:
         self.txt_url.set_text( url )

      # TODO: Set the tab title based on the page title.
      if self.label:
         self.label.set_text( url )

      # Actually change the page.
      #self.window.set_title( 'MatchMouse - {}'.format( url ) )
      self.web_view.open( url )

