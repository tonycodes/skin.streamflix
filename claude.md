# StreamFlix Kodi Skin - Development Notes

## Critical: Control IDs

### Rules
1. **Control IDs must be UNIQUE within each XML file** - Duplicate IDs cause infinite recursion and crashes
2. **Some IDs are reserved by Kodi** - Don't override system control IDs unless intentional
3. **DialogSelect.xml requires BOTH list ID 3 AND list ID 6** - ID 3 for simple lists, ID 6 for detailed lists
4. **FileBrowser.xml uses IDs 413/414** for OK/Cancel buttons (Kodi expects these)
5. **DialogMediaSource.xml uses IDs 10/11/12/18/19** for its controls

### Common ID Ranges
- 1-99: Reserved for window-specific controls (headings, labels)
- 50: Main content list/panel (standard convention)
- 60: Scrollbars
- 100-999: Custom controls
- 9000+: Navigation buttons (back, settings, etc.)

### Crashes from Duplicate IDs
If Kodi crashes with stack overflow in `CGUIControlGroupList::ValidateOffset()`, check for duplicate control IDs. This happens when:
- A grouplist and a control inside it have the same ID
- Multiple conditional controls share the same ID

## XML Validation Rules

### Invalid Patterns
```xml
<!-- WRONG: Can't use conditions in position tags -->
<posy>Container.Content(seasons) | Container.Content(episodes)</posy>

<!-- CORRECT: Use visibility conditions on the control group -->
<control type="group">
    <visible>Container.Content(seasons) | Container.Content(episodes)</visible>
    <posy>100</posy>
</control>
```

### Colors
- Always use 8-character hex format: `AARRGGBB` (e.g., `FFE50914`)
- Don't reference undefined color names
- Netflix palette: `FFE50914` (red), `FF141414` (black), `FFFFFFFF` (white)

## Required Workflow

### After Every XML Change
1. Run the linter: `python scripts/lint_skin.py`
2. Fix any errors before syncing
3. Sync to installed addon (macOS): `rsync -av xml/ ~/Library/Application\ Support/Kodi/addons/skin.streamflix/xml/`
4. Clear texture cache if needed: `rm -f ~/Library/Application\ Support/Kodi/userdata/Database/Textures*.db`
5. Restart Kodi to test changes

## File Purposes

| File | Purpose | Key IDs |
|------|---------|---------|
| DialogSelect.xml | Selection dialogs | 3 (simple list), 6 (detail list), 7 (close) |
| DialogConfirm.xml | Yes/No confirmations | 10 (cancel), 11 (ok) |
| DialogMediaSource.xml | Add video source | 10-12, 18-19 |
| FileBrowser.xml | Browse folders | 450 (list), 413 (ok), 414 (cancel) |
| DialogAddonSettings.xml | Addon/scraper settings | 3 (categories), 5 (settings), 7-15 (controls) |
| MyVideoNav.xml | Video library browsing | 50 (main panel), 9991 (back) |

## Debugging Tips

1. **Check Kodi log**: `~/.kodi/temp/kodi.log`
2. **Enable debug logging**: Settings > System > Logging
3. **Skin reload shortcut**: Ctrl+Shift+R (if enabled)
4. **Common crash causes**:
   - Duplicate control IDs
   - Missing required controls
   - Invalid XML syntax
   - Undefined includes/colors

## Texture Paths

### DON'T use special://skin/ for media textures
```xml
<!-- WRONG - causes crashes on some platforms -->
<texture>special://skin/backgrounds/default.jpg</texture>
<texture fallback="special://skin/default_poster.png">...</texture>

<!-- CORRECT - relative paths from media folder -->
<texture>backgrounds/default.jpg</texture>
<texture fallback="default_poster.png">...</texture>
```

### Required Textures
These must exist in `/media/` folder:
- `white.png`, `black.png` - Base textures for colordiffuse
- `button-fo.png`, `button-nofo.png` - Button focus/unfocus
- `dialog-bg.png` - Dialog backgrounds
- `gradient-bottom.png`, `gradient-top.png`, `gradient-left.png`
- `arrow-up.png`, `arrow-down.png` - Spin controls
- `edit-fo.png`, `edit-nofo.png` - Edit field textures
- `radio-on.png`, `radio-off.png` - Radio buttons
- `scrollbar.png`, `scrollbar-bg.png` - Scrollbars
- `slider-nib.png`, `slider-bg.png` - Sliders
- `spinner.png` - Loading spinner
- `default_poster.png`, `default_thumb.png` - Fallback images

## Kodi Version Compatibility

| Kodi Version | xbmc.gui Version |
|--------------|------------------|
| Kodi 20 (Nexus) | 5.17.0 |
| Kodi 21 (Omega) | 5.18.0 |

Update `addon.xml`:
```xml
<import addon="xbmc.gui" version="5.18.0"/>
```

## Release Workflow

1. Update version in `addon.xml`
2. Run linter: `python3 scripts/lint_skin.py`
3. Commit changes: `git add -A && git commit -m "message"`
4. Push: `git push origin main`
5. Create zip: `zip -r skin.streamflix.zip skin.streamflix -x "*.git*" -x "*scripts*"`
6. Create release: `gh release create vX.X.X --title "vX.X.X" skin.streamflix.zip`
7. Update `repository/addons.xml` with new version
8. Generate MD5: `md5 -q addons.xml > addons.xml.md5`
9. Push repository update

### Short URL
- **URL**: `is.gd/93dtrd`
- **Points to**: `https://github.com/tonycodes/skin.streamflix/releases/latest/download/skin.streamflix.zip`
- Always upload `skin.streamflix.zip` (consistent name) to releases for the short URL to work

## Android TV Notes

- Test on actual device - some crashes only happen on Android
- Missing textures cause immediate crashes (no graceful fallback)
- Use `python3 scripts/lint_skin.py` to catch issues before deploying
