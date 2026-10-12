import sys,json,struct
from lecture_practice import *
def deliver(address):
 recipient=Pubkey.from_string(address)
 assert str(recipient)==address and recipient!=a
 p=OUT/('recipient-'+address+'.json')
 if p.exists():print(p.read_text());return
 target=Pubkey.find_program_address([bytes(recipient),bytes(TOKEN),bytes(mint.pubkey())],ATA)[0]
 ixs=[Instruction(ATA,b'\x01',[M(a,True,True),M(target,False,True),M(recipient,False,False),M(mint.pubkey(),False,False),M(SYS,False,False),M(TOKEN,False,False)]),Instruction(TOKEN,struct.pack('<BQ',12,100000000)+bytes([6]),[M(ata,False,True),M(mint.pubkey(),False,False),M(target,False,True),M(a,True,False)])]
 sig=send(ixs,[payer])
 p.write_text(json.dumps({'signature':sig,'recipient':address,'ata':str(target),'verification_pending':True},indent=2))
 tx=rpc('getTransaction',[sig,{'encoding':'json','maxSupportedTransactionVersion':0}]);assert tx and tx['meta']['err'] is None
 b=rpc('getTokenAccountBalance',[str(target)]);assert int(b['value']['amount'])>=100000000
 d={'signature':sig,'recipient':address,'ata':str(target),'amount':100,'balance':b,'transaction':tx};p.write_text(json.dumps(d,indent=2));print(json.dumps({'recipient':address,'signature':sig,'amount':100}))
if __name__=='__main__':deliver(sys.argv[1])
