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
