"""
Streamflix Helper Service
Provides Netflix-style auto-preview for episodes.
Monitors selected items and plays preview after hover delay.
"""

import xbmc
import xbmcgui
import xbmcaddon
import time
import threading

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')

# Configuration
HOVER_DELAY = 2.5  # Seconds before preview starts
PREVIEW_WINDOW_ID = 10025  # MyVideoNav window ID
PREVIEW_VOLUME = 40  # Preview volume (0-100)

class PreviewMonitor(xbmc.Monitor):
    """Monitor for Kodi events."""

    def __init__(self):
        super().__init__()
        self.preview_active = False
        self.last_item = None
        self.last_item_time = 0
        self.preview_thread = None
        self.stop_preview = False
        self.original_volume = 100

    def log(self, msg, level=xbmc.LOGDEBUG):
        xbmc.log(f"[{ADDON_ID}] {msg}", level)

    def get_current_item_path(self):
        """Get the file path of the currently selected item."""
        try:
            window = xbmcgui.Window(PREVIEW_WINDOW_ID)
            # Check if we're on the video nav window
            if xbmc.getCondVisibility('Window.IsVisible(MyVideoNav)'):
                # Check if viewing episodes
                if xbmc.getCondVisibility('Container.Content(episodes)'):
                    # Get the selected item's file path
                    path = xbmc.getInfoLabel('Container(50).ListItem.FileNameAndPath')
                    if path:
                        return path
        except:
            pass
        return None

    def get_current_item_label(self):
        """Get the label of the currently selected item."""
        try:
            if xbmc.getCondVisibility('Window.IsVisible(MyVideoNav)'):
                return xbmc.getInfoLabel('Container(50).ListItem.Label')
        except:
            pass
        return None

    def start_preview(self, path):
        """Start playing preview in windowed mode."""
        if self.preview_active:
            return

        self.log(f"Starting preview: {path}", xbmc.LOGINFO)
        self.preview_active = True

        # Store original volume and lower it for preview
        self.original_volume = xbmc.getInfoLabel('Player.Volume')

        # Set skin property to indicate preview is active
        xbmcgui.Window(10000).setProperty('StreamflixPreviewActive', 'true')
        xbmcgui.Window(10000).setProperty('StreamflixPreviewPath', path)

        # Play the video
        # Using PlayMedia with windowed parameter
        xbmc.executebuiltin(f'PlayMedia("{path}",1)')  # 1 = don't switch to fullscreen

        # Lower volume for preview
        time.sleep(0.5)
        if xbmc.getCondVisibility('Player.Playing'):
            xbmc.executebuiltin(f'SetVolume({PREVIEW_VOLUME})')

    def stop_preview_playback(self):
        """Stop the preview playback."""
        if not self.preview_active:
            return

        self.log("Stopping preview", xbmc.LOGINFO)

        # Stop playback if it's our preview
        if xbmc.getCondVisibility('Player.Playing'):
            xbmc.executebuiltin('PlayerControl(Stop)')

        # Restore volume
        if self.original_volume:
            try:
                xbmc.executebuiltin(f'SetVolume({self.original_volume})')
            except:
                xbmc.executebuiltin('SetVolume(100)')

        # Clear skin properties
        xbmcgui.Window(10000).clearProperty('StreamflixPreviewActive')
        xbmcgui.Window(10000).clearProperty('StreamflixPreviewPath')

        self.preview_active = False

    def preview_worker(self, path, item_label):
        """Worker thread that waits and then starts preview."""
        start_time = time.time()

        while not self.stop_preview:
            # Check if we've waited long enough
            if time.time() - start_time >= HOVER_DELAY:
                # Verify we're still on the same item
                current_label = self.get_current_item_label()
                if current_label == item_label:
                    # Still on same item, start preview
                    self.start_preview(path)
                break

            # Check every 100ms
            time.sleep(0.1)

            # Check if item changed
            current_label = self.get_current_item_label()
            if current_label != item_label:
                break


class StreamflixService:
    """Main service class."""

    def __init__(self):
        self.monitor = PreviewMonitor()
        self.running = True
        self.last_checked_item = None

    def log(self, msg, level=xbmc.LOGDEBUG):
        xbmc.log(f"[{ADDON_ID}] {msg}", level)

    def run(self):
        """Main service loop."""
        self.log("Streamflix Helper service started", xbmc.LOGINFO)

        while self.running and not self.monitor.abortRequested():
            # Check if we're on the video nav window viewing episodes
            if (xbmc.getCondVisibility('Window.IsVisible(MyVideoNav)') and
                xbmc.getCondVisibility('Container.Content(episodes)')):

                # Get current item
                current_path = self.monitor.get_current_item_path()
                current_label = self.monitor.get_current_item_label()

                if current_path and current_label:
                    # Check if item changed
                    if current_label != self.last_checked_item:
                        # Item changed - stop any existing preview
                        self.monitor.stop_preview = True
                        self.monitor.stop_preview_playback()

                        # Start new preview timer
                        self.last_checked_item = current_label
                        self.monitor.stop_preview = False

                        # Start preview worker thread
                        preview_thread = threading.Thread(
                            target=self.monitor.preview_worker,
                            args=(current_path, current_label)
                        )
                        preview_thread.daemon = True
                        preview_thread.start()
            else:
                # Not on episodes view - stop preview if active
                if self.monitor.preview_active:
                    self.monitor.stop_preview = True
                    self.monitor.stop_preview_playback()
                self.last_checked_item = None

            # Sleep before next check
            if self.monitor.waitForAbort(0.2):
                break

        # Cleanup
        self.monitor.stop_preview_playback()
        self.log("Streamflix Helper service stopped", xbmc.LOGINFO)


if __name__ == '__main__':
    service = StreamflixService()
    service.run()
