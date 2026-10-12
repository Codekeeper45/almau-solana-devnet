import json
from pathlib import Path
root=Path(__file__).parent
lines=['# Неделя 2. Transaction Detective','Яппаров Эмир DS','','Для анализа использованы публичные транзакции других участников Devnet. Они не выдаются за мои переводы. JSON получен через getTransaction с encoding=jsonParsed.','']
for p in sorted((root/'evidence'/'detective').glob('transaction-*.json')):
 d=json.loads(p.read_text());t=d['result'];m=t['transaction']['message'];meta=t['meta'];lines.extend([f"## Транзакция {p.stem}",f"Ссылка: https://explorer.solana.com/tx/{d['signature']}?cluster=devnet",f"Слот: {t['slot']}. Комиссия: {meta['fee']} lamports. Ошибка выполнения: {meta['err']}.",f"Плательщик комиссии: {m['accountKeys'][0]['pubkey']}.",''])
 for i,ix in enumerate(m['instructions'],1):
  parsed=ix.get('parsed');typ=parsed.get('type') if isinstance(parsed,dict) else ('memo' if isinstance(parsed,str) else 'не декодировано RPC')
  lines.append(f"- Инструкция {i}: {ix['programId']}, тип {typ}.")
  if isinstance(parsed,dict):lines.append('  Поля: '+json.dumps(parsed.get('info',{}),ensure_ascii=False))
 lines.append('')
 lines.append('Аккаунты и права:')
 for a in m['accountKeys']:lines.append(f"- {a['pubkey']}: signer={a['signer']}, writable={a['writable']}, source={a.get('source','unknown')}.")
 lines.extend(['','### Объяснение','Compute Budget задаёт вычислительный бюджет и priority fee. Memo хранит текст в инструкции и логах. Associated Token Account Program обеспечивает наличие токен-аккаунта получателя; createIdempotent допускает повторный вызов для существующего аккаунта. SPL Token transfer переводит единицы токена между токен-аккаунтами, это не перевод SOL. Число amount без mint decimals нельзя считать количеством SOL или пользовательских токенов. Неизвестная пользовательская инструкция оставлена недекодированной: без IDL нельзя надёжно назвать её метод.',''])
lines.extend(['## Модель аккаунтов','Код программы и её состояние разделены: исполняемый аккаунт программы содержит код, аккаунты данных хранят состояние. Признак signer означает наличие подписи в сообщении транзакции, writable разрешает изменение аккаунта, но не отменяет проверок владельца и полномочий внутри программы.','Транзакция атомарна: при ошибке изменения инструкций откатываются, но комиссия за обработанную транзакцию может быть списана. Программы выполняют CPI через внутренние инструкции, поэтому полный анализ использует также meta.innerInstructions и meta.logMessages.'])
(root/'WEEK2.md').write_text('\n'.join(lines),encoding='utf-8')
print('Written WEEK2.md from two RPC responses')
