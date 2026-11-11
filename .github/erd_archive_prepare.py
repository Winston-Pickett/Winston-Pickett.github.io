import base64, hashlib, html, json, os, re, time, urllib.error, urllib.request
from pathlib import Path

REPO='Winston-Pickett/Winston-Pickett.github.io'
API='https://api.github.com/repos/'+REPO
BASE='534c6586132930f1fc1ef01c30ef6e843fc760c6'
SITE='https://winston-pickett.github.io'
ROOT='european-readiness/'
IMAGE=ROOT+'assets/europe-readiness-daily-landscape.jpg'
HEADERS={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'ERD-Archive-Restoration'}
OUT=Path('preview');OUT.mkdir(exist_ok=True)

def api(path, method='GET', payload=None):
    h=dict(HEADERS)
    if payload is not None: h['Content-Type']='application/json'
    req=urllib.request.Request(API+path,method=method,headers=h,data=None if payload is None else json.dumps(payload).encode())
    with urllib.request.urlopen(req,timeout=60) as r: return None if r.status==204 else json.load(r)

def getfile(path):
    obj=api('/contents/'+path+'?ref='+BASE)
    return base64.b64decode(obj['content']).decode('utf-8')

def blob_bytes(sha):
    obj=api('/git/blobs/'+sha)
    data=base64.b64decode(obj['content'])
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha
    return data

def putblob(data):
    if isinstance(data,str): data=data.encode('utf-8')
    expected=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    result=api('/git/blobs','POST',{'content':base64.b64encode(data).decode(),'encoding':'base64'})
    assert result['sha']==expected
    return expected

def sub1(pattern,replacement,text):
    result,count=re.subn(pattern,lambda m: replacement(m) if callable(replacement) else replacement,text,count=1,flags=re.S)
    assert count==1,pattern
    return result

def social(text):
    text=text.replace('/european-readiness/assets/europe-readiness-daily-300.png','/'+IMAGE)
    text=text.replace('property="og:image:width" content="300"','property="og:image:width" content="1280"').replace('property="og:image:height" content="300"','property="og:image:height" content="720"')
    if 'name="twitter:card"' not in text:
        text=text.replace('</head>','  <meta name="twitter:card" content="summary_large_image">\n  <meta name="twitter:image" content="'+SITE+'/'+IMAGE+'">\n</head>')
    return text

editions=[
 {'date':'2026-11-09','date_long':'November 9, 2026','weekday':'Monday','pages':79,'bytes':1253825,'sha256':'a9313ebfec3ce48f0c33da63dcd6291b05e7bc73a157d4b3da0f23beece1b25e','blob':'3afef0ce394a6656dddabbe2b0afd8f60d59361e','research_cutoff':'2026-11-09 14:37 EST','clock':'2:37 p.m. EST','window':'November 7, 2026, 8:15 a.m. EST through November 9, 2026, 2:37 p.m. EST','register':'September 9, 2026, 12:00 a.m. EDT through November 9, 2026, 2:37 p.m. EST','summary':'The original November 9 issue covers EU military-training support, attributed cyber activity, allied exercises, energy and transport exposures, and diplomatic assessments. It includes ten primary sections, a separate Russian military force-posture assessment, nine dashboard indicators, 304 dated or verified-overlap register records, and 22 separate date-limited disclosures. These totals are not counts of attacks.'},
 {'date':'2026-11-10','date_long':'November 10, 2026','weekday':'Tuesday','pages':76,'bytes':1197274,'sha256':'c91c943ff3256c76a4f9245f213f313a41ce400cc573c2ecc0ad4c1aaa61d979','blob':'e499f1fbbe25db32aa7fa316df150a789f3aa5bc','research_cutoff':'2026-11-10 09:20 EST','clock':'9:20 a.m. EST','window':'November 9, 2026, 2:37 p.m. EST through November 10, 2026, 9:20 a.m. EST','register':'September 10, 2026, 12:00 a.m. EDT through November 10, 2026, 9:20 a.m. EST','summary':'The original November 10 issue covers reported Ukrainian electricity disruption, Lithuanian grid-resilience planning, Black Sea maritime-security funding, diplomatic consultations and Russian military posture. It includes ten primary sections, nine standing indicators, 310 dated or verified-overlap register records, and 22 separate date-limited disclosures. Announcements, allegations and implemented actions remain separately classified.'}
]
assert api('/git/ref/heads/main')['object']['sha']==BASE,'Main changed; reconcile first.'
landing=getfile(ROOT+'index.html')
manifest=json.loads(getfile(ROOT+'editions.json'))
css=getfile(ROOT+'assets/readiness.css')
template=getfile(ROOT+'2026-11-11/index.html')
old_manifest=json.loads(json.dumps(manifest))
old_latest=re.search(r'<article class="er-latest-card">.*?</article>',landing,re.S).group()
old_summary=re.search(r'<section class="er-shell er-edition-intro">.*?</h2></div><div><p>(.*?)</p>',template,re.S).group(1)
old_rows=re.search(r'<table class="er-archive">.*?<tbody>(.*?)</tbody>',landing,re.S).group(1)
rows=re.findall(r'<tr>.*?</tr>',old_rows,re.S)
rows_by_date={re.search(r'<time datetime="([0-9-]+)"',row).group(1):row for row in rows}
assert len(rows_by_date)==len(rows)
assert manifest['editions'][0]['date']=='2026-11-11'
for edition in editions:
    assert edition['date'] not in rows_by_date
    assert not any(e['date']==edition['date'] for e in manifest['editions'])

