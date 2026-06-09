import os, re
from pathlib import Path
root=Path('.')
js_files=list(root.glob('app/static/js/*.js'))
css_files=list(root.glob('app/static/css/*.css'))
py_files=list(root.glob('app/**/*.py'))
html_files=list(root.glob('app/templates/*.html'))
all_text={}
for f in js_files+css_files+py_files+html_files:
    all_text[str(f)] = f.read_text(encoding='utf-8', errors='ignore')
funcs={}
for f in js_files:
    txt=all_text[str(f)]
    for m in re.finditer(r'function\s+([A-Za-z0-9_]+)\s*\(', txt):
        funcs.setdefault(m.group(1), []).append((str(f), txt[:m.start()].count('\n')+1))
    for m in re.finditer(r'([A-Za-z0-9_]+)\s*=\s*function\s*\(', txt):
        funcs.setdefault(m.group(1), []).append((str(f), txt[:m.start()].count('\n')+1))
usage={}
for name,defs in funcs.items():
    usage[name] = []
    pat=re.compile(r'\b'+re.escape(name)+r'\b')
    for p,t in all_text.items():
        for m in pat.finditer(t):
            usage[name].append((p, t[:m.start()].count('\n')+1))
unused_js=[]
for name,defs in funcs.items():
    refs=[(p,l) for p,l in usage[name] if not any(p==d[0] and l==d[1] for d in defs)]
    if not refs:
        unused_js.append((name, defs))
classes={}
for f in css_files:
    txt=all_text[str(f)]
    for m in re.finditer(r'\.([A-Za-z0-9_-]+)', txt):
        classes.setdefault(m.group(1), []).append((str(f), txt[:m.start()].count('\n')+1))
unused_css=[]
for cls,defs in classes.items():
    pat=re.compile(r'(["\\\']|\\s)'+re.escape(cls)+r'(["\\\']|\\s)')
    found=False
    for p,t in all_text.items():
        if p.endswith('.css'): continue
        if pat.search(t): found=True; break
    if not found:
        unused_css.append((cls, defs))
py_funcs={}
py_imports=[]
for f in py_files:
    txt=all_text[str(f)]
    for m in re.finditer(r'^def\s+([A-Za-z0-9_]+)\s*\(', txt, re.M):
        py_funcs.setdefault(m.group(1), []).append((str(f), txt[:m.start()].count('\n')+1))
    for m in re.finditer(r'^(?:from\s+([A-Za-z0-9_.]+)\s+import\s+(.+)|import\s+([A-Za-z0-9_.]+))', txt, re.M):
        if m.group(1):
            im=m.group(1); names=[x.strip().split(' ')[0] for x in m.group(2).split(',')]
            for n in names:
                py_imports.append((str(f), im, n, txt[:m.start()].count('\n')+1))
        elif m.group(3):
            py_imports.append((str(f), m.group(3), None, txt[:m.start()].count('\n')+1))
unused_py_funcs=[]
for name,defs in py_funcs.items():
    pat=re.compile(r'\b'+re.escape(name)+r'\b')
    refs=[]
    for p,t in all_text.items():
        for m in pat.finditer(t):
            refs.append((p, t[:m.start()].count('\n')+1))
    refs2=[r for r in refs if not any(r[0]==d[0] and r[1]==d[1] for d in defs)]
    if not refs2:
        unused_py_funcs.append((name, defs))
unused_imports=[]
for f,module,name,line in py_imports:
    if name:
        pat=re.compile(r'\b'+re.escape(name)+r'\b')
    else:
        short=module.split('.')[-1]
        pat=re.compile(r'\b'+re.escape(short)+r'\b')
    refs=[]
    for p,t in all_text.items():
        for m in pat.finditer(t):
            refs.append((p, t[:m.start()].count('\n')+1))
    if len(refs) <= 1:
        unused_imports.append((f, module, name, line))
routes=[]
for f in py_files:
    txt=all_text[str(f)]
    for m in re.finditer(r'@([A-Za-z0-9_]+)\.route\(([^\)]*)\)', txt):
        routes.append((str(f), txt[:m.start()].count('\n')+1, m.group(1), m.group(2).strip()))
url_for_usage=[]
for f,t in all_text.items():
    for m in re.finditer(r'url_for\(\s*["\']([A-Za-z0-9_\.]+)["\']', t):
        url_for_usage.append((f, t[:m.start()].count('\n')+1, m.group(1)))
print('JS funcs', len(funcs), 'unused candidate', len(unused_js))
print('CSS classes', len(classes), 'unused candidate', len(unused_css))
print('PY funcs', len(py_funcs), 'unused candidate', len(unused_py_funcs))
print('PY imports', len(py_imports), 'unused candidate', len(unused_imports))
print('Routes', len(routes), 'url_for refs', len(url_for_usage))
print('UNUSED_JS_SAMPLE')
for name,defs in unused_js[:40]:
    print(name, defs)
print('UNUSED_CSS_SAMPLE')
for cls,defs in unused_css[:40]:
    print(cls, defs[:1])
print('UNUSED_PY_FUNCS_SAMPLE')
for name,defs in unused_py_funcs[:40]:
    print(name, defs)
print('UNUSED_IMPORTS_SAMPLE')
for f,module,name,line in unused_imports[:40]:
    print(f, module, name, line)
print('ROUTES_SAMPLE')
for item in routes[:40]:
    print(item)
print('URL_FOR_SAMPLE')
for item in url_for_usage[:40]:
    print(item)
