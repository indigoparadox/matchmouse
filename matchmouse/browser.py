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

class MatchMouseBrowser(): # needs GTK, Python, Webkit-GTK

   window = None
   web_view = None
   txt_url = None

   def __init__( self ):

      self.window = gtk.Window()
      self.window.connect( 'delete_event', gtk.main_quit )

      mb = gtk.MenuBar()

      # Create the file menu.
      filemenu = gtk.Menu()
      filem = gtk.MenuItem( 'File' )
      filem.set_submenu( filemenu )

      openm = gtk.MenuItem( 'Open...' )
      openm.connect( 'activate', self.on_open )
      filemenu.append( openm )

      exitm = gtk.MenuItem( 'Exit' )
      exitm.connect( 'activate', gtk.main_quit )
      filemenu.append( exitm )

      mb.append( filem )

      # Create the web controls.
      self.txt_url = gtk.Entry()
      self.txt_url.connect( 'activate', self._txt_url_activate )

      self.web_view = webkit.WebView()

      web_scroll = gtk.ScrolledWindow()
      web_scroll.add( self.web_view )

      # Pack and display.
      vbox = gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      vbox.pack_start( mb, False, False, 0 )
      vbox.pack_start( self.txt_url, False, False )
      vbox.pack_start( web_scroll, fill=True, expand=True )
      self.window.add( vbox )
      self.window.show_all()

      gtk.main()

   def _txt_url_activate( self, entry ):
      self.web_view.open( entry.get_text() )

   def open( self, url ):
      self.txt_url.set_text( url )
      self.window.set_title( 'MatchMouse - {}'.format( url ) )
      self.web_view.open( url )

   def on_open( self, widget ):
      pass

