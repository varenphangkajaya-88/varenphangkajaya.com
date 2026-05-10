#!/usr/bin/env python3
"""
Convert hardcoded journal sections in index.html to dynamic CMS-driven version.
"""

import re
import sys
from pathlib import Path

def convert_html(input_file='index.html', output_file='index.html'):
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    original_size = len(html)
    print(f"Original size: {original_size:,} bytes")
    
    # 1. Replace hardcoded journal list section
    journal_list_pattern = re.compile(
        r'(<!-- Journal list -->\s*<div class="page fade-in" id="page-journal">\s*<div class="project-page">\s*<h1 class="project-title">Journal</h1>\s*<div class="journal-grid">)'
        r'.*?'
        r'(</div>\s*</div>\s*</div>)',
        re.DOTALL
    )
    
    new_journal_list = (
        r'\1\n'
        r'      <!-- Articles loaded dynamically from /_journals/ via journal-loader.js -->\n'
        r'    \2'
    )
    
    if journal_list_pattern.search(html):
        html = journal_list_pattern.sub(new_journal_list, html)
        print("OK Replaced journal list with empty grid")
    else:
        print("WARN Could not find journal list section")
    
    # 2. Remove hardcoded journal-popup article page
    simpler_popup = re.compile(
        r'<!-- Journal: Pop-up lessons -->.*?(?=<!-- Journal: Restart -->)',
        re.DOTALL
    )
    if simpler_popup.search(html):
        html = simpler_popup.sub('', html)
        print("OK Removed hardcoded journal-popup article")
    else:
        print("WARN Could not find journal-popup section")
    
    # 3. Remove hardcoded journal-restart article page
    restart_pattern = re.compile(
        r'<!-- Journal: Restart -->.*?(?=<!-- Contact -->)',
        re.DOTALL
    )
    if restart_pattern.search(html):
        html = restart_pattern.sub('', html)
        print("OK Removed hardcoded journal-restart article")
    else:
        print("WARN Could not find journal-restart section")
    
    # 4. Update routing logic - projects array
    old_projects = "const projects = ['campaign','activation','shopify','crm','systems','webapp','factory','rehab','journal','journal-popup','journal-restart','contact'];"
    new_projects = "const projects = ['campaign','activation','shopify','crm','systems','webapp','factory','rehab','journal','contact'];"
    
    if old_projects in html:
        html = html.replace(old_projects, new_projects)
        print("OK Updated projects array")
    else:
        print("WARN Could not find projects array")
    
    # 5. Update handleHash to handle dynamic journal slugs
    old_handle_hash = '''window.handleHash = function() {
    const hash = location.hash.replace('#','');
    if (hash && projects.includes(hash)) {
      showPage(hash);
    } else {
      showPage('home');
    }
  }'''
    
    new_handle_hash = '''window.handleHash = function() {
    const hash = location.hash.replace('#','');
    if (hash && projects.includes(hash)) {
      showPage(hash);
    } else if (hash && hash.startsWith('journal-')) {
      showPage(hash);
    } else {
      showPage('home');
    }
  }'''
    
    if old_handle_hash in html:
        html = html.replace(old_handle_hash, new_handle_hash)
        print("OK Updated handleHash for dynamic journal slugs")
    else:
        print("WARN Could not find handleHash function")
    
    # 6. Add script tag for journal-loader.js before </body>
    if 'journal-loader.js' not in html:
        html = html.replace(
            '</body>',
            '<script src="/journal-loader.js"></script>\n</body>'
        )
        print("OK Added journal-loader.js script tag")
    else:
        print("INFO journal-loader.js already referenced")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    new_size = len(html)
    print(f"\nNew size: {new_size:,} bytes")
    print(f"Saved: {original_size - new_size:,} bytes")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    convert_html()
