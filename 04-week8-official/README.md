# Неделя 8: Simple Vault и карточки пользователей

Яппаров Эмир DS

Основа: [официальный шаблон students-vault-card](https://github.com/0xnurda/vault-dev/tree/students-vault-card). Сохранены названия initialize_vault/create_user_card и PDA seeds шаблона. Моя первая версия каркаса до шаблона — в `03-liquidity-vault`.

## Три задания

1. UserCard.created_at: i64, время Clock::get()?.unix_timestamp.
2. close_user_card: подписывает только владелец, Anchor close возвращает ему всю ренту. Закрытие разрешено даже при паузе.
3. VaultState.paused: создание карточки блокируется при паузе. Дополнительно set_paused с has_one=admin, посторонний пользователь менять флаг не может.

## Архитектура

```text
mint
  vault_state PDA [vault, mint]: admin, mint, token account, share mint, bump, paused
    vault_token_account PDA [vault_tokens, mint]: token authority = vault_state
    share_mint PDA [share_mint, mint]: mint authority = vault_state
    user_card PDA [user_card, vault_state, user]: created_at, vault, owner, bump
```

Поля created_at и paused добавлены в структуры, размеры LEN увеличены. Программа задеплоена с новым program ID.

## Проверки

`test_svm.py` — 10 сценариев на собранной программе в LiteSVM: успешная инициализация, создание, ошибка дубликата, запрет чужой паузы и закрытия, пауза, закрытие при паузе, точный возврат ренты, запрет создания при паузе, снятие паузы и повторное создание.

`test_devnet.py` — то же самое в Devnet. Запрещённые действия проверяются через simulateTransaction, чтобы не отправлять заведомо неудачные транзакции. Результаты — в `evidence/`.

Программу собирал через Solana Playground. Тесты из шаблона преподавателя — в `tests/vault.ts`.

## Проверено в Devnet

Program ID: G3EE49SHxtdRFMDvzAyB9aWjoLwzBkt62EVhnRzhxw9t.
- [program](https://explorer.solana.com/address/G3EE49SHxtdRFMDvzAyB9aWjoLwzBkt62EVhnRzhxw9t?cluster=devnet)
- [vault](https://explorer.solana.com/address/6xHhvDf4Yo1L9nNbCGaXmYqRuh2e2CEQA3ZATBZ7WidT?cluster=devnet)
- [share_mint](https://explorer.solana.com/address/BdFsb1LXum7BRqHUj2wUtzEKaZHrxQNeVdiHLtSxuBF4?cluster=devnet)
- [token_vault](https://explorer.solana.com/address/GkRiUzMaWe3x8AxQXKGnGxuYjnsqa8KTbBjmM29qK4i2?cluster=devnet)
- [card](https://explorer.solana.com/address/2NjzefFfRAJFH8tCePXftmRyAnekEKH1LCjjdJYv9CEm?cluster=devnet)

created_at: 1791812993. При закрытии карточки вернулось 1 061 720 lamports ренты.
- [initialize_vault](https://explorer.solana.com/tx/4v156otkSKxdeUGAiwBXx93hkCNNPw2wu1ViztoZ1FR87ydkDTz2PhKA9Wf7ETCJNcwpZ6kiJ8bTQzSmH9nqrNdW?cluster=devnet)
- [create_user_card](https://explorer.solana.com/tx/4QqNo9KnC7w5nq7o57BumT77MsBQ1CMykbGRyhgDpFs4JsTkbE6oirTnvKMyhMbF9DKE4VyVHpLtxfcm4A5hPX3q?cluster=devnet)
- [set_paused](https://explorer.solana.com/tx/3euF38Ga5y2KLoFBSvTxecUcVqt4C1GsL7nrys6cpdLRnMGYy9bSAhzA7SAzrcLWBnuZUzPqnz5kXnJvNgpjNswy?cluster=devnet)
- [close_user_card](https://explorer.solana.com/tx/5Sp45Cy63soABJ6cXJYn3qH2V6ZbUamVGgMtrvva3exCTWbiEk9VGW5qBtRzGw1BrxUsRo5oB1hSHrV2XGG8bG5k?cluster=devnet)
- [set_paused](https://explorer.solana.com/tx/4oXttNaNfpx2zkWg8VpK9A9FLTsdpHDbrTvx5XgSLn8HYktoeTvMTNPJF7zHrc6ira2yAd5BjhQ8zpu74Vy1R8fw?cluster=devnet)
- [create_user_card](https://explorer.solana.com/tx/HZkGHLopbBnPfJqJTnm5KrykF4X5JybUSXm1rqF7GP3k26XRj55pWP6bpEux8iSzx72Ps1CuQo9xrovTMiMNcJQ?cluster=devnet)