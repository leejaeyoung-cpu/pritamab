#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# Read the file
with open('AI_Anticancer_Drug_System.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix the encoding issue
content = content.replace(
    "with open(patients_json, 'r', encoding='utf-8') as f:",
    "with open(patients_json, 'r', encoding='utf-8') as f:"
)

# Ensure proper encoding declaration
if '# -*- coding: utf-8 -*-' not in content[:100]:
    content = '#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n' + content

# Write back
with open('AI_Anticancer_Drug_System.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed encoding issues in AI_Anticancer_Drug_System.py")
