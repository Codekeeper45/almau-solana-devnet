# Неделя 2. Transaction Detective
Яппаров Эмир DS

Для анализа использованы публичные транзакции других участников Devnet. Они не выдаются за мои переводы. JSON получен через getTransaction с encoding=jsonParsed.

## Транзакция transaction-1
Ссылка: https://explorer.solana.com/tx/XV7fffZmLkGh8Vr4AvVdh9PcZkqtFniScaro8c5uYBoo8QGgmi1HMFUs3ubGTjuXgDdtEMdKnXgHRpLYhHbDdVU?cluster=devnet
Слот: 510170106. Комиссия: 35000 lamports. Ошибка выполнения: None.
Плательщик комиссии: 6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd.

- Инструкция 1: ComputeBudget111111111111111111111111111111, тип не декодировано RPC.
- Инструкция 2: ComputeBudget111111111111111111111111111111, тип не декодировано RPC.
- Инструкция 3: MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr, тип memo.
- Инструкция 4: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL, тип createIdempotent.
  Поля: {"account": "Expy4H7CJb6SXzL66oAwN1TSU1uYu7yCGUrSvJE2TCA6", "mint": "4wMp7FQJrSwHXJ92kKRd9X2LQE1Tw7L4beT7fBLgjY4y", "source": "6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd"}
