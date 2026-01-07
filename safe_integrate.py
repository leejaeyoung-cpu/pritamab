#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Safe integration script for adding Cellpose page to ADDS
Uses minimal file modification to avoid encoding issues
"""

import sys
import io

print("=" * 60)
print("ADDS + Cellpose Integration Script")
print("=" * 60)

# Step 1: Read original file with UTF-8
print("\n[1/5] Reading AI_Anticancer_Drug_System.py...")
with io.open('AI_Anticancer_Drug_System.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Step 2: Check if already integrated
if 'from modules.cellpose_page import render_cellpose_page' in content:
    print("   ✓ Already integrated!")
    sys.exit(0)

# Step 3: Add UTF-8 declaration if missing
print("[2/5] Checking encoding declaration...")
if '# -*- coding: utf-8 -*-' not in content[:200]:
    lines = content.split('\n', 2)
    if lines[0].startswith('"""'):
        # After docstring
        lines.insert(1, '# -*- coding: utf-8 -*-')
    else:
        lines.insert(0, '# -*- coding: utf-8 -*-')
    content = '\n'.join(lines)
    print("   ✓ Added UTF-8 declaration")

# Step 4: Add menu item (safe string replacement)
print("[3/5] Adding menu item...")
old_menu = '["🏠 홈", "📊 데이터 현황", "👤 환자 정보 입력", "🔍 환자 조회", "📂 데이터 업로드", "🤖 AI 정밀 항암제 조합"]'
new_menu = '["🏠 홈", "📊 데이터 현황", "👤 환자 정보 입력", "🔍 환자 조회", "📂 데이터 업로드", "🤖 AI 정밀 항암제 조합", "🔬 세포 이미지 분석"]'

if old_menu in content:
    content = content.replace(old_menu, new_menu)
    print("   ✓ Menu updated")
else:
    print("   ⚠ Menu pattern not found, skipping")

# Step 5: Add integration code at the end
print("[4/5] Adding Cellpose page integration...")
integration_code = """

# ============ Cellpose Integration ============
try:
    from modules.cellpose_page import render_cellpose_page
    
    if page == "🔬 세포 이미지 분석":
        render_cellpose_page()
except Exception as e:
    if page == "🔬 세포 이미지 분석":
        st.error(f"Cellpose module error: {str(e)}")
        st.info("Please ensure the modules folder exists with cellpose_page.py")
"""

content += integration_code
print("   ✓ Integration code added")

# Step 6: Write with UTF-8
print("[5/5] Writing updated file...")
with io.open('AI_Anticancer_Drug_System.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("\n" + "=" * 60)
print("✅ Integration Complete!")
print("=" * 60)
print("\nFile size:", len(content), "characters")
print("\nNext steps:")
print("1. Stop current ADDS server (Ctrl+C)")
print("2. Run: streamlit run AI_Anticancer_Drug_System.py")
print("3. Check new menu item: 🔬 세포 이미지 분석")
print("=" * 60)
