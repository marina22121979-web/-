"""Build the Russian index and check exact upstream Git blob hashes."""
from pathlib import Path
import json,re,hashlib,collections
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'sources.json').read_text())
repos={r['name']:r for r in data['repositories']}

def category(text):
    rules=[('davinci','DaVinci Resolve',r'davinci|resolve|fusion'),('premiere','Premiere Pro',r'premiere'),('capcut','CapCut / Jianying',r'capcut|jianying|剪映'),('final-cut','Final Cut Pro / FCPXML',r'fcpxml|final.cut|fcpx'),('after-effects','After Effects',r'after.effects|extendscript|code2ae|/ae-'),('ffmpeg','FFmpeg',r'ffmpeg|ffprobe'),('remotion','Remotion',r'remotion'),('color','Цветокоррекция',r'colo[u]?r.grad|colo[u]?rist|lut|retouch'),('subtitles','Субтитры и звук',r'subtitle|caption|transcrib|audio|speech|sound|voiceover|dubbing'),('motion','Анимация и VFX',r'motion|animat|vfx|hyperframes|gsap|threejs|manim')]
    for slug,label,pattern in rules:
        if re.search(pattern,text,re.I):return slug,label
    return 'editing','Монтаж и видеопроизводство'

def fields(text):
    fm=re.match(r'^---\s*\n(.*?)\n---',text,re.S)
    block=fm.group(1) if fm else ''
    name=re.search(r'^name:\s*(.+)',block,re.M)
    desc=re.search(r'^description:\s*(.*?)(?=\n\w[\w-]*:|\Z)',block,re.M|re.S)
    name=name.group(1).strip().strip('\"\'') if name else 'Без имени'
    desc=desc.group(1).strip() if desc else ''
    desc=re.sub(r'^[|>]\s*[-+]?\s*','',desc)
    desc=re.sub(r'\s+',' ',desc.strip('\"\''))
    return name,desc

def esc(s):return s.replace('|','\\|').replace('\n',' ')
rows=[];errors=[]
for f in data['snapshots']:
    p=root/f['path'];b=p.read_bytes();sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if sha!=f['sha']:errors.append(f['path'])
    if not f['path'].startswith('snapshots/'):continue
    name,desc=fields(b.decode('utf-8'))
    slug,label=category(f['repo']+' '+f['upstream_path']+' '+name)
    branch=repos[f['repo']]['branch']
    rows.append(dict(name=name,description=desc,category=label,slug=slug,local=f['path'],repository=f['repo'],upstream_path=f['upstream_path'],sha=f['sha'],source=f"https://github.com/{f['repo']}/blob/{branch}/{f['upstream_path']}",immutable_blob=f"https://api.github.com/repos/{f['repo']}/git/blobs/{f['sha']}"))
