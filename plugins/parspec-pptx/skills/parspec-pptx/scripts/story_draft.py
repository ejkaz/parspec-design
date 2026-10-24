"""Build a confidential LOCAL draft from caller-supplied JSON, never bundled data.

--content is required. IN20/IN21/IN22 use the plain builder schemas documented
in references/story-archetypes.md. External partner labeling is the default.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from story_gallery import build_story, load_fixture, placeholders, FIXTURE, TEMPLATE_DIR


def normalize_content(source):
    """Adapt the external authoring schema without adding company-specific text."""
    result={}
    for sid in ('IN20','IN21','IN22'):
        r=source[sid].copy()
        r['title']=r.get('title',r.get('headline',''))
        # Explicit breaks preserve the profile's title size.
        if len(r['title'])>65:
            words=r['title'].split();middle=min(range(1,len(words)),key=lambda j:abs(len(' '.join(words[:j]))-len(r['title'])/2))
            r['title']=' '.join(words[:middle])+'\n'+' '.join(words[middle:])
        r['subtitle']=r.get('subtitle',r.get('dek',source.get('as_of','')))
        r['notes']='\n'.join(r.get('source_notes',[]))+'\n'+source.get('confidentiality','')+'\nAs of '+source.get('as_of','')
        if sid=='IN20' and 'stages' in r:
            r['columns']=[dict(name=v['stage'],buyer_job=v['buyer_job'],status=v['status']+'\n'+v.get('as_of',''),context=v['reusable_from_wedge'],dependency=v.get('dependency','UNKNOWN: scope / buyer budget')) for v in r['stages']]
        if sid=='IN21' and 'lanes' in r:
            lanes=r['lanes']
            r['triggers']=[dict(text=v) if isinstance(v,str) else v for v in lanes['trigger']]
            r['agent_steps']=[dict(text=v.get('text',v.get('step')),status=v['status']) for v in lanes['agent_steps']]
            r['human_controls']=[dict(text=v.get('text',v.get('control'))) for v in lanes['human_controls']]
            r['notes']+='\n'+r.get('status_legend','')+'\n'+'\n'.join(v.get('why','') for v in lanes['human_controls'])
            r['audit_path']=r.get('audit_path','')
        if sid=='IN22':
            r['rows']=[dict(request=v['request'],response=v.get('response',v.get('product_response')),status=v.get('status',v.get('observed_status')),next_test=v['next_test']) for v in r['rows']]
            chronology=r['chronology']
            r['chronology']=[(v['date']+'\n'+v['event']) if isinstance(v,dict) else v for v in chronology]
        result[sid]=r
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--content',type=Path,required=True)
    ap.add_argument('--data',type=Path,default=FIXTURE)
    ap.add_argument('--out',type=Path,default=TEMPLATE_DIR/'seriesb_story/Parspec_SeriesB_Story_Draft.pptx')
    ap.add_argument('--internal',action='store_true')
    ap.add_argument('--wait-seconds',type=int,default=1200)
    ap.add_argument('--evidence',type=Path)
    a=ap.parse_args();deadline=time.monotonic()+min(1200,max(0,a.wait_seconds))
    while not a.content.exists() and time.monotonic()<deadline:
        time.sleep(min(5,max(0,deadline-time.monotonic())))
    missing=not a.content.exists()
    if missing:
        content=placeholders();sha='PLACEHOLDERS: content absent after wait'
    else:
        raw=a.content.read_bytes();content=json.loads(raw);sha=hashlib.sha256(raw).hexdigest()
        # Accept either top-level slide records or a "slides" mapping.
        labels=content;content=content.get('slides',content)
        external=labels.get('partner_label_external',content.get('partner_label_external'))
        internal=labels.get('partner_label_internal',content.get('partner_label_internal'))
        label=internal if a.internal else external
        if not label: raise ValueError('requested partner label absent; refusing inferred identity')
        content=normalize_content({**labels,**content})
        content['IN22']['partner_label']=label
        content['IN22']['subtitle']=label
    d,fixture_sha=load_fixture(a.data)
    receipt=build_story(content,d,a.out,content_sha=sha,fixture_sha=fixture_sha)
    receipt.update(content_missing=missing,partner_label_mode='internal' if a.internal else 'external')
    if a.evidence:
        a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'{a.out}: 13 slides; '+('PLACEHOLDERS' if missing else 'local content; '+receipt['partner_label_mode']+' label'))


if __name__=='__main__': main()
