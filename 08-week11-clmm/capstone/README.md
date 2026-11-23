# Liquidity Vault: неделя 14

Веб-интерфейс для существующей программы в Solana Devnet. Пользователь подключает Phantom или Solflare, видит баланс токена A и долей, вносит токены и выводит их. Кошелёк администратора также видит обмен, открытие позиции Raydium CLMM, сбор комиссий и закрытие. Каждая отправленная транзакция получает ссылку на Explorer. Ключи остаются в кошельке. Интерфейс не поддерживает mainnet.

## Запуск

Нужны Node.js и Python 3. В терминале из папки `08-week11-clmm`:

```sh
npm ci
npx --yes esbuild@0.28.2 capstone/app.mjs --bundle --minify --platform=browser --format=esm --outfile=capstone/app.js
python3 -m http.server 18843 --bind 127.0.0.1 --directory capstone
```

Откройте `http://localhost:18843/` в браузере с кошельком в режиме Devnet. У кошелька должны быть тестовые SOL и токен A. Подписывайте только после проверки сети и суммы. Панель Raydium видна только владельцу адреса администратора из VaultState. Если стратегия ещё открыта, сначала закройте позицию и обменяйте весь остаток B обратно в A.

## Схема

```text
mint A (TOKEN_A)
  └── VaultState PDA ["vault", mint_a] (владелец: программа, хранит admin, доли и текущую позицию)
        ├── vault_token_account PDA ["vault_tokens", mint_a] (баланс A в хранилище)
        ├── quote ATA (ATA для TOKEN_B от VaultState)
        ├── share_mint PDA ["share_mint", mint_a] (mint долей, authority = VaultState)
        ├── UserCard PDA ["user_card", vault_state, user] (вклад и доли пользователя)
        └── NFT позиции Raydium CLMM (Token-2022, владелец: VaultState)
```

Кошелёк подписывает пользовательскую инструкцию. `VaultState` (PDA от mint A) хранит администратора, состояние стратегии и суммы; `UserCard` (PDA от VaultState и кошелька) хранит данные пользователя. `VaultState` управляет счётом хранения A, счётом B и выпуском долей. При депозите программа переводит A в vault и выпускает доли. При выводе сжигает доли и переводит A обратно. Для swap и операций с позицией vault вызывает фиксированный пул Raydium через CPI. NFT позиции принадлежит PDA vault.

- [Программа Devnet](https://explorer.solana.com/address/EGrtYqUVMoRxGbQj6YT5KhYNTdNQsybBjidq8zVJiahQ?cluster=devnet)
- [VaultState](https://explorer.solana.com/address/EkBXz7M3sWLqxFfbW5D19xe3ANU6xqijLVerPJPE4cCh?cluster=devnet)
- [Raydium CLMM](https://explorer.solana.com/address/5d9XKBYg3VJkZjYsyCpWyfTht8KTipWLRhnPgDPrUMac?cluster=devnet)
- Публичные данные о mint и пуле: [devnet-pool.json](../evidence/devnet-pool.json).

## Проверка

Прогнал весь сценарий через интерфейс в Devnet: [депозит](https://explorer.solana.com/tx/WWNBsp29DRfMTM9vTMU5t8XKZsDXVVvQDrRoQnhocsHYq9omRv2nA48QjMyREMwmbVykwNwE5VtkvN3QtUEefm1?cluster=devnet), [swap](https://explorer.solana.com/tx/3zsxqwFChPkv5yZADdu6c48HAmZLFbZfTjNyBrMZ77GFA7okmXyxpCepPskF43zjfBKSfTjsFqgSD9YDQtzmMWdF?cluster=devnet), [открытие](https://explorer.solana.com/tx/2zR4D61B2pF5pxa4NjzVeXGieEj1q9tTAbt4qmJSXaDNtoXfwKz6sVthZCA34NsbKVhwUqVWCF9XUHsbD6YR2D5j?cluster=devnet), [сбор](https://explorer.solana.com/tx/2YpVm7dmWU2EHL8ofph6oJeeKqEaQaDTSse27X4EomYQEsSdLxC7w3ezZWNTFpFBkmC8jpVePbzByRzhDADA2bSV?cluster=devnet), [закрытие](https://explorer.solana.com/tx/4Mbat9JBqkb61oZkFcqiMcowwydoYCqtdn4K2YKcDoACzQw41HXfHrfeuFJNwfNvF38msJYXCjomdPKAsYqc28Nj?cluster=devnet) и [вывод](https://explorer.solana.com/tx/55Dk6uUCPt9vg7bZHcjEQjFEvoxfhbmgiE1UYVWeW6M8tXgKZeP86CgUdATAohS3gs1nHFpfUHYEHZTBGB64E3wp?cluster=devnet). Также проверил: без кошелька действия не выполняются, ноль внести нельзя, вывод заблокирован, пока открыта позиция, и снова работает после её закрытия. Для автоматического прогона есть `test_live.py` (Playwright), он подписывает транзакции тестовым ключом из `ANCHOR_WALLET`.

## Проект

Учебная работа Эмира Яппарова (DS). Программа, веб-интерфейс, README и тесты выполнены индивидуально.
