import xbmc
import xbmcvfs
import xbmcaddon
import os

def install_keymap():
    """Install the StreamFlix keymap to userdata if not already present."""
    addon = xbmcaddon.Addon()
    addon_path = addon.getAddonInfo('path')

    # Source keymap in addon
    source = os.path.join(addon_path, 'resources', 'keymaps', 'keymap.xml')

    # Destination in userdata
    userdata = xbmcvfs.translatePath('special://userdata/')
    keymaps_dir = os.path.join(userdata, 'keymaps')
    dest = os.path.join(keymaps_dir, 'streamflix.xml')

    # Create keymaps directory if it doesn't exist
    if not xbmcvfs.exists(keymaps_dir):
        xbmcvfs.mkdirs(keymaps_dir)

    # Copy keymap if source exists and destination doesn't
    if xbmcvfs.exists(source) and not xbmcvfs.exists(dest):
        xbmcvfs.copy(source, dest)
        xbmc.log('StreamFlix: Installed keymap to userdata', xbmc.LOGINFO)
        # Reload keymaps
        xbmc.executebuiltin('Action(reloadkeymaps)')
    elif xbmcvfs.exists(source):
        xbmc.log('StreamFlix: Keymap already installed', xbmc.LOGDEBUG)

if __name__ == '__main__':
    install_keymap()