files={}
for label,sha,expected_hash,size in [('graphic','a3eaf3448a7ed9006bfa1188b813a0febdc45d82','5e8e43cafe5a4f09df525bb7951694f2f568b657aebaab332b7004774a945b80',307152)]+[(e['date'],e['blob'],e['sha256'],e['bytes']) for e in editions]:
    data=blob_bytes(sha)
    assert len(data)==size and hashlib.sha256(data).hexdigest()==expected_hash
    path=IMAGE if label=='graphic' else ROOT+'editions/Europe_Readiness_Daily_'+label+'.pdf'
    files[path]=(data,sha)

archive_note='This historical copy was supplied by the publisher and restored to the archive on November 11, 2026. The PDF is preserved byte-for-byte with its original issue date, research cutoff, contents and source-access disclosures. It was originally circulated as a review edition; restoration is not a new final-release certification or a fresh verification of every historical claim and source link. Consult the latest edition for subsequent updates and corrections.'
for e in editions:
    date=e['date']; kb=round(e['bytes']/1024); pdffile='Europe_Readiness_Daily_'+date+'.pdf'
    page=template.replace('2026-11-11',date).replace('Wednesday, November 11, 2026',e['weekday']+', '+e['date_long']).replace('November 11, 2026',e['date_long'])
    page=page.replace('78 pages · PDF · 1236 KB',str(e['pages'])+' pages · PDF · '+str(kb)+' KB').replace('8:54 a.m. EST',e['clock'])
    page=page.replace(old_summary,html.escape(e['summary']))
    details='<dl>'+''.join('<div><dt>'+k+'</dt><dd>'+html.escape(v)+'</dd></div>' for k,v in [('Issue date',e['date_long']),('Research cutoff',e['date_long']+', '+e['clock']+' (America/Detroit)'),('Daily coverage window',e['window']),('Rolling register window',e['register']),('File',str(e['pages'])+' pages · '+format(e['bytes'],',')+' bytes · Original archived PDF'),('Archive restoration','November 11, 2026; original review status and research cutoff retained')])+'</dl>'
    page=sub1(r'<dl>.*?</dl>',details,page)
    page=page.replace('3183411b02a386574b1e193b6100a1516eb387b7f82d19e74f3186a749caa2a4',e['sha256'])
    page=sub1(r'<p class="er-archive-warning"><strong>Edition note:</strong>.*?</p>','<p class="er-archive-warning"><strong>Archive note:</strong> '+archive_note+'</p>',page)
    page=page.replace('<p class="er-viewer-help">','<p class="er-archive-warning"><strong>Historical review copy.</strong> Original content is preserved, not newly certified as a current final briefing.</p><p class="er-viewer-help">',1)
    page=social(page)
    assert date in page and e['sha256'] in page and e['window'] in page
    assert 'Final PDF' not in page and 'Same-cutoff finalization' not in page
    path=ROOT+date+'/index.html';files[path]=(page.encode(),None)
    manifest['editions'].append({'date':date,'title':'Europe Readiness Daily','page':'/'+ROOT+date+'/','pdf':'/'+ROOT+'editions/'+pdffile,'pages':e['pages'],'bytes':e['bytes'],'status':'archived_review_copy','sha256':e['sha256'],'research_cutoff':e['research_cutoff'],'archive_restored':'2026-11-11'})
    rows_by_date[date]='<tr><th scope="row"><time datetime="'+date+'">'+e['date_long']+'</time></th><td><a href="/'+ROOT+date+'/">Europe Readiness Daily <span aria-hidden="true">→</span></a><span class="er-table-note">Historical review copy · Original date and cutoff retained</span></td><td><a href="/'+ROOT+'editions/'+pdffile+'" download="'+pdffile+'">PDF ↓<span class="er-sr-only">, '+e['date_long']+'</span></a><span class="er-table-note">'+str(e['pages'])+' pages · '+str(kb)+' KB</span></td></tr>'

