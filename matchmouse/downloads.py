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
import logging
from gi.repository import Gtk

class MatchMouseDownloadsMinder( threading.Thread ):

    browser = None
    running = True
    downloads = []
    downloads_lock = None
    logger = None

    def __init__( self, browser ):
        self.logger = logging.getLogger( 'matchmouse.downloads.minder' )
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

class MatchMouseDownloadsTab( Gtk.Frame, threading.Thread ):

    browser = None
    window = None
    tabs = None
    updating = True
    txt_fields = {}
    downloads_frames = []
    downloads_progresses = []
    downloads_labels = []
    vbox = None
    logger = None

    def __init__( self, browser ):

        Gtk.Frame.__init__( self ) 
        threading.Thread.__init__( self )

        self.logger = logging.getLogger( 'matchmouse.downloads.viewer' )

        self.browser = browser

        self.vbox = Gtk.VBox( spacing=5 )
        self.vbox.set_border_width( 5 )

        self.add( self.vbox )

    def _on_close( self, widget ):
        self.updating = False

    @staticmethod
    def _create_download_frame( filename ):
        frame = Gtk.Frame()
        label = Gtk.Label( filename )
        progress = Gtk.ProgressBar()

        vbox = Gtk.VBox( spacing=5 )
        vbox.pack_start( label, False, False, 0 )
        vbox.pack_start( progress, False, False, 0 )

        frame.add( vbox )

        return (frame, label, progress)

    def run( self ):
        while self.updating:
            for index_iter in range( 0, self.browser.downloads.count_downloads() ):

                download = self.browser.downloads.get_download( index_iter )

                # Create a new progress frame for this download if we need one.
                if index_iter >= len( self.downloads_frames ):

                    self.logger.debug( 'Adding download index: {}'.format(
                        index_iter
                    ) )

                    frame_tuple = MatchMouseDownloadsTab._create_download_frame(
                        download.get_destination()
                    )

                    self.downloads_frames.append( frame_tuple[0] )
                    self.downloads_labels.append( frame_tuple[1] )
                    self.downloads_progresses.append( frame_tuple[2] )
                    
                    self.vbox.pack_start(
                        self.downloads_frames[index_iter], False, False, 0
                    )
                    self.show_all()

                # Update progress bar.
                self.downloads_progresses[index_iter].set_fraction(
                    download.get_estimated_progress()
                )

            time.sleep( 1 )

