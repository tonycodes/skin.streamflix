#!/usr/bin/env python3
"""
Kodi Skin XML Linter for StreamFlix
Checks for common issues that cause crashes or display problems.
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

# Netflix color palette (valid colors)
VALID_COLORS = {
    'FFE50914',  # Netflix red
    'FF141414',  # Netflix black
    'FF1a1a1a',  # Dark gray
    'FF181818',  # Darker gray
    'FF333333',  # Medium gray
    'FFFFFFFF',  # White
    'CCFFFFFF',  # Semi-transparent white
    'AAFFFFFF',  # More transparent white
    '80FFFFFF',  # 50% white
    '60FFFFFF',  # 37% white
    '40FFFFFF',  # 25% white
    '20FFFFFF',  # 12% white
    'FF000000',  # Black
    'DD000000',  # Semi-transparent black
    'E0141414',  # Semi-transparent dark
    '80000000',  # 50% black
    '00000000',  # Fully transparent
}

# Known Kodi reserved IDs per dialog type
RESERVED_IDS = {
    'DialogSelect': {3, 6, 7, 60},  # list, detail list, close, scrollbar
    'FileBrowser': {413, 414, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461},
    'DialogConfirm': {1, 2, 3, 10, 11, 12},  # heading, lines, buttons
    'DialogMediaSource': {10, 11, 12, 18, 19},
}

class LintError:
    def __init__(self, file, line, message, severity='error'):
        self.file = file
        self.line = line
        self.message = message
        self.severity = severity

    def __str__(self):
        icon = '❌' if self.severity == 'error' else '⚠️'
        return f"{icon} {self.file}:{self.line}: {self.message}"

def find_xml_files(directory):
    """Find all XML files in directory."""
    xml_dir = Path(directory)
    return list(xml_dir.glob('**/*.xml'))

def get_line_number(content, pos):
    """Get line number from character position."""
    return content[:pos].count('\n') + 1

def check_duplicate_ids(file_path, content):
    """Check for duplicate control IDs in a single file."""
    errors = []

    # Find all id attributes
    id_pattern = re.compile(r'<control[^>]*\s+id=["\'](\d+)["\']|<control[^>]*>\s*<[^>]*id>(\d+)</|id="(\d+)"')

    # More robust: parse as XML and find all id attributes
    try:
        root = ET.fromstring(content)
        ids_found = defaultdict(list)

        def find_ids(element, path=''):
            # Check for id attribute
            if 'id' in element.attrib:
                id_val = element.attrib['id']
                ids_found[id_val].append(path or element.tag)

            # Check for <id> child element (older Kodi style)
            id_child = element.find('id')
            if id_child is not None and id_child.text:
                ids_found[id_child.text].append(path or element.tag)

            for child in element:
                find_ids(child, f"{path}/{element.tag}" if path else element.tag)

        find_ids(root)

        for id_val, locations in ids_found.items():
            # Skip parameterized IDs (used in includes)
            if '$PARAM' in id_val or '$VAR' in id_val:
                continue
            if len(locations) > 1:
                errors.append(LintError(
                    file_path.name,
                    0,  # Can't easily get line number from ET
                    f"Duplicate control ID '{id_val}' found {len(locations)} times: {', '.join(locations)}"
                ))

    except ET.ParseError as e:
        errors.append(LintError(file_path.name, e.position[0] if e.position else 0, f"XML parse error: {e}"))

    return errors

def check_invalid_position_conditions(file_path, content):
    """Check for conditional expressions in position tags (invalid)."""
    errors = []

    position_tags = ['posx', 'posy', 'width', 'height']

    for tag in position_tags:
        pattern = re.compile(rf'<{tag}>[^<]*(?:Container\.|Window\.|String\.|Integer\.)[^<]*</{tag}>', re.MULTILINE)
        for match in pattern.finditer(content):
            line = get_line_number(content, match.start())
            errors.append(LintError(
                file_path.name,
                line,
                f"Invalid conditional expression in <{tag}>. Conditions belong in <visible> tags."
            ))

    return errors

def check_undefined_colors(file_path, content):
    """Check for potentially undefined color references."""
    errors = []
    warnings = []

    # Find colordiffuse attributes with hex values
    color_pattern = re.compile(r'colordiffuse="([A-Fa-f0-9]{8})"')

    for match in color_pattern.finditer(content):
        color = match.group(1).upper()
        if color not in VALID_COLORS:
            line = get_line_number(content, match.start())
            warnings.append(LintError(
                file_path.name,
                line,
                f"Color '{color}' not in standard palette (may be intentional)",
                severity='warning'
            ))

    return errors + warnings

def check_xml_wellformed(file_path, content):
    """Check if XML is well-formed."""
    errors = []

    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        line = e.position[0] if e.position else 0
        errors.append(LintError(file_path.name, line, f"Malformed XML: {e}"))

    return errors

def check_empty_tags(file_path, content):
    """Check for empty required tags."""
    errors = []

    required_tags = ['texture', 'label', 'onclick', 'font']

    for tag in required_tags:
        pattern = re.compile(rf'<{tag}>\s*</{tag}>')
        for match in pattern.finditer(content):
            line = get_line_number(content, match.start())
            errors.append(LintError(
                file_path.name,
                line,
                f"Empty <{tag}> tag found",
                severity='warning'
            ))

    return errors

def check_missing_defaultcontrol(file_path, content):
    """Check that windows have a defaultcontrol."""
    errors = []

    if '<window' in content:
        if '<defaultcontrol' not in content:
            errors.append(LintError(
                file_path.name,
                1,
                "Window missing <defaultcontrol> - navigation may not work",
                severity='warning'
            ))

    return errors

def lint_file(file_path):
    """Run all lint checks on a file."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [LintError(file_path.name, 0, f"Could not read file: {e}")]

    # Run all checks
    errors.extend(check_xml_wellformed(file_path, content))

    # Only continue if XML is well-formed
    if not any(e.message.startswith('Malformed XML') for e in errors):
        errors.extend(check_duplicate_ids(file_path, content))
        errors.extend(check_invalid_position_conditions(file_path, content))
        errors.extend(check_undefined_colors(file_path, content))
        errors.extend(check_empty_tags(file_path, content))
        errors.extend(check_missing_defaultcontrol(file_path, content))

    return errors

def main():
    """Main entry point."""
    # Find skin directory
    script_dir = Path(__file__).parent
    skin_dir = script_dir.parent
    xml_dir = skin_dir / 'xml'

    if not xml_dir.exists():
        # Try resources path
        xml_dir = skin_dir / 'resources' / 'skins' / 'Default' / '1080p'

    if not xml_dir.exists():
        print(f"❌ Could not find XML directory")
        sys.exit(1)

    print(f"🔍 Linting XML files in: {xml_dir}")
    print("=" * 60)

    xml_files = find_xml_files(xml_dir)

    if not xml_files:
        print("No XML files found!")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for xml_file in sorted(xml_files):
        errors = lint_file(xml_file)

        if errors:
            print(f"\n📄 {xml_file.name}")
            for error in errors:
                print(f"   {error}")
                if error.severity == 'error':
                    total_errors += 1
                else:
                    total_warnings += 1

    print("\n" + "=" * 60)

    if total_errors == 0 and total_warnings == 0:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print(f"Found {total_errors} error(s) and {total_warnings} warning(s)")
        if total_errors > 0:
            print("❌ Fix errors before deploying!")
            sys.exit(1)
        else:
            print("⚠️  Warnings can be ignored if intentional")
            sys.exit(0)

if __name__ == '__main__':
    main()