- Инструкция 5: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL, тип createIdempotent.
  Поля: {"account": "55Xoy6LMWPpc2DZNUYZPgf3PVhpZKEd6QFeUnqiAAmDQ", "mint": "4wMp7FQJrSwHXJ92kKRd9X2LQE1Tw7L4beT7fBLgjY4y", "source": "6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "2VyJghegXGD7rPxS5HzemSWWjv64N8v8bThJoMRmTeEs"}
- Инструкция 6: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA, тип transfer.
  Поля: {"amount": "1000000000", "authority": "6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd", "destination": "55Xoy6LMWPpc2DZNUYZPgf3PVhpZKEd6QFeUnqiAAmDQ", "source": "Expy4H7CJb6SXzL66oAwN1TSU1uYu7yCGUrSvJE2TCA6"}

Аккаунты и права:
- 6a1wxRdkWZKPHqSJvEEwcd9KywCEtrSnmswHDhNsBNqd: signer=True, writable=True, source=transaction.
- 55Xoy6LMWPpc2DZNUYZPgf3PVhpZKEd6QFeUnqiAAmDQ: signer=False, writable=True, source=transaction.
- Expy4H7CJb6SXzL66oAwN1TSU1uYu7yCGUrSvJE2TCA6: signer=False, writable=True, source=transaction.
- 11111111111111111111111111111111: signer=False, writable=False, source=transaction.
- 2VyJghegXGD7rPxS5HzemSWWjv64N8v8bThJoMRmTeEs: signer=False, writable=False, source=transaction.
- 4wMp7FQJrSwHXJ92kKRd9X2LQE1Tw7L4beT7fBLgjY4y: signer=False, writable=False, source=transaction.
- ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL: signer=False, writable=False, source=transaction.
- ComputeBudget111111111111111111111111111111: signer=False, writable=False, source=transaction.
- MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr: signer=False, writable=False, source=transaction.
- TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA: signer=False, writable=False, source=transaction.

### Объяснение
Compute Budget задаёт вычислительный бюджет и priority fee. Memo хранит текст в инструкции и логах. Associated Token Account Program обеспечивает наличие токен-аккаунта получателя; createIdempotent допускает повторный вызов для существующего аккаунта. SPL Token transfer переводит единицы токена между токен-аккаунтами, это не перевод SOL. Число amount без mint decimals нельзя считать количеством SOL или пользовательских токенов. Неизвестная пользовательская инструкция оставлена недекодированной: без IDL нельзя надёжно назвать её метод.

## Транзакция transaction-2
Ссылка: https://explorer.solana.com/tx/32yNDQx9iRVsxKsFj2BBpaWn1BpiW4RhytN8gmX7LyV6y2gLExjRtHbeXLLQXrDSHVWW7qJCdvuuUgvqiaTWs96h?cluster=devnet
Слот: 510170105. Комиссия: 15700 lamports. Ошибка выполнения: None.
Плательщик комиссии: AVm1wwtnLtsdJSpgz8S2SfC4JDepipEwBpLYuHgQ25Yb.

- Инструкция 1: ComputeBudget111111111111111111111111111111, тип не декодировано RPC.
- Инструкция 2: ComputeBudget111111111111111111111111111111, тип не декодировано RPC.
- Инструкция 3: MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr, тип memo.
- Инструкция 4: ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL, тип createIdempotent.
  Поля: {"account": "DFJbHB9qhxWm7QeZ5DS478j6YHBZHbzJaTG7wk5FRCCh", "mint": "Aj1qyqJRvi7VFdCriNvLiiCvjkLW3pTRgFCKSyGtAbsk", "source": "AVm1wwtnLtsdJSpgz8S2SfC4JDepipEwBpLYuHgQ25Yb", "systemProgram": "11111111111111111111111111111111", "tokenProgram": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "wallet": "5ddL6W1bGGSexKb3soLR8i2xsJU1UR5PTW7MVrCqB7W3"}
- Инструкция 5: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA, тип transfer.
  Поля: {"amount": "69511888", "authority": "4tvnspM9Af164V6sBLrCB14p4nKUrJeNWTRRDRVUVWHo", "destination": "DFJbHB9qhxWm7QeZ5DS478j6YHBZHbzJaTG7wk5FRCCh", "source": "8AnqSPLDLU5gPpEpKs2zGBRHJYW11M1F2EwAwqYt4XbW"}
- Инструкция 6: Bz4AoAXL8vkTSFPqR52GwNxFixAbKPJ3VShhgoS2eV2G, тип не декодировано RPC.

Аккаунты и права:
- AVm1wwtnLtsdJSpgz8S2SfC4JDepipEwBpLYuHgQ25Yb: signer=True, writable=True, source=transaction.
- 4tvnspM9Af164V6sBLrCB14p4nKUrJeNWTRRDRVUVWHo: signer=True, writable=False, source=transaction.
- 5ddL6W1bGGSexKb3soLR8i2xsJU1UR5PTW7MVrCqB7W3: signer=True, writable=False, source=transaction.
- 24cTcLgNHsfHW1YyvBoyZijomhBRE9ezcUTwqZpV23Xm: signer=False, writable=True, source=transaction.
- 5NzjFxGb3SPjr3ZKKptLZdgpjcLgY4TRVwuyhX83Kvef: signer=False, writable=True, source=transaction.
- 8AnqSPLDLU5gPpEpKs2zGBRHJYW11M1F2EwAwqYt4XbW: signer=False, writable=True, source=transaction.
- A2wVDvZLWb2bVZqzZZu5sf3UrztvhbnChCSdCRQMkUng: signer=False, writable=True, source=transaction.
- DFJbHB9qhxWm7QeZ5DS478j6YHBZHbzJaTG7wk5FRCCh: signer=False, writable=True, source=transaction.
- GushWWAz6daSFBWuxgmGcpxyYBMPZfgyV26sA5ikRrnn: signer=False, writable=True, source=transaction.
- 11111111111111111111111111111111: signer=False, writable=False, source=transaction.
- ComputeBudget111111111111111111111111111111: signer=False, writable=False, source=transaction.
- MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr: signer=False, writable=False, source=transaction.
- TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA: signer=False, writable=False, source=transaction.
- 2129g7V5wHFByM2tM3BvPfo4J4QhnmeX4yhz2aQ1mYdZ: signer=False, writable=False, source=transaction.
- 494amNfTn5tDhpj5S6t23yrny4bMG7JuaMad8iezH8sy: signer=False, writable=False, source=transaction.
- ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL: signer=False, writable=False, source=transaction.
- Aj1qyqJRvi7VFdCriNvLiiCvjkLW3pTRgFCKSyGtAbsk: signer=False, writable=False, source=transaction.
- Bz4AoAXL8vkTSFPqR52GwNxFixAbKPJ3VShhgoS2eV2G: signer=False, writable=False, source=transaction.
- GcYDfgs2rPoGiGi8YkfsDxpH2Y3BaZmEC4Jy9CRgh7ev: signer=False, writable=False, source=transaction.

### Объяснение
Compute Budget задаёт вычислительный бюджет и priority fee. Memo хранит текст в инструкции и логах. Associated Token Account Program обеспечивает наличие токен-аккаунта получателя; createIdempotent допускает повторный вызов для существующего аккаунта. SPL Token transfer переводит единицы токена между токен-аккаунтами, это не перевод SOL. Число amount без mint decimals нельзя считать количеством SOL или пользовательских токенов. Неизвестная пользовательская инструкция оставлена недекодированной: без IDL нельзя надёжно назвать её метод.

## Модель аккаунтов
Код программы и её состояние разделены: исполняемый аккаунт программы содержит код, аккаунты данных хранят состояние. Признак signer означает наличие подписи в сообщении транзакции, writable разрешает изменение аккаунта, но не отменяет проверок владельца и полномочий внутри программы.
Транзакция атомарна: при ошибке изменения инструкций откатываются, но комиссия за обработанную транзакцию может быть списана. Программы выполняют CPI через внутренние инструкции, поэтому полный анализ использует также meta.innerInstructions и meta.logMessages.