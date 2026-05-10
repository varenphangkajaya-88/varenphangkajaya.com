#!/usr/bin/env python3
"""
Extract base64 images from index.html and save as separate files.
"""

import re
import base64
import os
import hashlib
from pathlib import Path

def slugify(text, max_length=50):
    if not text:
        return None
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text[:max_length] if text else None

def extract_alt_text(html_segment):
    alt_match = re.search(r'alt=["\']([^"\']+)["\']', html_segment)
    if alt_match:
        return alt_match.group(1)
    return None

def extract_images(html_file='index.html', output_html='index-clean.html', images_dir='images'):
    print(f"Reading {html_file}...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    original_size = len(html)
    print(f"Original size: {original_size:,} bytes ({original_size / 1024 / 1024:.2f} MB)")

    Path(images_dir).mkdir(exist_ok=True)

    img_pattern = re.compile(
        r'<img\s+([^>]*?)src=["\'](data:image/(\w+);base64,([^"\']+))["\']([^>]*?)>',
        re.IGNORECASE | re.DOTALL
    )

    bg_pattern = re.compile(
        r'url\(["\']?(data:image/(\w+);base64,([^"\')]+))["\']?\)',
        re.IGNORECASE
    )

    extracted = []
    counter = {'img': 0, 'bg': 0}
    used_names = set()

    def get_unique_name(base_name, ext):
        name = f"{base_name}.{ext}"
        if name not in used_names:
            used_names.add(name)
            return name
        i = 2
        while f"{base_name}-{i}.{ext}" in used_names:
            i += 1
        name = f"{base_name}-{i}.{ext}"
        used_names.add(name)
        return name

    def replace_img(match):
        before_attrs = match.group(1)
        ext = match.group(3).lower()
        b64_data = match.group(4)
        after_attrs = match.group(5)

        if ext == 'jpeg':
            ext = 'jpg'

        counter['img'] += 1

        full_tag = match.group(0)
        alt_text = extract_alt_text(full_tag)
        slug = slugify(alt_text) if alt_text else None

        if slug:
            base_name = slug
        else:
            hash_short = hashlib.md5(b64_data[:200].encode()).hexdigest()[:8]
            base_name = f"image-{counter['img']}-{hash_short}"

        filename = get_unique_name(base_name, ext)
        filepath = os.path.join(images_dir, filename)

        try:
            img_data = base64.b64decode(b64_data)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            extracted.append((filename, len(img_data)))
            print(f"  OK {filename} ({len(img_data):,} bytes) -- alt: {alt_text or '(none)'}")
        except Exception as e:
            print(f"  FAIL Failed to decode image {counter['img']}: {e}")
            return match.group(0)

        new_src = f'/{images_dir}/{filename}'
        return f'<img {before_attrs}src="{new_src}"{after_attrs}>'

    def replace_bg(match):
        ext = match.group(2).lower()
        b64_data = match.group(3)

        if ext == 'jpeg':
            ext = 'jpg'

        counter['bg'] += 1
        hash_short = hashlib.md5(b64_data[:200].encode()).hexdigest()[:8]
        base_name = f"bg-{counter['bg']}-{hash_short}"
        filename = get_unique_name(base_name, ext)
        filepath = os.path.join(images_dir, filename)

        try:
            img_data = base64.b64decode(b64_data)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            extracted.append((filename, len(img_data)))
            print(f"  OK {filename} ({len(img_data):,} bytes) -- CSS background")
        except Exception as e:
            print(f"  FAIL Failed to decode bg {counter['bg']}: {e}")
            return match.group(0)

        return f'url("/{images_dir}/{filename}")'

    print("\nExtracting <img> base64 images...")
    html = img_pattern.sub(replace_img, html)

    print("\nExtracting CSS background base64 images...")
    html = bg_pattern.sub(replace_bg, html)

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    new_size = len(html)
    total_img_size = sum(size for _, size in extracted)

    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"{'='*60}")
    print(f"Images extracted:    {len(extracted)}")
    print(f"  - <img> tags:      {counter['img']}")
    print(f"  - CSS backgrounds: {counter['bg']}")
    print(f"Total image size:    {total_img_size:,} bytes ({total_img_size / 1024 / 1024:.2f} MB)")
    print(f"\nHTML size:")
    print(f"  Before: {original_size:,} bytes ({original_size / 1024 / 1024:.2f} MB)")
    print(f"  After:  {new_size:,} bytes ({new_size / 1024:.2f} KB)")
    print(f"  Saved:  {original_size - new_size:,} bytes ({(1 - new_size/original_size) * 100:.1f}% reduction)")

if __name__ == '__main__':
    extract_images()
