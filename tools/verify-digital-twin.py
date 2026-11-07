from pathlib import Path
import json,hashlib,re
import yaml
root=Path(__file__).resolve().parents[1];base=root/'digital-twin'
d=json.loads((base/'installed.json').read_text());errors=[];checks=[]
for f in d['files']:
 p=root/f['path'];b=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if actual!=f['sha']:errors.append('Hash mismatch: '+f['path'])
for pkg in d['packages']:
 path=root/pkg['directory'];s=(path/'SKILL.md').read_text()
 front=re.match(r'^---\s*\n(.*?)\n---',s,re.S)
 if not front:errors.append('Missing frontmatter '+pkg['name']);continue
 meta=yaml.safe_load(front.group(1));assert meta['name']==pkg['name']
 assert meta.get('description')
 for p in path.rglob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   target=target.split('#',1)[0].split(' ',1)[0]
   if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target):continue
   if target.startswith('/') or '<' in target or '>' in target:continue
   if not (p.parent/target).exists():errors.append(str(p.relative_to(root))+': missing '+target)
 checks.append({'skill':pkg['name'],'frontmatter_valid':True,'license_present':(path/'LICENSE').exists(),'file_count':sum(p.is_file() for p in path.rglob('*'))})
report={'downloaded_skill_count':len(d['packages']),'downloaded_source_files':len(d['files']),'byte_identity_checks':len(d['files']),'packages':checks,'errors':errors,'generation_test':'Not run. Download and local registration only; provider authentication and credits not configured by this task.'}
(base/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
if errors:raise SystemExit(1)
