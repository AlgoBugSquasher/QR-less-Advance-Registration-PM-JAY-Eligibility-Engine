from pathlib import Path
root=Path('app')
files=[p for p in root.rglob('*') if p.suffix in ['.html','.js']]
terms=['data-tooltip','loading','pulse','shake','d-none','d-block','d-flex','d-grid','gap-1','gap-2','gap-3','visible','invisible','position-relative','position-absolute','cursor-pointer','cursor-default','opacity-50','opacity-75','transition-fast','transition-slow','is-invalid','is-valid','invalid-feedback','sr-only','copyToClipboard','printToken','reloadPage','logout(','cancelToken(']
for term in terms:
    occurrences=[]
    for f in files:
        txt=f.read_text(encoding='utf-8', errors='ignore')
        if term in txt:
            occurrences.append(str(f))
    if occurrences:
        print(term, len(occurrences), '->', occurrences[:10])
