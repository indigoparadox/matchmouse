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

class MatchMouseOptionsWindow():

   window = None
   tabs = None

   fields = {}

   def __init__( self ):

      self.window = Gtk.Window()
      self.window.set_title( 'MatchMouse Options' )
      self.window.connect( 'delete_event', self._on_cancel )

      self.tabs = Gtk.Notebook()

      self._add_page( 'Content', FIELDS_CONTENT_KEYS )
      self._add_page( 'Sync', FIELDS_SYNC_KEYS )

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

   def _add_page( self, tab_label, keys ):

      ''' Create a tab and add it to the main options notebook. '''

      tab = Gtk.Frame()
      vbox = Gtk.VBox( spacing=5 )
      
      my_storage = storage.MatchMouseStorage()
      
      for label_iter in keys.keys():
         
         # Create and append the field.
         field_hbox = keys[label_iter]( label_iter )
         storage_key = '{}_{}'.format( tab_label.lower(), label_iter.lower() )
         self.fields[storage_key] = field_hbox[0]
         vbox.pack_start( field_hbox[1], False, False, 0 )

         # Add default data to the field.
         default = my_storage.get_option( storage_key )
         if default:
            self.fields[storage_key].set_text( default )
      
      my_storage.close()

      tab.add( vbox )
      self.tabs.append_page( tab, Gtk.Label( tab_label ) )

   @staticmethod
   def _create_field_txt( field_label ):
      hbox = Gtk.HBox( spacing=5 )
      field = Gtk.Entry()
      hbox.pack_start( Gtk.Label( field_label ), False, False, 0 )
      hbox.pack_start( field, True, True, 0 )
      return (field, hbox)

   @staticmethod
   def _create_field_dir( field_label ):
      hbox = Gtk.HBox( spacing=5 )
      field = Gtk.Label()
      btn_choose = Gtk.Button( 'Select...' )
      btn_choose.connect(
         'clicked',
         MatchMouseOptionsWindow._choose_directory,
         # TODO: Load default data in here?
         (field,'')
      )
      hbox.pack_start( Gtk.Label( field_label ), False, False, 0 )
      hbox.pack_start( field, True, True, 0 )
      hbox.pack_start( btn_choose, False, False, 0 )
      return (field, hbox)

   @staticmethod
   def _choose_directory( widget, data ):
      
      ''' Present the user with a directory chooser and return the chosen
      directory path. '''

      label = data[0]
      default = data[1]

      # TODO: Start in default directory.

      choose_dialog = Gtk.FileChooserDialog(
         title='Select Directory',
         buttons=( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK )
      )
      choose_dialog.set_action( Gtk.FileChooserAction.SELECT_FOLDER )

      rc = choose_dialog.run()
      if Gtk.ResponseType.OK == rc:
         label.set_text( choose_dialog.get_filename() )

      choose_dialog.destroy()

   def _on_cancel( self, widget ):
      self.window.destroy()

   def _on_ok( self, widget ):
      
      # Iterate through all options fields and save their values.
      my_storage = storage.MatchMouseStorage()
      for field_key_iter in self.fields.keys():
         my_storage.set_option(
            field_key_iter, self.fields[field_key_iter].get_text()
         )
      my_storage.commit()
      my_storage.close()

      self.window.destroy()

FIELDS_SYNC_KEYS = {
   'Server': MatchMouseOptionsWindow._create_field_txt,
   'Username': MatchMouseOptionsWindow._create_field_txt,
   'Password': MatchMouseOptionsWindow._create_field_txt,
   'Key': MatchMouseOptionsWindow._create_field_txt
}

FIELDS_CONTENT_KEYS = {
   'Downloads': MatchMouseOptionsWindow._create_field_dir,
}