manifest['editions'].sort(key=lambda x:x['date'],reverse=True)
assert manifest['editions'][0]==old_manifest['editions'][0]
assert [e for e in manifest['editions'] if e['date'] not in [x['date'] for x in editions]]==old_manifest['editions']
landing=sub1(r'(<table class="er-archive">.*?<tbody>).*?(</tbody>)',lambda m:m.group(1)+''.join(rows_by_date[d] for d in sorted(rows_by_date,reverse=True))+m.group(2),landing)
assert re.search(r'<article class="er-latest-card">.*?</article>',landing,re.S).group()==old_latest
landing=social(landing)
landing=landing.replace('<div class="er-hero-inner">','<div class="er-hero-inner er-hero-inner-landscape">',1)
landing=landing.replace('<figure class="er-brand">','<figure class="er-brand er-brand-landscape">',1)
landing=landing.replace('width="300" height="300" alt="Europe Readiness Daily,','width="1280" height="720" fetchpriority="high" alt="Europe Readiness Daily,',1)
# A scoped override preserves the full 16:9 artwork rather than cropping into the old square.
css+='\n/* Publisher-supplied landscape newsletter artwork, November 11, 2026. */\n.er-hero-inner.er-hero-inner-landscape{grid-template-columns:minmax(0,1fr);gap:36px;padding-top:36px}\n.er-hero-inner-landscape>.er-brand-landscape{grid-row:1;justify-self:stretch;width:100%;display:block}\n.er-brand.er-brand-landscape img{width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;max-width:100%}\n.er-brand.er-brand-landscape figcaption{max-width:none;margin-top:14px}\n@media(max-width:800px){.er-hero-inner.er-hero-inner-landscape{padding-top:24px;gap:24px}.er-brand.er-brand-landscape{display:block;width:100%}.er-brand.er-brand-landscape img{width:100%;height:auto}.er-brand.er-brand-landscape figcaption{font-size:11px;margin-top:12px}}\n@media print{.er-hero-inner-landscape>.er-brand-landscape{display:none}}\n'
files[ROOT+'index.html']=(landing.encode(),None)
files[ROOT+'editions.json']=((json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode(),None)
files[ROOT+'assets/readiness.css']=(css.encode(),None)
files[ROOT+'2026-11-11/index.html']=(social(template).encode(),None)
assert len(files)==9
assert '2026-11-11' in old_latest
for oldrow in rows: assert oldrow in landing
assert '<meta property="og:image:width" content="1280">' in landing
assert '<meta property="og:image:height" content="720">' in landing
assert 'G-BKMG1B8WPZ' in landing
for path,(data,sha) in files.items():
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
# Existing base CSS supports an offline preview without modifying it in Git.
asset='_next/static/chunks/09xumwo6mu4xc.css'
p=OUT/asset;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(getfile(asset))
commit=api('/git/commits/'+BASE)
entries=[]
for path,(data,sha) in files.items():
    entries.append({'path':path,'mode':'100644','type':'blob','sha':sha or putblob(data)})
tree=api('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries})
staged=api('/git/commits','POST',{'message':'Restore November 9 and 10 newsletter archive and update landscape artwork','tree':tree['sha'],'parents':[BASE]})
comparison=api('/compare/'+BASE+'...'+staged['sha'])
assert {x['filename'] for x in comparison['files']}==set(files)
assert comparison['ahead_by']==1 and comparison['behind_by']==0
report={'staged_commit':staged['sha'],'expected_main':BASE,'paths':{x['path']:x['sha'] for x in entries},'archive_dates':[e['date'] for e in manifest['editions']],'added_dates':[e['date'] for e in editions],'latest_preserved':'2026-11-11','image_sha256':'5e8e43cafe5a4f09df525bb7951694f2f568b657aebaab332b7004774a945b80','pdf_sha256':{e['date']:e['sha256'] for e in editions}}
Path('archive-prepared.json').write_text(json.dumps(report,indent=2))
print('STAGED_ARCHIVE_COMMIT='+staged['sha'])
print('EXPECTED_MAIN='+BASE)
print('SCOPED_FILE_COUNT='+str(len(files)))
print('Archive dates:',','.join(report['added_dates']))
print('No main reference, old PDF, schedule, email send, analytics, repository settings or Pages workflow changed.')
