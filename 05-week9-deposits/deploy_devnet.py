#!/usr/bin/env python3
"""Real Devnet deploy/test runner. Refuses to transact until payer is funded.

Uses solders + Python stdlib HTTP JSON-RPC; never contacts mainnet and never
requests an airdrop. Requires a newly generated program keypair because the
requested historical program ID has no corresponding private key.
"""
import base64, json, os, struct, sys, time, urllib.request
from pathlib import Path
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction

ROOT = Path(__file__).resolve().parent
RPC = 'https://api.devnet.solana.com'
PAYER_FILE = Path('/home/hermes/.hermes/secrets/almau-solana-devnet.json')
KEY_DIR = Path('/home/hermes/.hermes/secrets/almau-solana-week9')
LOADER = Pubkey.from_string('BPFLoader2111111111111111111111111111111111')
TOKEN = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
SYSTEM = Pubkey.default()
RENT = Pubkey.from_string('SysvarRent111111111111111111111111111111111')
EVIDENCE = ROOT / 'evidence'


def rpc(method, params):
    req = urllib.request.Request(RPC, data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=40) as response:
        body=json.loads(response.read())
    if 'error' in body: raise RuntimeError(f'{method}: {body["error"]}')
    return body['result']


def key(name):
    path=KEY_DIR/(name+'.json')
    if path.exists():
        if path.stat().st_mode & 0o077: raise RuntimeError(f'Unsafe permissions on {path}; chmod 600')
        return Keypair.from_bytes(bytes(json.loads(path.read_text())))
    KEY_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(KEY_DIR,0o700)
    kp=Keypair(); fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f: json.dump(list(bytes(kp)),f)
    return kp


def send(ixs, signers, payer):
    bh=Hash.from_string(rpc('getLatestBlockhash',[{'commitment':'confirmed'}])['value']['blockhash'])
    tx=Transaction.new_signed_with_payer(ixs,payer.pubkey(),signers,bh)
    sig=rpc('sendTransaction',[base64.b64encode(bytes(tx)).decode(),{'encoding':'base64','preflightCommitment':'confirmed'}])
    for _ in range(60):
        status=rpc('getSignatureStatuses',[[sig],{'searchTransactionHistory':True}])['value'][0]
        if status and status['confirmationStatus'] in ('confirmed','finalized'):
            if status['err']: raise RuntimeError(f'{sig}: {status["err"]}')
            return sig
        time.sleep(1)
    raise TimeoutError(sig)


def deploy(payer, program, so):
    data=so.read_bytes()
    if rpc('getAccountInfo',[str(program.pubkey()),{'encoding':'base64'}])['value']:
        raise RuntimeError('Program account already exists; refusing ambiguous redeploy')
    rent=rpc('getMinimumBalanceForRentExemption',[len(data),{'commitment':'confirmed'}])
    from solders.system_program import create_account, CreateAccountParams
    sigs=[send([create_account(CreateAccountParams(from_pubkey=payer.pubkey(),to_pubkey=program.pubkey(),lamports=rent,space=len(data),owner=LOADER))],[payer,program],payer)]
    for off in range(0,len(data),850):
        chunk=data[off:off+850]
        ix=Instruction(LOADER,struct.pack('<IIQ',0,off,len(chunk))+chunk,[AccountMeta(program.pubkey(),True,True)])
        sigs.append(send([ix],[payer,program],payer))
    ix=Instruction(LOADER,struct.pack('<I',1),[AccountMeta(program.pubkey(),True,True),AccountMeta(RENT,False,False)])
    sigs.append(send([ix],[payer,program],payer))
    info=rpc('getAccountInfo',[str(program.pubkey()),{'encoding':'base64'}])['value']
    if not info or not info['executable']: raise RuntimeError('Program failed executable verification')
    return sigs


def main():
    EVIDENCE.mkdir(exist_ok=True)
    if not PAYER_FILE.exists(): raise SystemExit(f'BLOCKED: payer key missing: {PAYER_FILE}')
    payer=Keypair.from_bytes(bytes(json.loads(PAYER_FILE.read_text())))
    balance=rpc('getBalance',[str(payer.pubkey()),{'commitment':'confirmed'}])['value']
    print(f'DEVNET payer={payer.pubkey()} balance_lamports={balance}')
    (EVIDENCE/'devnet-preflight.json').write_text(json.dumps({'rpc':RPC,'payer':str(payer.pubkey()),'balance_lamports':balance,'slot':rpc('getSlot',[{'commitment':'confirmed'}])},indent=2))
    if balance == 0: raise SystemExit('BLOCKER: payer balance is zero; no deploy/test transaction sent. Fund only via public Devnet faucet, then rerun.')
    program=key('program')
    if not (EVIDENCE/'vault-new-id.so').exists(): raise SystemExit('BLOCKER: build SBF for new Program ID first; existing vault.so targets the old ID and is NOT valid for deployment.')
    sigs=deploy(payer,program,EVIDENCE/'vault-new-id.so')
    (EVIDENCE/'devnet-deploy.json').write_text(json.dumps({'program_id':str(program.pubkey()),'deploy_signatures':sigs,'rpc':RPC},indent=2))
    raise SystemExit('Deployment done; transaction scenario runner still needs explicit initialized mint/account fixtures; stopping rather than claim unexecuted tests.')

if __name__=='__main__': main()

# Transaction-level test construction is intentionally gated until funded deploy
# and an SBF built against the newly generated program keypair are available.
# Devnet calls must use real SPL Token instructions (InitializeMint2,
# InitializeAccount3, MintTo) and simulateTransaction for negative cases.
