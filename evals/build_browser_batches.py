#!/usr/bin/env python3
"""Preregister fresh ChatGPT browser comparison batches via oracle-task-orchestrator."""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE_ROOT = ROOT.parent / 'oracle-runs'
CREATE = Path.home() / '.codex/skills/oracle-task-orchestrator/scripts/create_batch.py'
ARMS = ('base', 'verify', 'horizon', 'two_turn_base', 'clarify')
PROMPT_PATHS = {
    'verify': ROOT / 'prompts/verification-first.txt',
    'horizon': ROOT / 'prompts/question-horizon.txt',
    'clarify': ROOT / 'prompts/clarify-then-investigate.txt',
}
PROMPTS = {name: path.read_text(encoding='utf-8').strip() for name,path in PROMPT_PATHS.items()}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--repeats', type=int, default=None)
    ap.add_argument('--concurrency', type=int, default=3)
    args = ap.parse_args()
    if args.concurrency != 3:
        raise SystemExit('This browser replication is fixed to the user-requested concurrency 3')
    repeats = args.repeats if args.repeats is not None else (1 if args.pilot else 3)
    if repeats < 1:
        raise SystemExit('Repeats must be positive')
    task_path = ROOT / 'evals' / ('browser-web-pilot-tasks.json' if args.pilot else 'browser-web-tasks.json')
    tasks = json.loads(task_path.read_text(encoding='utf-8'))
    expected = 3 if args.pilot else 15
    if len(tasks) != expected or len({task['id'] for task in tasks}) != expected:
        raise SystemExit('Wrong number of unique tasks')
    if not args.pilot and Counter(task['category'] for task in tasks) != Counter({'factual':4,'analytical':4,'practical':4,'ambiguous':3}):
        raise SystemExit('Category balance changed')
    for task in tasks:
        if not all(task.get(k) for k in ('prompt','seed','required','latent','clarify','sources')):
            raise SystemExit(f"Incomplete case: {task['id']}")
        if not all(source.startswith('https://') for source in task['sources']):
            raise SystemExit(f"Invalid official-source URL: {task['id']}")
    design = [{'task_id':task['id'], 'category':task['category'], 'arm':arm, 'repeat':repeat}
              for task in tasks for arm in ARMS for repeat in range(1,repeats+1)]
    random.Random(20260929 if not args.pilot else 20260928).shuffle(design)
    run_root = ORACLE_ROOT / 'research-prompt-benchmark'
    run_root.mkdir(parents=True, exist_ok=True)
    staging = run_root / f'{args.run_id}-items.json'
    if staging.exists():
        raise SystemExit(f'Existing staging file: {staging}')
    staging.write_text(json.dumps([{'title': f"{row['task_id']}-{row['arm']}-r{row['repeat']}",
                                    'brief': 'Frozen official-source browser research benchmark'} for row in design],indent=2)+'\n')
    command = ['python3',str(CREATE),'--brief','Official-source research prompt benchmark',
               '--artifact','text','--items-file',str(staging), '--task-slug','research-prompt-benchmark',
               '--run-id',args.run_id,'--engine','browser','--model','gpt-5.6-sol',
               '--browser-research','search','--independent-replicates','--timeout','12m',
               '--concurrency','3','--language','en','--output-root',str(ORACLE_ROOT)]
    batch_path = Path(subprocess.check_output(command,text=True).strip())
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    by_id = {task['id']:task for task in tasks}
    for row,item in zip(design,batch['items'],strict=True):
        task = by_id[row['task_id']]
        full = task['prompt']
        followup = 'Here are the complete case details and my answers to the relevant questions. Please now answer the original question.\n\n'+full
        if row['arm']=='base':
            initial, followups = full, []
        elif row['arm']=='verify':
            initial, followups = full+'\n\n'+PROMPTS['verify'], []
        elif row['arm']=='horizon':
            initial, followups = full+'\n\n'+PROMPTS['horizon'], []
        elif row['arm']=='two_turn_base':
            initial, followups = task['seed'], [followup]
        else:
            initial, followups = task['seed']+'\n\n'+PROMPTS['clarify'], [followup]
        chain_path=Path(item['chainPath'])
        chain=json.loads(chain_path.read_text(encoding='utf-8'))
        chain['promptChain']={'initialPrompt':initial,'followUps':followups}
        chain_path.write_text(json.dumps(chain,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        row['item_id']=item['id']
    run_dir=batch_path.parent
    (run_dir/'design.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n')
    (run_dir/'tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+'\n')
    manifest={'protocol':'browser-web-20260929-v1','pilot':args.pilot,'taskCount':len(tasks),'arms':list(ARMS),
              'repeats':repeats,'dialogueCount':len(design),'concurrency':3,'engine':'browser',
              'model':'gpt-5.6-sol','thinking':'High','research':'search','independent':True,
              'taskSha256':sha256(task_path),'promptSha256':{name:sha256(path) for name,path in PROMPT_PATHS.items()},
              'seed':20260928 if args.pilot else 20260929}
    (run_dir/'preregistration.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(batch_path)
    print(f"{len(tasks)} tasks × {len(ARMS)} arms × {repeats} repeats = {len(design)} dialogues")

if __name__=='__main__':
    main()
