import json
from pathlib import Path
from devnet_work import rpc
root=Path(__file__).parent/'evidence'/'detective';root.mkdir(parents=True,exist_ok=True)
program='MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'
rows=rpc('getSignaturesForAddress',[program,{'limit':5}])
count=0
for row in rows:
 if row.get('err'):continue
 sig=row['signature'];tx=rpc('getTransaction',[sig,{'encoding':'jsonParsed','maxSupportedTransactionVersion':0,'commitment':'confirmed'}])
 if not tx:continue
 (root/f'transaction-{count+1}.json').write_text(json.dumps({'signature':sig,'provenance':'Public third-party transaction for analysis only. NOT performed by student.','result':tx},indent=2))
 print(json.dumps({'signature':sig,'slot':tx['slot'],'fee':tx['meta']['fee'],'payer':tx['transaction']['message']['accountKeys'][0], 'instructions':tx['transaction']['message']['instructions']},ensure_ascii=False))
 count+=1
 if count==2:break
if count<2:raise SystemExit('Incomplete: fewer than two real public transactions')
