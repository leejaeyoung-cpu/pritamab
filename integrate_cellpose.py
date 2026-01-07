#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to safely integrate Cellpose page into ADDS
"""

import sys
import io

# Read original file
print("Reading AI_Anticancer_Drug_System.py...")
with io.open('AI_Anticancer_Drug_System.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Read addon content
print("Reading cellpose_page_addon.py...")
with io.open('cellpose_page_addon.py', 'r', encoding='utf-8') as f:
    addon_content = f.read()

# Add UTF-8 declaration if not present
if '# -*- coding: utf-8 -*-' not in original_content[:200]:
    lines = original_content.split('\n')
    if lines[0].startswith('#!'):
        lines.insert(1, '# -*- coding: utf-8 -*-')
    else:
        lines.insert(0, '#!/usr/bin/env python')
        lines.insert(1, '# -*- coding: utf-8 -*-')
    original_content = '\n'.join(lines)

# Update page menu
print("Updating navigation menu...")
old_menu = '["🏠 홈", "📊 데이터 현황", "👤 환자 정보 입력", "🔍 환자 조회", "📂 데이터 업로드", "🤖 AI 정밀 항암제 조합"]'
new_menu = '["🏠 홈", "📊 데이터 현황", "👤 환자 정보 입력", "🔍 환자 조회", "📂 데이터 업로드", "🤖 AI 정밀 항암제 조합", "🔬 세포 이미지 분석"]'
original_content = original_content.replace(old_menu, new_menu)

# Append addon at the end
print("Appending Cellpose page...")
final_content = original_content + '\n\n' + addon_content

# Write back with UTF-8
print("Writing updated file...")
with io.open('AI_Anticancer_Drug_System.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(final_content)

print("✅ Successfully integrated Cellpose page!")
print("File size:", len(final_content), "characters")
