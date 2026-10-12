import sys
sys.path.insert(0,"/home/hermes/projects/almau-solana-rk1")
import json,struct,base64,time
from pathlib import Path
from solders.pubkey import Pubkey
from solders.instruction import Instruction,AccountMeta as M
from solders.system_program import create_account,CreateAccountParams
from deploy_devnet import send,payer
from devnet_work import rpc,key
ROOT=Path(__file__).parent
L=Pubkey.from_string('BPFLoaderUpgradeab1e11111111111111111111111')
S=Pubkey.from_string('11111111111111111111111111111111');R=Pubkey.from_string('SysvarRent111111111111111111111111111111111');C=Pubkey.from_string('SysvarC1ock11111111111111111111111111111111')
def deploy(name):
 b=(ROOT/f'evidence/cloud-build/{name}.so').read_bytes(); p=key('v3-'+name); buf=key('buffer-'+name)
 # Anchor binary embeds original declared ID, so use original key for Anchor programs.
 if name!='first':p=key('program-'+name)
 rent=rpc('getMinimumBalanceForRentExemption',[37+len(b)])
 existing=rpc('getAccountInfo',[str(buf.pubkey()),{'encoding':'base64'}])['value']
 sigs=[]
 if not existing:
  ix=create_account(CreateAccountParams(from_pubkey=payer.pubkey(),to_pubkey=buf.pubkey(),lamports=rent,space=37+len(b),owner=L))
  init=Instruction(L,struct.pack('<I',0),[M(buf.pubkey(),False,True),M(payer.pubkey(),False,False)])
  sigs.append(send([ix,init],[payer,buf]))
 for off in range(0,len(b),900):
  chunk=b[off:off+900]
  if existing and base64.b64decode(existing['data'][0])[37+off:37+off+len(chunk)]==chunk: continue
  ix=Instruction(L,struct.pack('<IIQ',1,off,len(chunk))+chunk,[M(buf.pubkey(),False,True),M(payer.pubkey(),True,False)])
  sigs.append(send([ix],[payer]));print(name,'write',off,flush=True)
 pd,_=Pubkey.find_program_address([bytes(p.pubkey())],L)
 prent=rpc('getMinimumBalanceForRentExemption',[36])
 create=create_account(CreateAccountParams(from_pubkey=payer.pubkey(),to_pubkey=p.pubkey(),lamports=prent,space=36,owner=L))
 deploy=Instruction(L,struct.pack('<IQ',2,len(b)),[M(payer.pubkey(),True,True),M(pd,False,True),M(p.pubkey(),False,True),M(buf.pubkey(),False,True),M(R,False,False),M(C,False,False),M(S,False,False),M(payer.pubkey(),True,False)])
 sigs.append(send([create,deploy],[payer,p]))
 info=rpc('getAccountInfo',[str(p.pubkey()),{'encoding':'base64'}])['value'];assert info['executable']
 (ROOT/f'evidence/cloud-build/{name}-deploy.json').write_text(json.dumps({'program_id':str(p.pubkey()),'programdata':str(pd),'signatures':sigs,'executable':True,'owner':info['owner']},indent=2))
 print('DEPLOYED',name,p.pubkey(),flush=True)
if __name__=='__main__':deploy('week8')
