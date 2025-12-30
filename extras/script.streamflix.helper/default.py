"""
Streamflix Helper - Manual trigger script
Can be called to manually start/stop preview
"""

import xbmc
import xbmcgui
import sys

def main():
    """Handle manual script calls."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if 'stop' in args:
        # Stop preview
        xbmcgui.Window(10000).clearProperty('StreamflixPreviewActive')
        if xbmc.getCondVisibility('Player.Playing'):
            xbmc.executebuiltin('PlayerControl(Stop)')
    elif 'toggle' in args:
        # Toggle preview
        if xbmcgui.Window(10000).getProperty('StreamflixPreviewActive'):
            xbmcgui.Window(10000).clearProperty('StreamflixPreviewActive')
            if xbmc.getCondVisibility('Player.Playing'):
                xbmc.executebuiltin('PlayerControl(Stop)')
        else:
            # Get current item and play
            path = xbmc.getInfoLabel('Container(50).ListItem.FileNameAndPath')
            if path:
                xbmcgui.Window(10000).setProperty('StreamflixPreviewActive', 'true')
                xbmc.executebuiltin(f'PlayMedia("{path}",1)')

if __name__ == '__main__':
    main()
