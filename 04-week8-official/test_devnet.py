import sys,json,hashlib,struct,base64
from pathlib import Path
sys.path.insert(0,'/home/hermes/projects/almau-solana-rk1')
from devnet_work import rpc,key
from deploy_devnet import send,payer
from solders.pubkey import Pubkey as P
from solders.instruction import Instruction,AccountMeta as M
root=Path(__file__).parent;p=key('program-week8').pubkey();mint=P.from_string('HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe');u=key('week8-user');v=P.find_program_address([b'vault',bytes(mint)],p)[0];t=P.find_program_address([b'vault_tokens',bytes(mint)],p)[0];s=P.find_program_address([b'share_mint',bytes(mint)],p)[0];card=P.find_program_address([b'user_card',bytes(v),bytes(u.pubkey())],p)[0];system=P.default();token=P.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');rent=P.from_string('SysvarRent111111111111111111111111111111111');ev=[]
def ix(name,ac,data=b''):return Instruction(p,hashlib.sha256(('global:'+name).encode()).digest()[:8]+data,ac)
def info(a):return rpc('getAccountInfo',[str(a),{'encoding':'base64'}])['value']
def execute(name,ac,signers,data=b''):
 sig=send([ix(name,ac,data)],signers);ev.append({'instruction':name,'signature':sig});return sig
def rejected(name,ac,signers,data=b''):
 from solders.transaction import Transaction
 from solders.message import Message
 tx=Transaction(signers,Message([ix(name,ac,data)],payer.pubkey()),__import__('solders.hash',fromlist=['Hash']).Hash.from_string(rpc('getLatestBlockhash',[])['value']['blockhash']))
 result=rpc('simulateTransaction',[base64.b64encode(bytes(tx)).decode(),{'encoding':'base64','sigVerify':True}])['value'];assert result['err'];ev.append({'negative':name,'err':result['err'],'logs':result['logs']})
if not info(u.pubkey()):
 from solders.system_program import transfer,TransferParams
 send([transfer(TransferParams(from_pubkey=payer.pubkey(),to_pubkey=u.pubkey(),lamports=20000000))],[payer])
if not info(v):execute('initialize_vault',[M(v,False,True),M(t,False,True),M(s,False,True),M(mint,False,False),M(payer.pubkey(),True,True),M(token,False,False),M(system,False,False),M(rent,False,False)],[payer])
create=[M(v,False,False),M(card,False,True),M(u.pubkey(),True,True),M(system,False,False)]
if not info(card):execute('create_user_card',create,[payer,u])
d=base64.b64decode(info(card)['data'][0]);created=struct.unpack_from('<q',d,8)[0];now=rpc('getBlockTime',[rpc('getSlot',[])])
assert abs(now-created)<300
rejected('create_user_card',create,[payer,u])
rejected('set_paused',[M(v,False,True),M(u.pubkey(),True,False)],[payer,u],b'\x01')
close=[M(v,False,False),M(card,False,True),M(u.pubkey(),True,True)]
rejected('close_user_card',[M(v,False,False),M(card,False,True),M(payer.pubkey(),True,True)],[payer])
execute('set_paused',[M(v,False,True),M(payer.pubkey(),True,False)],[payer],b'\x01')
amount=info(card)['lamports'];before=rpc('getBalance',[str(u.pubkey())])['value'];execute('close_user_card',close,[payer,u]);assert not info(card);assert rpc('getBalance',[str(u.pubkey())])['value']-before==amount
rejected('create_user_card',create,[payer,u])
execute('set_paused',[M(v,False,True),M(payer.pubkey(),True,False)],[payer],b'\x00');execute('create_user_card',create,[payer,u]);assert info(card)
(root/'evidence/live-tests.json').write_text(json.dumps({'program':str(p),'vault':str(v),'share_mint':str(s),'token_vault':str(t),'card':str(card),'user':str(u.pubkey()),'created_at':created,'rent_returned':amount,'checks':ev},indent=2));print('VERIFIED timestamp, duplicate rejection, unauthorized pause/close, close while paused, exact rent return, paused rejection, unpause and recreate',flush=True)
