import sys,json,re,hashlib,requests
from pathlib import Path
sys.path.insert(0,'/home/hermes/projects/almau-solana-rk1')
from devnet_work import key
root=Path(__file__).parent
out=root/'evidence';out.mkdir(exist_ok=True)
k=key('program-vault')
p=root/'programs/liquidity_vault/src/lib.rs'
s=p.read_text();s=re.sub(r'declare_id!\("[^"]+"\)',f'declare_id!("{k.pubkey()}")',s)
p.write_text(s)
s=s.split('#[cfg(test)]')[0]
r=requests.post('https://api.solpg.io/build',json={'files':[['/src/lib.rs',s]],'flags':{'seedsFeature':True,'safetyChecks':True}},timeout=240)
(out/'build-response.json').write_text(r.text);r.raise_for_status();d=r.json();print(d.get('stderr',''),flush=True)
assert d.get('uuid') and 'error: could not compile' not in d.get('stderr','')
b=requests.get('https://api.solpg.io/deploy/'+d['uuid'],timeout=60);b.raise_for_status();assert b.content[:4]==b'\x7fELF'
(out/'vault.so').write_bytes(b.content)
(out/'manifest.json').write_text(json.dumps({'program_id':str(k.pubkey()),'bytes':len(b.content),'sha256':hashlib.sha256(b.content).hexdigest(),'uuid':d['uuid']},indent=2))
print('BUILD_VERIFIED',str(k.pubkey()),len(b.content),flush=True)
