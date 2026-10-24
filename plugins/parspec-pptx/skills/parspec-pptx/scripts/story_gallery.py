"""Build a local Series B story gallery from explicitly fictional fixtures."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

SKILL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SKILL))
from assets.house import HouseDeck, TEMPLATE_DIR
from assets import story

FIXTURE=SKILL/'fixtures/incubation_fixture.json'


def placeholders():
    return {
        'IN20': {'columns':[
            dict(name='Intake',buyer_job='[Buyer / intake job]',status='Prototype',context='[Request and account context]',dependency='[Access and permission scope]'),
            dict(name='Quote',buyer_job='[Buyer / paid quoting job]',status='Live',context='[Product and quote context]',dependency='[Acceptance and price proof]'),
            dict(name='Post-award',buyer_job='[Buyer / next workflow]',status='Roadmap',context='[Reusable project context]',dependency='[Integration and buyer budget]')]},
        'IN21': {'triggers':[dict(text='[Customer request]',status='Prototype'),dict(text='[System event]',status='Roadmap')],
                 'agent_steps':[dict(text='[Prepare work]',status='Demo environment'),dict(text='[Check confidence]',status='Prototype'),dict(text='[Prepare response]',status='Roadmap')],
                 'human_controls':[dict(text='[Approve output]',status='Prototype'),dict(text='[Resolve exception]',status='Roadmap')]},
        'IN22': {'partner_label':'[Anonymous design partner] · generic placeholder',
                 'rows':[dict(request=f'[{r}]',response='[Response / specification]',status='[Observed stage]',next_test='[Next evaluation]') for r in ('Traceability','Ambiguous routing','Low-confidence review','Restricted access')],
                 'chronology':['[Steering review]','[Specialist review]','[Sample evaluation planned]']}}


def build_story(content, fixture, output, *, content_sha='', fixture_sha=''):
    deck=HouseDeck('investor')
    for sid,func in [('IN20',story.wedge_workflow),('IN21',story.agent_swimlanes),('IN22',story.learning_ledger)]:
        s=func(deck,content[sid])
        deck.notes(s,s.notes_slide.notes_text_frame.text+'\nContent SHA-256: '+content_sha)
    story.incubation_divider(deck)
    for n,func in story.BUILDERS.items():
        s=func(deck,fixture[f'IN{n}'])
        deck.notes(s,s.notes_slide.notes_text_frame.text+f'\nFictional fixture IN{n}. SHA-256: '+fixture_sha)
    output.parent.mkdir(parents=True,exist_ok=True)
    deck.save(output)
    return dict(deck=str(output),slides=13,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),content_sha256=content_sha,fixture_sha256=fixture_sha)


def load_fixture(path):
    raw=path.read_bytes();d=json.loads(raw)
    if 'DUMMY NUMBERS' not in d.get('_note','') or 'Not Parspec data' not in d['_note']:
        raise ValueError('requires explicitly fictional incubation fixture')
    return d,hashlib.sha256(raw).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=FIXTURE)
    ap.add_argument('--out',type=Path,default=TEMPLATE_DIR/'parspec_seriesb_story_gallery.pptx')
    ap.add_argument('--evidence',type=Path)
    a=ap.parse_args();d,sha=load_fixture(a.data)
    receipt=build_story(placeholders(),d,a.out,content_sha='generic-placeholders',fixture_sha=sha)
    if a.evidence:
        a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'{a.out}: 13 slides')


if __name__=='__main__': main()
