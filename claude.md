# StreamFlix Kodi Skin - Development Notes

## Critical: DRY Principle - Centralized Styling

### ALWAYS use Defaults.xml for styling
**NEVER define colors, fonts, or textures inline in individual XML files.** All styling must be centralized in `Defaults.xml`.

```xml
<!-- WRONG - inline styling -->
<control type="button">
    <textcolor>FFFFFFFF</textcolor>
    <texturefocus colordiffuse="FFFFFFFF">white.png</texturefocus>
</control>

<!-- CORRECT - inherits from Defaults.xml -->
<control type="button">
    <label>My Button</label>
</control>
```

### Defaults.xml Controls
All these control types have default styling defined:
- `button` - Buttons with white.png texture
- `label` - Text labels
- `fadelabel` - Scrolling labels
- `textbox` - Multi-line text
- `list`, `wraplist`, `fixedlist` - List controls
- `panel` - Panel containers
- `scrollbar` - Scrollbars
- `slider` - Slider controls
- `progress` - Progress bars
- `edit` - Text input fields
- `radiobutton` - Radio buttons
- `togglebutton` - Toggle buttons
- `spincontrol`, `spincontrolex` - Spin controls

## Color Palette - ALWAYS Use Hex Values

**NEVER use color names** - always use 8-character hex format `AARRGGBB`:

| Purpose | Hex Value | Usage |
|---------|-----------|-------|
| White text | `FFFFFFFF` | Primary text, focused buttons |
| Gray text | `FFB3B3B3` | Secondary text, descriptions |
| Dim text | `FF808080` | Tertiary text, hints |
| Dark text | `FF141414` | Text on white backgrounds |
| Red accent | `FFE50914` | Netflix red, primary buttons |
| Green accent | `FF46D369` | Success, update buttons |
| Dark background | `FF141414` | Main background |
| Card background | `FF1A1A1A` | Dialog backgrounds |
| Button unfocused | `FF404040` | Default button background |
| Overlay | `CC000000` | Semi-transparent overlays |
| Overlay dark | `DD000000` | Darker overlays |

### Button Styling Convention
```xml
<!-- Standard button colors -->
<texturefocus colordiffuse="FFFFFFFF">white.png</texturefocus>      <!-- White when focused -->
<texturenofocus colordiffuse="FF404040">white.png</texturenofocus>  <!-- Gray when unfocused -->
<textcolor>FFFFFFFF</textcolor>                                      <!-- White text unfocused -->
<focusedcolor>FF141414</focusedcolor>                               <!-- Dark text when focused -->
```

## Info Labels - Correct Syntax

Use the correct Kodi info labels:

```xml
<!-- WRONG -->
$INFO[ListItem.Property(Addon.Version)]
$INFO[ListItem.Property(Addon.Creator)]

<!-- CORRECT -->
$INFO[ListItem.AddonVersion]
$INFO[ListItem.AddonCreator]
$INFO[ListItem.AddonDescription]
$INFO[ListItem.AddonSummary]
$INFO[ListItem.Label]
$INFO[ListItem.Icon]
```

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

## Required Workflow

### After Every XML Change
1. Run the linter: `python scripts/lint_skin.py`
2. Fix any errors before syncing
3. Sync to installed addon (macOS):
   ```bash
   cd /Users/tony/Herd/skin.streamflix
   cp -r addon.xml icon.png fanart.jpg LICENSE.txt resources media fonts "$HOME/Library/Application Support/Kodi/addons/skin.streamflix/"
   ```
4. Clear texture cache if needed:
   ```bash
   rm -f "$HOME/Library/Application Support/Kodi/userdata/Database/Textures"*.db
   ```
5. Restart Kodi to test changes

## File Purposes

| File | Purpose | Key IDs |
|------|---------|---------|
| Defaults.xml | **Centralized control styling** | N/A |
| DialogSelect.xml | Selection dialogs | 3 (simple list), 6 (detail list), 7 (close) |
| DialogConfirm.xml | Yes/No confirmations | 10 (cancel), 11 (ok) |
| DialogAddonInfo.xml | Addon info page | 6 (install), 5 (update), 8 (disable), 7 (close) |
| DialogMediaSource.xml | Add video source | 10-12, 18-19 |
| FileBrowser.xml | Browse folders | 450 (list), 413 (ok), 414 (cancel) |
| DialogAddonSettings.xml | Addon/scraper settings | 3 (categories), 5 (settings), 7-15 (controls) |
| MyVideoNav.xml | Video library browsing | 50 (main panel), 9991 (back) |

## Debugging Tips

1. **Check Kodi log**: `~/.kodi/temp/kodi.log` or `/Users/tony/Library/Application Support/Kodi/temp/kodi.log`
2. **Enable debug logging**: Settings > System > Logging
3. **Skin reload shortcut**: Ctrl+Shift+R (if enabled)
4. **Common crash causes**:
   - Duplicate control IDs
   - Missing required controls
   - Invalid XML syntax
   - Undefined includes/colors
   - Using color names instead of hex values

## Texture Paths

### DON'T use special://skin/ for media textures
```xml
<!-- WRONG - causes crashes on some platforms -->
<texture>special://skin/backgrounds/default.jpg</texture>

<!-- CORRECT - relative paths from media folder -->
<texture>backgrounds/default.jpg</texture>
```

### Key Textures
- `white.png` - **Primary texture for colordiffuse buttons** (1x1 white pixel)
- `black.png` - Base texture for dark backgrounds
- `radio-on.png`, `radio-off.png` - Radio button states
- `arrow-up.png`, `arrow-down.png` - Spin controls
- `scrollbar.png`, `scrollbar-bg.png` - Scrollbars
- `spinner.png` - Loading spinner
- `default_poster.png`, `default_thumb.png` - Fallback images

## Kodi Version Compatibility

| Kodi Version | xbmc.gui Version |
|--------------|------------------|
| Kodi 20 (Nexus) | 5.17.0 |
| Kodi 21 (Omega) | 5.17.0 (use this for compatibility) |

## Release Workflow

1. Update version in `addon.xml`
2. Update version in `addons.xml` (root)
3. Regenerate MD5: `md5 -q addons.xml > addons.xml.md5`
4. Create skin zip with correct structure:
   ```bash
   rm -f skin.streamflix/skin.streamflix-*.zip
   mkdir -p temp_skin/skin.streamflix
   cp -r addon.xml icon.png fanart.jpg LICENSE.txt resources media fonts temp_skin/skin.streamflix/
   cd temp_skin && zip -r ../skin.streamflix/skin.streamflix-X.X.X.zip skin.streamflix
   cd .. && rm -rf temp_skin
   ```
5. Commit and push: `git add -A && git commit -m "message" && git push origin main`

### Repository Structure
```
root/
├── addons.xml              # Addon metadata (at root!)
├── addons.xml.md5          # MD5 checksum (at root!)
├── skin.streamflix/
│   └── skin.streamflix-X.X.X.zip  # Skin zip
└── repository.streamflix/
    └── addon.xml           # Repository addon
```

### Short URLs
- **Repository (auto-updates)**: `is.gd/wbolqo`
- **Direct skin install**: `is.gd/93dtrd`

## Android TV Notes

- Test on actual device - some crashes only happen on Android
- Missing textures cause immediate crashes (no graceful fallback)
- Use `python3 scripts/lint_skin.py` to catch issues before deploying
- Clear Kodi cache on device if updates don't appear
