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
try:
   import storage
except ImportError:
   import matchmouse.storage as storage

TXT_FIELDS_SYNC_KEYS = ['Server', 'Username', 'Password', 'Key']

class MatchMouseOptionsWindow():

   window = None
   tabs = None

   txt_fields = {}

   def __init__( self ):

      self.window = Gtk.Window()
      self.window.connect( 'delete_event', self._on_cancel )

      self.tabs = Gtk.Notebook()

      # Create Tab: Sync
      sync_tab = Gtk.Frame()
      sync_vbox = Gtk.VBox( spacing=5 )
      my_storage = storage.MatchMouseStorage()
      for label_iter in TXT_FIELDS_SYNC_KEYS:
         sync_txt_hbox = MatchMouseOptionsWindow._add_field( label_iter )
         storage_key = 'sync_{}'.format( label_iter.lower() )
         self.txt_fields[storage_key] = sync_txt_hbox[0]
         self.txt_fields[storage_key].set_text( my_storage.get_option(
            storage_key
         ) )
         sync_vbox.pack_start( sync_txt_hbox[1], False, False, 0 )
      my_storage.close()
      sync_tab.add( sync_vbox )
      self.tabs.append_page( sync_tab, Gtk.Label( 'Sync' ) )

      # Create OK/Cancel buttons.
      ok_btn = Gtk.Button( 'OK' )
      ok_btn.connect( 'clicked', self._on_ok )

      cancel_btn = Gtk.Button( 'Cancel' )
      cancel_btn.connect( 'clicked', self._on_cancel )

      # Pack and display.
      buttons_hbox = Gtk.HBox()
      buttons_hbox.pack_start( ok_btn, False, False, 0 )
      buttons_hbox.pack_start( cancel_btn, False, False, 0 )

      vbox = Gtk.VBox( spacing=5 )
      vbox.set_border_width( 5 )
      vbox.pack_start( self.tabs, True, True, 0 )
      vbox.pack_start( buttons_hbox, False, False, 0 )

      self.window.add( vbox )
      self.window.show_all()

   @staticmethod
   def _add_field( field_label ):
      hbox = Gtk.HBox( spacing=5 )
      txt_field = Gtk.Entry()
      hbox.pack_start( Gtk.Label( field_label ), False, False, 0 )
      hbox.pack_start( txt_field, True, True, 0 )
      return (txt_field, hbox)

   def _on_cancel( self, widget ):
      self.window.destroy()

   def _on_ok( self, widget ):
      
      # Iterate through all options fields and save their values.
      my_storage = storage.MatchMouseStorage()
      for field_key_iter in self.txt_fields.keys():
         my_storage.set_option(
            field_key_iter, self.txt_fields[field_key_iter].get_text()
         )
      my_storage.commit()
      my_storage.close()

      self.window.destroy()

