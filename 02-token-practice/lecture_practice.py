import struct,json,base64
from pathlib import Path
from solders.pubkey import Pubkey
from solders.instruction import Instruction,AccountMeta as M
from solders.system_program import create_account,CreateAccountParams,transfer,TransferParams
from devnet_work import rpc,key
from deploy_devnet import send,payer
ROOT=Path(__file__).parent;OUT=ROOT/'evidence/lecture-practice';OUT.mkdir(parents=True,exist_ok=True)
TOKEN=Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');ATA=Pubkey.from_string('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');SYS=Pubkey.default();a=payer.pubkey();mint=key('lecture-mint');ata=Pubkey.find_program_address([bytes(a),bytes(TOKEN),bytes(mint.pubkey())],ATA)[0]
def step(label,ixs,signers):
 p=OUT/(label+'.json')
 if p.exists():return
 sig=send(ixs,signers);p.write_text(json.dumps({'signature':sig},indent=2));print(label,sig,flush=True)
def main():
 recipient=key('recipient').pubkey()
 step('sol-memo',[transfer(TransferParams(from_pubkey=a,to_pubkey=recipient,lamports=10000000)),Instruction(Pubkey.from_string('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'),b'Hello Solana',[])],[payer])
 if rpc('getAccountInfo',[str(mint.pubkey())])['value'] is None:
  rent=rpc('getMinimumBalanceForRentExemption',[82]);step('create-mint',[create_account(CreateAccountParams(from_pubkey=a,to_pubkey=mint.pubkey(),lamports=rent,space=82,owner=TOKEN)),Instruction(TOKEN,bytes([20,6])+bytes(a)+bytes([1])+bytes(a),[M(mint.pubkey(),False,True)])],[payer,mint])
 if rpc('getAccountInfo',[str(ata)])['value'] is None:step('create-ata',[Instruction(ATA,b'\x01',[M(a,True,True),M(ata,False,True),M(a,False,False),M(mint.pubkey(),False,False),M(SYS,False,False),M(TOKEN,False,False)])],[payer])
 step('mint-10000',[Instruction(TOKEN,struct.pack('<BQ',7,10000000000),[M(mint.pubkey(),False,True),M(ata,False,True),M(a,True,False)])],[payer])
 step('burn-50',[Instruction(TOKEN,struct.pack('<BQ',8,50000000),[M(ata,False,True),M(mint.pubkey(),False,True),M(a,True,False)])],[payer])
 supply=rpc('getTokenSupply',[str(mint.pubkey())]);balance=rpc('getTokenAccountBalance',[str(ata)]);assert supply['value']['amount']=='9950000000';assert balance['value']['amount']=='9950000000'
 d={'cluster':'devnet','mint':str(mint.pubkey()),'ata':str(ata),'authority':str(a),'decimals':6,'supply':supply,'balance':balance,'pending':'Three real classmates public wallet addresses required. No substitutes.','memo_recipient':str(recipient),'memo_recipient_kind':'existing own test recipient, not classmate'}
 for p in OUT.glob('*.json'):
  v=json.loads(p.read_text());sig=v.get('signature')
  if sig:
   tx=rpc('getTransaction',[sig,{'encoding':'json','maxSupportedTransactionVersion':0}]);assert tx and tx['meta']['err'] is None;v['transaction']=tx;p.write_text(json.dumps(v,indent=2))
 (OUT/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
