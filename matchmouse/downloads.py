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
from gi.repository import Gtk

class MatchMouseDownloadsMinder( threading.Thread ):

   browser = None
   running = True
   downloads = []
   downloads_lock = None

   def __init__( self, browser ):
      self.browser = browser
      self.downloads_lock = threading.Lock()
      threading.Thread.__init__( self )

   def run( self ):
      while self.running:
         #self.downloads_lock.acquire()
         # TODO: Update download status somehow?
         #self.downloads_lock.release()
         time.sleep( 1 )

   def add_download( self, download ):
      self.downloads_lock.acquire()
      self.downloads.append( download )
      self.downloads_lock.release()

   def get_download( self, index ):
      self.downloads_lock.acquire()
      try:
         dl = self.downloads[index]
      except:
         dl = None
      finally:
         self.downloads_lock.release()
      return dl

   def count_downloads( self ):
      self.downloads_lock.acquire()
      count = len( self.downloads )
      self.downloads_lock.release()
      return count

class MatchMouseDownloadsWindow( threading.Thread ):

   browser = None
   window = None
   tabs = None
   updating = True
   txt_fields = {}
   downloads_list_frame_vbox = None

   def __init__( self, browser ):

      self.browser = browser

      self.window = Gtk.Window()
      self.window.connect( 'delete_event', self._on_close )

      close_btn = Gtk.Button( 'Cancel' )
      close_btn.connect( 'clicked', self._on_close )

      # Pack and display.
      buttons_hbox = Gtk.HBox()
      buttons_hbox.pack_start( close_btn, False, False, 0 )

      vbox = Gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      #vbox.pack_start( self.tabs, True, True, 0 )
      vbox.pack_start( buttons_hbox, False, False, 0 )

      self.window.add( vbox )
      self.window.show_all()

      threading.Thread.__init__( self )

   def _on_close( self, widget ):
      self.updating = False
      self.window.destroy()

   def run( self ):
      while self.updating:
         for index_iter in range( 0, self.browser.downloads.count_downloads() ):
            download = self.browser.downloads.get_download( index_iter )
            print download.get_status()
         time.sleep( 1 )

