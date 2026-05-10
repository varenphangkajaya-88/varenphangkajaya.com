#!/usr/bin/env python3
"""
Rename hash-named images to clean, descriptive names.
Updates index.html references too.

Usage:
    python3 rename_images.py

Mappings:
    image-9-*.jpg  -> campaign-1.jpg
    image-10-*.jpg -> campaign-2.jpg
    ...
    image-16-*.jpg -> campaign-8.jpg
    image-17-*.jpg -> laundry-1.jpg
"""

import os
import re
import glob
from pathlib import Path

# Mapping: old image number -> new clean name
RENAME_MAP = {
    9: 'campaign-1.jpg',
    10: 'campaign-2.jpg',
    11: 'campaign-3.jpg',
    12: 'campaign-4.jpg',
    13: 'campaign-5.jpg',
    14: 'campaign-6.jpg',
    15: 'campaign-7.jpg',
    16: 'campaign-8.jpg',
    17: 'laundry-1.jpg',
}

def rename_images(images_dir='images', html_file='index.html'):
    print(f"Scanning {images_dir}/ for hash-named images...")
    
    images_path = Path(images_dir)
    if not images_path.exists():
        print(f"ERROR: {images_dir}/ folder not found")
        return
    
    # Read HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    renamed = []
    
    # Pattern to match: image-N-HASH.ext (where N is the number we care about)
    pattern = re.compile(r'^image-(\d+)-[a-f0-9]+\.(\w+)$', re.IGNORECASE)
    
    for img_file in sorted(images_path.iterdir()):
        if not img_file.is_file():
            continue
        
        match = pattern.match(img_file.name)
        if not match:
            continue
        
        img_num = int(match.group(1))
        ext = match.group(2).lower()
        
        if img_num not in RENAME_MAP:
            print(f"  SKIP: {img_file.name} (no mapping for image-{img_num})")
            continue
        
        new_name = RENAME_MAP[img_num]
        # Make sure extension matches
        new_ext = new_name.split('.')[-1].lower()
        if ext != new_ext:
            # Force the extension to match what's actually on disk
            new_name = new_name.rsplit('.', 1)[0] + '.' + ext
        
        new_path = images_path / new_name
        
        if new_path.exists():
            print(f"  WARN: {new_name} already exists, skipping {img_file.name}")
            continue
        
        # Rename the file
        old_name = img_file.name
        img_file.rename(new_path)
        renamed.append((old_name, new_name))
        print(f"  RENAMED: {old_name} -> {new_name}")
        
        # Update HTML references
        old_ref = f'/{images_dir}/{old_name}'
        new_ref = f'/{images_dir}/{new_name}'
        if old_ref in html:
            html = html.replace(old_ref, new_ref)
            print(f"    -> Updated HTML references")
    
    if not renamed:
        print("\nNo files renamed. Either no hash-named images found, or all already clean.")
        return
    
    # Write updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"{'='*60}")
    print(f"Renamed: {len(renamed)} files")
    print(f"HTML updated: {html_file}")
    print(f"\nFinal images/ folder:")
    for img in sorted(images_path.iterdir()):
        if img.is_file():
            size_kb = img.stat().st_size / 1024
            print(f"  {img.name} ({size_kb:.1f} KB)")

if __name__ == '__main__':
    rename_images()
