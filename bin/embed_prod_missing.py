#!/usr/bin/env python3
"""T-PTG-621: embed every corpus article on prod (or test) via api/operations.php embed_by_csv_number.
Idempotent: ArticleChunkEmbeddingService skips already-embedded articles. Batches of 200 (API cap).
Usage: python3 embed_prod_missing.py prod|test [--dry-run] [--force] [--csvs 123,456,789]
  --force        re-embed even csv numbers that already have current-model vectors
                 (T-PTG-633 -- use after a stage-1/2/3 cleanup pass changes an
                 article's text, since the ordinary path leaves stale vectors in
                 place forever). Combine with --csvs to scope it, or it applies
                 to the full md_map, which is rarely what a force run wants.
  --csvs a,b,c   only these csv numbers, instead of the full md_map
Reads JOURNALGPT_OPERATIONS_TOKEN and JOURNALGPT_OPERATIONS_URL_<ENV> from task_coordinator/.env.
"""
import json, os, sys, time, urllib.request, pathlib
env = sys.argv[1] if len(sys.argv) > 1 else 'test'
dry = '--dry-run' in sys.argv
force = '--force' in sys.argv
root = pathlib.Path(__file__).resolve().parents[1]
cfg = {}
for line in (root / '.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); cfg[k.strip()] = v.strip()
token = cfg['JOURNALGPT_OPERATIONS_TOKEN']; base = cfg[f'JOURNALGPT_OPERATIONS_URL_{env.upper()}'].rstrip('/')
csvs_arg = next((a.split('=', 1)[1] if '=' in a else sys.argv[i + 1]
                  for i, a in enumerate(sys.argv) if a == '--csvs' or a.startswith('--csvs=')), None)
if csvs_arg:
    csvs = sorted({int(c) for c in csvs_arg.split(',') if c.strip()})
else:
    md_map = json.loads((root.parent / 'newmexicoptg.org/journalgpt/corpus/articles/md_map.json').read_text())
    csvs = sorted(int(k) for k in md_map)
print(f'{env}: {len(csvs)} csv numbers{" (--csvs)" if csvs_arg else " in md_map"}, force={force}, {len(csvs)//200+1} jobs', file=sys.stderr)
def call(path, body=None, tries=6, timeout=120):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST' if body is not None else 'GET')
            with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
        except Exception as e:  # read timeouts: the server may be running the batch inline
            last = e; print(f'  {path} attempt {attempt+1}: {type(e).__name__}: {str(e)[:120]}', file=sys.stderr, flush=True); time.sleep(20)
    raise last
for i in range(0, len(csvs), 200):
    batch = csvs[i:i+200]
    if dry: print('would submit', batch[0], '..', batch[-1]); continue
    args = {'csv_numbers': batch}
    if force: args['force'] = True
    created = call('/create', {'type': 'embed_by_csv_number', 'arguments': args})
    job = created['job']
    try: call(f"/confirm/{job['id']}", {'confirmation_secret': created['confirmation_secret']}, tries=1, timeout=600)
    except Exception as e: print(f'  confirm returned {type(e).__name__}; polling status', file=sys.stderr, flush=True)
    while True:
        time.sleep(15); j = call(f"/status/{job['id']}")['job']
        if j.get('state') in ('succeeded', 'failed'): break
    print(batch[0], '..', batch[-1], j.get('state'), json.dumps(j.get('result') or j.get('error') or '')[:200], flush=True)
