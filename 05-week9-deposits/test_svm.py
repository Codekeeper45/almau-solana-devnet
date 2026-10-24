"""Execute the compiled Solana program in LiteSVM, using real SPL Token CPI."""
import hashlib,json,struct
from pathlib import Path
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey as P
from solders.instruction import Instruction,AccountMeta as M
from solders.transaction import Transaction
from solders.account import Account
R=Path(__file__).parent
svm=LiteSVM();admin=Keypair();users=[Keypair() for _ in range(4)]
for k in [admin,*users]:svm.airdrop(k.pubkey(),10**10)
p=P.from_string('EbojNUfh9Jk6dyZaaQAJWofbdnkvdxfQbeAPq6iWoHAu');svm.add_program(p,(R/'evidence/vault.so').read_bytes())
token=P.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');mint=Keypair().pubkey();fee=Keypair().pubkey()
def mint_data(authority,supply=0):return struct.pack('<I',1)+bytes(authority)+struct.pack('<QBBI',supply,6,1,0)+bytes(32)
def token_data(m,owner,amount):return bytes(m)+bytes(owner)+struct.pack('<Q',amount)+bytes(36)+bytes([1])+bytes(12)+struct.pack('<Q',0)+bytes(36)
svm.set_account(mint,Account(10**7,mint_data(admin.pubkey(),4*1000*10**6),token))
svm.set_account(fee,Account(10**7,token_data(mint,admin.pubkey(),0),token))
v=P.find_program_address([b'vault',bytes(mint)],p)[0];t=P.find_program_address([b'vault_tokens',bytes(mint)],p)[0];s=P.find_program_address([b'share_mint',bytes(mint)],p)[0]
cards=[P.find_program_address([b'user_card',bytes(v),bytes(u.pubkey())],p)[0] for u in users]
balances=[];share_accounts=[];checks=[]
for u in users:
 a=Keypair().pubkey();b=Keypair().pubkey();balances.append(a);share_accounts.append(b)
 svm.set_account(a,Account(10**7,token_data(mint,u.pubkey(),1000*10**6),token))
def run(name,accounts,signers,data=b'',failure=None):
 ix=Instruction(p,hashlib.sha256(('global:'+name).encode()).digest()[:8]+data,accounts)
 tx=Transaction.new_signed_with_payer([ix],admin.pubkey(),signers,svm.latest_blockhash());z=svm.send_transaction(tx)
 failed=hasattr(z,'err');logs=z.meta().logs() if failed else z.logs()
 assert failed==(failure is not None),(name,str(z))
 if failure:assert failure in '\n'.join(logs),(failure,logs)
 checks.append({'instruction':name,'expected_error':failure,'logs':logs});svm.expire_blockhash()
def amount(a):return struct.unpack_from('<Q',svm.get_account(a).data,64)[0]
def state():
 d=svm.get_account(v).data
 return struct.unpack_from('<QQ',d,169)
def deps(i,fee_account=fee,share=None):return [M(v,False,True),M(cards[i],False,True),M(mint,False,False),M(fee_account,False,True),M(t,False,True),M(s,False,True),M(balances[i],False,True),M(share or share_accounts[i],False,True),M(users[i].pubkey(),True,True),M(token,False,False)]
run('initialize_vault',[M(v,False,True),M(t,False,True),M(s,False,True),M(mint,False,False),M(fee,False,False),M(admin.pubkey(),True,True),M(token,False,False),M(P.default(),False,False),M(P.from_string('SysvarRent111111111111111111111111111111111'),False,False)],[admin])
assert state()==(0,0)
for i,u in enumerate(users):
 svm.set_account(share_accounts[i],Account(10**7,token_data(s,u.pubkey(),0),token))
 if i<3:run('create_user_card',[M(v,False,False),M(cards[i],False,True),M(u.pubkey(),True,True),M(P.default(),False,False)],[admin,u])
run('deposit',deps(3),[admin,users[3]],struct.pack('<Q',10**6),'AccountNotInitialized')
run('deposit',deps(0),[admin,users[0]],struct.pack('<Q',0),'ZeroAmount')
run('deposit',deps(0),[admin,users[0]],struct.pack('<Q',999999),'BelowMinimum')
run('set_paused',[M(v,False,True),M(users[0].pubkey(),True,False)],[admin,users[0]],b'\x01','ConstraintHasOne')
run('set_paused',[M(v,False,True),M(admin.pubkey(),True,False)],[admin],b'\x01')
run('deposit',deps(0),[admin,users[0]],struct.pack('<Q',10**6),'Paused')
assert amount(t)==0 and amount(fee)==0 and state()==(0,0)
run('create_user_card',[M(v,False,False),M(cards[3],False,True),M(users[3].pubkey(),True,True),M(P.default(),False,False)],[admin,users[3]],failure='Paused')
assert svm.get_account(cards[3]) is None
run('set_paused',[M(v,False,True),M(admin.pubkey(),True,False)],[admin],b'\x00')
wrong=Keypair().pubkey();svm.set_account(wrong,Account(10**7,token_data(mint,admin.pubkey(),0),token))
run('deposit',deps(0,wrong),[admin,users[0]],struct.pack('<Q',10**6),'ConstraintAddress')
run('deposit',deps(0,share=share_accounts[1]),[admin,users[0]],struct.pack('<Q',10**6),'ConstraintTokenOwner')
for i,n in enumerate([100,200,300]):
 run('deposit',deps(i),[admin,users[i]],struct.pack('<Q',n*10**6))
 assert amount(share_accounts[i])==n*990000
 assert amount(balances[i])==(1000-n)*10**6
assert amount(fee)==6*10**6 and amount(t)==594*10**6 and state()==(594*10**6,594*10**6)
for i,n in enumerate([99,198,297]):
 d=svm.get_account(cards[i]).data
 assert struct.unpack_from('<QQ',d,80)==(n*10**6,n*10**6)
run('close_user_card',[M(v,False,False),M(cards[0],False,True),M(users[0].pubkey(),True,True)],[admin,users[0]],failure='ActivePosition')
run('deposit',deps(0),[admin,users[0]],struct.pack('<Q',1001*10**6),'insufficient funds')
assert amount(t)==594*10**6 and amount(fee)==6*10**6 and state()==(594*10**6,594*10**6)
result={'environment':'LiteSVM with compiled SBF and real SPL Token CPI, NOT public Devnet','checks':checks,'summary':{'scenarios':len(checks),'gross_deposits':[100,200,300],'fee_tokens':6,'vault_tokens':594,'shares':[99,198,297],'fractions':['1/6','1/3','1/2'],'decimals':6,'rollback_verified':True}}
(R/'evidence/svm-tests.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('PASS',json.dumps(result['summary'],ensure_ascii=False))
