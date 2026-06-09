from pathlib import Path
import re
root=Path('.')
css=Path('app/static/css/style.css').read_text(encoding='utf-8', errors='ignore')
selectors=[]
for block in re.findall(r'([^\{]+)\{', css):
    parts=[p.strip() for p in block.split(',')]
    for p in parts:
        if p.startswith('.'):
            cls=re.match(r'\.([A-Za-z0-9_-]+)', p)
            if cls: selectors.append(cls.group(1))
all_files=[p for p in root.rglob('*') if p.suffix in ['.html','.js','.py']]
text={str(p):p.read_text(encoding='utf-8', errors='ignore') for p in all_files}
unused=[]
for cls in sorted(set(selectors)):
    pat=re.compile(r'\b'+re.escape(cls)+r'\b')
    found=False
    for path,txt in text.items():
        if pat.search(txt):
            found=True
            break
    if not found:
        unused.append(cls)
print('css selectors', len(selectors), 'unique', len(set(selectors)), 'unused', len(unused))
for cls in unused:
    print(cls)
