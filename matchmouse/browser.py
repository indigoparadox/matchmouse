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
from gi.repository import Gtk
import logging
try:
   import storage
   import storage
   import tab
except ImportError:
   import matchmouse.syncstorage as syncstorage
   import matchmouse.storage as storage
   import matchmouse.tab as tab

STATUSBAR_CONTEXT_LOADING = 1
STATUSBAR_CONTEXT_SYNCING = 2

STORAGE_PATH = 'storage.db'
SYNCHER_CONFIG_PATH = 'sync.yaml'

class MatchMouseBrowser(): # needs GTK, Python, Webkit-GTK

   window = None
   web_view = None
   txt_url = None
   logger = None
   synching = False
   bookmarks = {}
   bookmarksm = None
   tabbook = None
   bm_bar = None

   def __init__( self ):

      self.logger = logging.getLogger( 'matchmouse.browser' )

      self.window = Gtk.Window()
      self.window.connect( 'delete_event', self._on_quit )

      mb = Gtk.MenuBar()

      # Create the file menu.
      filemenu = Gtk.Menu()
      filem = Gtk.MenuItem( 'File' )
      filem.set_submenu( filemenu )

      newtabm = Gtk.MenuItem( 'New Tab...' )
      newtabm.connect( 'activate', self._on_new_tab )
      filemenu.append( newtabm )

      openm = Gtk.MenuItem( 'Open...' )
      openm.connect( 'activate', self._on_open )
      filemenu.append( openm )

      exitm = Gtk.MenuItem( 'Exit' )
      exitm.connect( 'activate', self._on_quit )
      filemenu.append( exitm )

      mb.append( filem )

      # Create the bookmarks menu.
      bookmarksmenu = Gtk.Menu()
      self.bookmarksm = Gtk.MenuItem( 'Bookmarks' )
      self.bookmarksm.set_submenu( bookmarksmenu )

      mb.append( self.bookmarksm )

      # Create the tools menu.
      toolsmenu = Gtk.Menu()
      toolsm = Gtk.MenuItem( 'Tools' )
      toolsm.set_submenu( toolsmenu )

      syncm = Gtk.MenuItem( 'Sync Now' )
      syncm.connect( 'activate', self._on_sync )
      toolsmenu.append( syncm )

      mb.append( toolsm )

      # Add a bookmarks toolbar.
      self.bm_bar = Gtk.Toolbar()

      # Create the tab notebook.
      self.tabbook = Gtk.Notebook()
      #self.tabbook.set_tab_pos( Gtk.POS_TOP )

      # Add a status bar.
      self.statusbar = Gtk.Statusbar()

      # Pack and display.
      vbox = Gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      vbox.pack_start( mb, False, False, 0 )
      vbox.pack_start( self.bm_bar, False, False, 0 )
      vbox.pack_start( self.tabbook, True, True, 0 )
      vbox.pack_start( self.statusbar, False, False, 0 )
      self.window.add( vbox )
      self.window.show_all()

      # Setup bookmarks menu.
      self.rebuild_bookmarks()

      Gtk.main()

   def open_tab( self, url=None ):
      
      # Create the label/close button/frame.
      tab_label = Gtk.Label( 'Tab' )

      tab_close = Gtk.Button()
      tab_close_image = Gtk.Image()
      tab_close_image.set_from_icon_name(
         'window-close', Gtk.IconSize.SMALL_TOOLBAR
      )
      tab_close.set_image( tab_close_image )
      tab_close.connect( 'clicked', self._on_tab_close )

      tab_frame = tab.MatchMouseBrowserTab( self, tab_label, tab_close, url )

      # Setup a little HBox to hold the label/close button.
      hbox = Gtk.HBox( spacing=5 )
      hbox.pack_start( tab_label, True, True, 0 )
      hbox.pack_start( tab_close, False, False, 0 )
      hbox.show_all()

      tab_close.tab_index = self.tabbook.append_page( tab_frame, hbox )

      self.window.show_all()

   def close_tab( self, index=None ):
      if None != index:
         self.logger.debug( 'Closing tab: {}'.format( index ) )

         # Adjust indexes so that they stay consistent.
         for index_iter in range( 0, self.tabbook.get_n_pages() ):
            if index < index_iter:
               self.logger.debug(
                  'Tab {} becomes {}...'.format( index_iter, index_iter - 1 )
               )
               self.tabbook.get_nth_page( index_iter ).close.tab_index -= 1

         self.tabbook.remove_page( index )

   def _rebuild_bookmark_menu( self, bm_parent ):
      bookmarksmenu = Gtk.Menu()
      for bookmark_iter in bm_parent:
         bmm_iter = Gtk.MenuItem( bookmark_iter['title'] )

         # Create link/submenu as appropriate.
         if 'folder' == bookmark_iter['type']:
            submenu = self._rebuild_bookmark_menu( bookmark_iter['children'] )
            bmm_iter.set_submenu( submenu )
         elif 'bookmark' == bookmark_iter['type']:
            bmm_iter.connect( 'activate', self._on_open_bookmark )
            bmm_iter.bm_url = bookmark_iter['url']
         else:
            # Skip queries or other types.
            continue

         bookmarksmenu.append( bmm_iter )

      return bookmarksmenu

   def _rebuild_bookmark_tb( self, bm_parent ):

      for index_iter in range( self.bm_bar.get_n_items(), 0 ):
         self.bm_bar.remove( index_iter )
      
      for bookmark_iter in bm_parent:
         bmb_img_iter = Gtk.Image()
         bmb_img_iter.set_from_icon_name( 
            'image-missing', Gtk.IconSize.SMALL_TOOLBAR
         )

         bmb_label_iter = Gtk.Label( bookmark_iter['title'] )

         hbox_iter = Gtk.HBox()
         hbox_iter.pack_start( bmb_img_iter, False, False, 0 )
         hbox_iter.pack_start( bmb_label_iter, False, False, 0 )

         bmb_iter = Gtk.ToolButton( label_widget=hbox_iter )

         if 'bookmark' == bookmark_iter['type']:
            bmb_iter.connect( 'clicked', self._on_open_bookmark )
            bmb_iter.bm_url = bookmark_iter['url']

         self.bm_bar.insert( bmb_iter, -1 )

   def rebuild_bookmarks( self, reload=True ):

      ''' Rebuild the bookmarks menu from storage. '''
      
      # Grab bookmarks from storage.
      my_storage = storage.MatchMouseStorage( STORAGE_PATH )
      self.bookmarks = my_storage.list_bookmarks()

      # Put up the menus.
      bookmarksmenu = self._rebuild_bookmark_menu( self.bookmarks[0] )
      self.bookmarksm.set_submenu( bookmarksmenu )

      self._rebuild_bookmark_tb( self.bookmarks[1] )

      self.window.show_all()

   def _on_new_tab( self, widget ):
      self.open_tab()

   def _on_tab_close( self, widget ):
      self.close_tab( index=widget.tab_index )

   def _on_open_bookmark( self, widget ):
      #current_tab = \
      #   self.tabbook.get_nth_page( self.tabbook.get_current_page() )
      #current_tab.open( widget.bm_url, True )

      self.open_tab( url=widget.bm_url )

   def _on_open( self, widget ):
      pass

   def _on_quit( self, widget ):
      #if None != self.storage:
      #   self.storage.commit()
      #   self.storage.close()
      Gtk.main_quit()

   def _on_sync( self, widget ):
      # TODO: Put sync in a separate thread.
      #self.syncher.sync()

      if not self.synching:
         self.statusbar.push( STATUSBAR_CONTEXT_SYNCING, 'Syncing...' )
         self.synching = True
         storage_sync = syncstorage.MatchMouseSyncStorage(
            self, SYNCHER_CONFIG_PATH, STORAGE_PATH
         )
         storage_sync.start()

   def on_sync_complete( self ):
      self.statusbar.pop( STATUSBAR_CONTEXT_SYNCING )
      #self.storage = storage.MatchMouseStorage( STORAGE_PATH )
      self.synching = False
      self.rebuild_bookmarks()

