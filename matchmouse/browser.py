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

from gi.repository import Gtk
from gi.repository import WebKit2
import sys
import logging
import os
try:
   import syncstorage
   import storage
   import tab
   import options
   import downloads
except ImportError:
   import matchmouse.syncstorage as syncstorage
   import matchmouse.storage as storage
   import matchmouse.tab as tab
   import matchmouse.options as options
   import matchmouse.downloads as downloads

STATUSBAR_CONTEXT_LOADING = 1
STATUSBAR_CONTEXT_SYNCING = 2

DEFAULT_CACHE_DIR = '/tmp/matchmouse'

ICON_LOCATIONS = [
   '/usr/share/pixmaps/matchmouse.png'
   'matchmouse.png'
]

class MatchMouseBrowser(): # needs GTK, Python, Webkit-GTK

   window = None
   web_view = None
   logger = None
   synching = False
   bookmarks = {}
   bookmarksm = None
   bookmarkstb = None
   tabbook = None
   downloads = None

   bookmarks_menuitems = {}

   def __init__( self ):

      self.logger = logging.getLogger( 'matchmouse.browser' )

      self.window = Gtk.Window()
      self.window.set_title( 'MatchMouse Browser' )
      self.window.connect( 'delete_event', self._on_quit )

      # TODO: Try to find matchmouse.png on the system.
      for location_iter in ICON_LOCATIONS:
         if os.path.isfile( location_iter ):
            self.window.set_icon_from_file( location_iter )
            break

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

      downloadsm = Gtk.MenuItem( 'Downloads...' )
      downloadsm.connect( 'activate', self._on_downloads )
      toolsmenu.append( downloadsm )

      optionsm = Gtk.MenuItem( 'Options...' )
      optionsm.connect( 'activate', self._on_options )
      toolsmenu.append( optionsm )

      mb.append( toolsm )

      # Add a bookmarks toolbar.
      self.bookmarkstb = Gtk.MenuBar()

      # Create the tab notebook.
      self.tabbook = Gtk.Notebook()
      #self.tabbook.set_tab_pos( Gtk.POS_TOP )

      # Add a status bar.
      self.statusbar = Gtk.Statusbar()

      # Pack and display.
      vbox = Gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      vbox.pack_start( mb, False, False, 0 )
      vbox.pack_start( self.bookmarkstb, False, False, 0 )
      vbox.pack_start( self.tabbook, True, True, 0 )
      vbox.pack_start( self.statusbar, False, False, 0 )
      self.window.add( vbox )
      self.window.show_all()

      # Load options.
      my_storage = storage.MatchMouseStorage()

      # Setup bookmarks menu.
      self.rebuild_bookmarks( reload_from_storage=my_storage )

      # Setup the default web context.
      cache_dir = my_storage.get_option( 'cache_dir' )
      if None == cache_dir:
         self.logger.debug( 'No cache directory specified. Using default...' )
         cache_dir = DEFAULT_CACHE_DIR
      if not os.path.isdir( cache_dir ):
         self.logger.debug( 'Cache directory not found. Creating...' )
         os.mkdir( cache_dir )

      self.context = WebKit2.WebContext.get_default()
      self.context.set_disk_cache_directory( cache_dir )

      #self.context.set_process_model(
      #   WebKit2.ProcessModel.MULTIPLE_SECONDARY_PROCESSES
      #)

      self.context.connect( 'download-started', self._on_download_started )

      my_storage.close()

      # Setup download manager.
      self.downloads = downloads.MatchMouseDownloadsMinder( self )
      self.downloads.start()

      Gtk.main()

   def _create_tab( self, frame, title='New Tab' ):

      # Create the label/close button/frame.
      tab_label = Gtk.Label( title )

      tab_close = Gtk.Button()
      tab_close_image = Gtk.Image()
      tab_close_image.set_from_icon_name(
         'window-close', Gtk.IconSize.SMALL_TOOLBAR
      )
      tab_close.set_image( tab_close_image )
      tab_close.connect( 'clicked', self._on_tab_close )

      # Set the label/close so the tab can change its own label later.
      frame.label = tab_label
      frame.close = tab_close

      # Setup a little HBox to hold the label/close button.
      hbox = Gtk.HBox( spacing=5 )
      hbox.pack_start( tab_label, True, True, 0 )
      hbox.pack_start( tab_close, False, False, 0 )
      hbox.show_all()

      tab_close.tab_index = self.tabbook.append_page( frame, hbox )

      self.window.show_all()

   def open_tab_page( self, url=None, bm_id=None, view=None ):

      tab_frame = tab.MatchMouseBrowserTab( self, url=url, view=view )

      # Hold on to the bookmark ID for favicon purposes.
      if bm_id:
         tab_frame.bm_id = bm_id

      self._create_tab( tab_frame )

   def open_tab_downloads( self ):
      tab_frame = downloads.MatchMouseDownloadsTab( self )
      tab_frame.start()
      self._create_tab( tab_frame, title='Downloads' )

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

         # If the tab is an updating type, stop it.
         self.tabbook.get_nth_page( index ).updating = False

         self.tabbook.remove_page( index )

   def _rebuild_bookmark_menu( self, bm_parent, bookmarksmenu=None ):

      if None == bookmarksmenu:
         bookmarksmenu = Gtk.Menu()

      for bookmark_iter in bm_parent:
         bmm_iter = Gtk.ImageMenuItem( bookmark_iter['title'] )

         # Create link/submenu as appropriate.
         if 'folder' == bookmark_iter['type']:
            submenu = self._rebuild_bookmark_menu( bookmark_iter['children'] )
            bmm_iter.set_submenu( submenu )

            # Set a folder icon.
            bmm_image_iter = Gtk.Image()
            bmm_image_iter.set_from_icon_name(
               'folder', Gtk.IconSize.SMALL_TOOLBAR
            )
            bmm_iter.set_image( bmm_image_iter )

         elif 'bookmark' == bookmark_iter['type']:
            bmm_iter.connect( 'activate', self._on_open_bookmark )
            bmm_iter.bm_url = bookmark_iter['url']
            bmm_iter.bm_id = bookmark_iter['id']

            # Load the icon if present.
            bmm_image_iter = Gtk.Image()
            if bookmark_iter['icon']:
               bmm_image_iter.set_from_pixbuf( bookmark_iter['icon'] )
            else:
               bmm_image_iter.set_from_icon_name(
                  'image-missing', Gtk.IconSize.SMALL_TOOLBAR
               )
            bmm_iter.set_image( bmm_image_iter )
            bmm_iter.set_submenu( None )

            # Add the menu item to a dict so that we can quickly change the
            # icon or whatever later.
            self.bookmarks_menuitems[bookmark_iter['id']] = bmm_iter

         else:
            # Skip queries or other types.
            continue

         bookmarksmenu.append( bmm_iter )

      return bookmarksmenu

   def rebuild_bookmarks( self, reload_from_storage=None ):

      ''' Rebuild the bookmarks menu from storage. '''
      
      if reload_from_storage:
         # Grab bookmarks from storage.
         self.bookmarks = reload_from_storage.list_bookmarks()

      # Put up the menus.
      bookmarksmenu = self._rebuild_bookmark_menu( self.bookmarks[0] )
      self.bookmarksm.set_submenu( bookmarksmenu )

      # TODO: Can we cache the bookmarks in binary form and then just rebuild
      #       the menu on launch?
      self._rebuild_bookmark_menu( self.bookmarks[1], self.bookmarkstb )

      self.window.show_all()

   def set_bookmark_icon( self, bm_id, icon ):

      storage.MatchMouseStorage.set_bookmark_icon( bm_id, icon )

      # Quickly set the new icon on the menus/toolbar.
      icon_image = Gtk.Image()
      icon_image.set_from_pixbuf( icon )
      self.bookmarks_menuitems[bm_id].set_image( icon_image )

   def _on_new_tab( self, widget ):
      self.open_tab_page()

   def _on_tab_close( self, widget ):
      self.close_tab( index=widget.tab_index )

   def _on_open_bookmark( self, widget ):
      #current_tab = \
      #   self.tabbook.get_nth_page( self.tabbook.get_current_page() )
      #current_tab.open( widget.bm_url, True )

      self.open_tab_page( url=widget.bm_url, bm_id=widget.bm_id )

   def _on_open( self, widget ):
      pass

   def _on_quit( self, widget ):
      self.downloads.running = False

      # If there are updating tabs, stop them.
      for index_iter in range( 0, self.tabbook.get_n_pages() ):
         self.tabbook.get_nth_page( index_iter ).updating = False

      Gtk.main_quit()

   def _on_sync( self, widget ):
      if not self.synching:
         self.statusbar.push( STATUSBAR_CONTEXT_SYNCING, 'Syncing...' )
         self.synching = True
         storage_sync = syncstorage.MatchMouseSyncStorage( self )
         storage_sync.start()

   def on_sync_complete( self ):
      self.statusbar.pop( STATUSBAR_CONTEXT_SYNCING )
      self.synching = False
      self.rebuild_bookmarks()

   def _on_options( self, widget ):
      options.MatchMouseOptionsWindow()

   def _on_downloads( self, widget ):
      self.open_tab_downloads()

   # = Download Handlers =

   # TODO: Work these into the MatchMouseDownloads* classes and use signals
   #       instead of a polling thread.

   def _on_download_started( self, context, download ):
      download.connect( 'decide-destination', self._on_decide_destination )
      download.connect( 'created-destination', self._on_created_destination )
      return True

   def _on_decide_destination( self, download, suggested_filename ):
      # Grab the downloads directory from storage.
      # TODO: Show a file chooser dialog.
      my_storage = storage.MatchMouseStorage()
      download_dir = my_storage.get_option( 'cache_dir' )
      if None == download_dir:
         download_dir = os.path.expanduser( '~' )
      my_storage.close()

      download.set_destination( 'file://' + os.path.join(
         download_dir, suggested_filename
      ) )

   def _on_created_destination( self, download, destination ):
      self.downloads.add_download( download )