if errors:raise SystemExit('HASH MISMATCH: '+repr(errors))
rows.sort(key=lambda x:(x['category'],x['name'],x['repository']))
(root/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
catalogs=root/'catalogs';catalogs.mkdir(exist_ok=True)
groups=collections.defaultdict(list)
for r in rows:groups[r['slug']].append(r)
for slug,group in groups.items():
    lines=['# '+group[0]['category'],'',f'Файлов навыков: {len(group)}. Это снимки инструкций; работоспособность в приложениях не проверялась.','','| Навык | Назначение | Источник |','| --- | --- | --- |']
    for r in group:
        lines.append(f"| [{esc(r['name'])}](../{r['local']}) | {esc(r['description'][:260])} | [{r['repository']}]({r['source']}) |")
    (catalogs/(slug+'.md')).write_text('\n'.join(lines)+'\n')
links=['# Дополнительные источники без локальной копии','','Для этих файлов не найдена распознанная лицензия на распространение в проверенных файлах лицензий. Это не заключение об отсутствии лицензии. Содержимое не копировалось.','','| Репозиторий | Файл |','| --- | --- |']
for r in sorted(data['link_only'],key=lambda r:(r['repo'],r['path'])):links.append(f"| {r['repo']} | [{esc(r['path'])}]({r['url']}) |")
(root/'LINKS_ONLY.md').write_text('\n'.join(links)+'\n')
summary={'date':data['date'],'queries':len(data['queries']),'candidate_repositories':len(repos),'inspected_repositories':sum(r['inspected'] for r in repos.values()),'repositories_with_skill_files':sum(bool(r['skill_files']) for r in repos.values()),'saved_skill_files':len(rows),'unique_saved_contents':len({r['sha'] for r in rows}),'saved_source_repositories':len({r['repository'] for r in rows}),'license_files':sum(f['path'].startswith('licenses/') for f in data['snapshots']),'link_only_skill_files':len(data['link_only']),'categories':{v[0]['category']:len(v) for v in groups.values()},'hash_verification':'all snapshots match original upstream Git blob SHA-1'}
(root/'VERIFICATION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
readme=['# Навыки для видеомонтажа','','Подборка AI-навыков с GitHub для монтажа, цветокоррекции, субтитров, звука, анимации и экспорта видео. Дата поиска: **5 ноября 2026**.','',f"Сохранено **{len(rows)} файлов SKILL.md** из **{summary['saved_source_repositories']} репозиториев**. Дополнительно: **{len(data['link_only'])} ссылок** без копирования содержимого.",'','## Каталог','','| Программа / задача | Файлов |','| --- | --- |']
for slug,group in sorted(groups.items(),key=lambda x:x[1][0]['category']):readme.append(f"| [{group[0]['category']}](catalogs/{slug}.md) | {len(group)} |")
readme += ['','## Как пользоваться','','Откройте нужный раздел и выберите навык. В таблице есть сохранённая инструкция и ссылка на оригинальный проект. Для установки берите полный пакет из оригинального проекта с его scripts, references, assets и зависимостями. Здесь сохранены файлы инструкций и лицензии, а не все вспомогательные файлы проектов.','','Навыки не установлены и автоматически не активируются. Некоторые требуют локальную монтажную программу, MCP-сервер, API-ключ или платный сервис. Наличие инструкции не означает, что такое средство доступно в текущем чате. Тестов монтажа и рендера по этим навыкам не проводилось.','','## Что проверено','','- Наличие файлов SKILL.md в деревьях исходных репозиториев.','- Побайтовое совпадение сохранённых файлов с Git blob SHA-1 исходников.','- Повторы одного blob внутри репозитория сокращены; варианты между разными проектами сохранены с атрибуцией.','- Обычные навыки разработки и нерелевантные результаты поиска исключались. Это отбор, а не полная ручная проверка каждой инструкции.','','## Источники и лицензии','','- [sources.json](sources.json): запросы, найденные репозитории, ветки, SHA деревьев и файлов.','- [catalog.json](catalog.json): машиночитаемый каталог.','- [LINKS_ONLY.md](LINKS_ONLY.md): дополнительные навыки без копии.','- [licenses/](licenses/): исходные лицензии и уведомления.','- [VERIFICATION.json](VERIFICATION.json): результаты проверки и точные счётчики.','','Авторство и условия использования каждого навыка принадлежат его авторам. Общей лицензии, заменяющей условия исходников, у сборника нет. Наличие лицензии проекта не отменяет специальных условий отдельных файлов и сервисов.','','## Границы поиска','','Проверено 12 запросов GitHub, до 30 результатов каждого запроса, плюс официальный репозиторий remotion-dev/skills. Часть выдачи может измениться, а некоторые репозитории недоступны. Все возможные навыки GitHub перечислить и проверить невозможно; эта подборка не заявляет полноту. Категории назначены по названию проекта и навыка; возможны пересечения и неточности.','','Для повторной проверки файлов и сборки индекса:','','```sh','python tools/build_catalog.py','```','','Поиск и копирование выполнены без запуска сторонних скриптов и установки скачанных навыков.']
readme_text='\n'.join(readme)+'\n'
if (root/'selected/installed.json').exists():
    readme_text=readme_text.replace('## Каталог','## Выбранные и установленные пять\n\n[Открыть установленный набор](selected/README.md) — монтаж, коррекция красноты кожи, HDR iPhone, субтитры и экспорт. Полные рабочие пакеты лежат в `selected/`; остальные файлы ниже — библиотечные снимки.\n\n## Каталог',1)
    readme_text=readme_text.replace('Навыки не установлены и автоматически не активируются.','Навыки из общего каталога не установлены и автоматически не активируются. Пять выбранных пакетов отдельно установлены в текущую среду, см. `selected/README.md`.')
if (root/'digital-twin/installed.json').exists():
    readme_text=readme_text.replace('## Каталог','## Цифровой двойник\n\n[Пять навыков для вашего цифрового двойника](digital-twin/README.md): аватар, говорящие видео, озвучка, клонирование собственного голоса и последовательность внешности.\n\n## Каталог',1)
(root/'README.md').write_text(readme_text)
print(json.dumps(summary,ensure_ascii=False))
