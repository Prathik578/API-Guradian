import os
import re

files_to_fix = [
    "frontend/src/app/(app)/api-changes/page.tsx",
    "frontend/src/app/(app)/api-changes/[change_id]/page.tsx",
    "frontend/src/app/(app)/apis/[api_id]/page.tsx",
    "frontend/src/app/(app)/cases/page.tsx",
    "frontend/src/app/(app)/apis/page.tsx",
    "frontend/src/app/(app)/cases/[case_id]/page.tsx",
    "frontend/src/app/(app)/activity/page.tsx",
    "frontend/src/app/(app)/notices/page.tsx",
    "frontend/src/app/(app)/pull-requests/page.tsx",
    "frontend/src/app/(app)/notices/[notice_id]/page.tsx",
    "frontend/src/app/(app)/repositories/[repo_id]/page.tsx",
    "frontend/src/app/(app)/repositories/page.tsx",
    "frontend/src/app/(app)/settings/page.tsx"
]

# The regex matches the start of the return statement up to the start of the content-area's inner content.
# Because whitespace and inner text might vary slightly, we use re.DOTALL.
pattern_start = re.compile(r'(return\s*\(\s*)<div className="dashboard-layout">\s*<aside className="sidebar">.*?</aside>\s*<main className="main-content">\s*<header className="header">.*?</header>\s*<div className="content-area">', re.DOTALL)
pattern_end = re.compile(r'</div>\s*</main>\s*</div>\s*\);\s*}\s*$', re.DOTALL)

for f in files_to_fix:
    if not os.path.exists(f):
        continue
    with open(f, 'r') as file:
        content = file.read()
    
    if '<div className="dashboard-layout">' not in content:
        continue
        
    # Replace opening
    new_content = pattern_start.sub(r'\1<>', content)
    
    # Replace closing
    new_content = pattern_end.sub(r'</>\n  );\n}\n', new_content)
    
    with open(f, 'w') as file:
        file.write(new_content)
    print(f"Fixed {f}")
