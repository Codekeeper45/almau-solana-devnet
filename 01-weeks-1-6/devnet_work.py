import json, os, time
from pathlib import Path
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
ROOT=Path(__file__).parent
RPC='https://api.devnet.solana.com'
def rpc(method,params):
    r=requests.post(RPC,json={'jsonrpc':'2.0','id':1,'method':method,'params':params},timeout=40)
    r.raise_for_status(); d=r.json()
    if 'error' in d: raise RuntimeError(str(d['error']))
    return d['result']
def key(name):
    p=ROOT/'private'/f'{name}.json'; p.parent.mkdir(exist_ok=True)
    if p.exists(): return Keypair.from_bytes(bytes(json.loads(p.read_text())))
    k=Keypair(); fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f: json.dump(list(bytes(k)),f)
    return k
if __name__=='__main__':
    a,b=key('student'),key('recipient'); print('Student:',a.pubkey(),'Recipient:',b.pubkey(),flush=True)
    evidence=ROOT/'evidence'; evidence.mkdir(exist_ok=True)
    balance=rpc('getBalance',[str(a.pubkey()),{'commitment':'confirmed'}]); print('Balance:',balance,flush=True)
    if balance['value']<2000000:
        try: print('Airdrop:',rpc('requestAirdrop',[str(a.pubkey()),1000000000,{'commitment':'confirmed'}]),flush=True)
        except Exception as e: print('Airdrop blocked:',e,flush=True)
        time.sleep(3)
    balance=rpc('getBalance',[str(a.pubkey()),{'commitment':'confirmed'}]); print('Balance after:',balance,flush=True)
    (evidence/'wallet.json').write_text(json.dumps({'rpc':RPC,'student':str(a.pubkey()),'recipient':str(b.pubkey()),'balance':balance},indent=2))
    if balance['value']<2000000: raise SystemExit('BLOCKED: insufficient Devnet SOL, no transaction sent')
    bh=rpc('getLatestBlockhash',[{'commitment':'confirmed'}])['value']['blockhash']
    ix=transfer(TransferParams(from_pubkey=a.pubkey(),to_pubkey=b.pubkey(),lamports=1000000))
    tx=Transaction.new_signed_with_payer([ix],a.pubkey(),[a],Hash.from_string(bh))
    import base64
    sig=rpc('sendTransaction',[base64.b64encode(bytes(tx)).decode(),{'encoding':'base64','preflightCommitment':'confirmed'}]); print('Sent:',sig,flush=True)
    for _ in range(20):
        result=rpc('getTransaction',[sig,{'encoding':'jsonParsed','commitment':'confirmed','maxSupportedTransactionVersion':0}])
        if result:
            (evidence/'transfer.json').write_text(json.dumps({'signature':sig,'result':result},indent=2)); print('Confirmed err:',result['meta']['err'],flush=True); break
        time.sleep(2)
    else: raise SystemExit('Not yet confirmed')
