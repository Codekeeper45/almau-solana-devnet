import base64,json,struct,time
from pathlib import Path
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import Instruction,AccountMeta
from solders.system_program import create_account,CreateAccountParams
from solders.transaction import Transaction
from devnet_work import rpc,key
ROOT=Path(__file__).parent
LOADER=Pubkey.from_string('BPFLoader2111111111111111111111111111111111')
payer=key('student')
def send(ixs,signers):
 bh=rpc('getLatestBlockhash',[{'commitment':'confirmed'}])['value']['blockhash']
 tx=Transaction.new_signed_with_payer(ixs,payer.pubkey(),signers,Hash.from_string(bh))
 sig=rpc('sendTransaction',[base64.b64encode(bytes(tx)).decode(),{'encoding':'base64','preflightCommitment':'confirmed'}])
 for _ in range(50):
  s=rpc('getSignatureStatuses',[[sig]])['value'][0]
  if s and s['confirmationStatus'] in ['confirmed','finalized']:
   if s['err']:raise RuntimeError(str(s['err']))
   return sig
  time.sleep(.5)
 raise RuntimeError('Confirmation timeout '+sig)
def deploy(name):
 program=key('program-'+name);binary=(ROOT/f'evidence/cloud-build/{name}.so').read_bytes()
 rent=rpc('getMinimumBalanceForRentExemption',[len(binary)])
 print('rent lamports',name,rent,flush=True)
 account=rpc('getAccountInfo',[str(program.pubkey()),{'encoding':'base64'}])['value']
 log=[]
 if not account:
  log.append(send([create_account(CreateAccountParams(from_pubkey=payer.pubkey(),to_pubkey=program.pubkey(),lamports=rent,space=len(binary),owner=LOADER))],[payer,program]))
 elif account['executable']:return
 for off in range(0,len(binary),850):
  chunk=binary[off:off+850]
  data=struct.pack('<IIQ',0,off,len(chunk))+chunk
  ix=Instruction(LOADER,data,[AccountMeta(program.pubkey(),True,True)])
  log.append(send([ix],[payer,program]));print('write',off,flush=True)
 ix=Instruction(LOADER,struct.pack('<I',1),[AccountMeta(program.pubkey(),True,True),AccountMeta(Pubkey.from_string('SysvarRent111111111111111111111111111111111'),False,False)])
 log.append(send([ix],[payer,program]))
 info=rpc('getAccountInfo',[str(program.pubkey()),{'encoding':'base64'}])['value'];assert info['executable']
 (ROOT/f'evidence/cloud-build/{name}-deploy.json').write_text(json.dumps({'program_id':str(program.pubkey()),'signatures':log,'executable':info['executable'],'owner':info['owner']},indent=2))
 print('DEPLOYED',name,program.pubkey(),flush=True)
if __name__=='__main__':deploy('first')
