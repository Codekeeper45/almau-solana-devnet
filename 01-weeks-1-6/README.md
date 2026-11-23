# Задания 1–6

Яппаров Эмир DS

Всё сделано в Solana Devnet с моего кошелька [`2SzJ2P…`](https://explorer.solana.com/address/2SzJ2PSuhnQsenfvHK4DhQHibjVL2d68fwdHAMwxJ7pL?cluster=devnet).

## 1. Кошелёк и первая транзакция

Создал кошелёк, получил тестовые SOL и отправил 0,001 SOL на второй свой адрес `AK3KTt…`.

[Перевод в Explorer](https://explorer.solana.com/tx/ri4caYoSbLVQRkMdYdZhwJw7kNdvRT9fF27HzraFb1Y6Bu4mHriXJEZMT64uq84hauKyhKd8ZbfyMHGVVXCKhhV?cluster=devnet). В транзакции одна инструкция System Program `transfer`, подписывает и платит комиссию мой кошелёк, комиссия 5000 lamports.

## 2. Transaction Detective

Разбор двух чужих транзакций Devnet: [WEEK2.md](WEEK2.md).

## 3. CLI на Rust

`rust-cli` — консольная утилита: проверяет адреса и подписи в Base58 и запрашивает баланс через JSON-RPC Devnet. Внутри структуры, enum для команд и ошибок, `match`, обработка ошибок через `Result` и 5 тестов.

```sh
cargo test --manifest-path rust-cli/Cargo.toml
cargo run --manifest-path rust-cli/Cargo.toml -- balance 2SzJ2PSuhnQsenfvHK4DhQHibjVL2d68fwdHAMwxJ7pL
```

## 4. Первая программа

`programs/first-program` — нативная программа на `solana-program`. Если в данных инструкции байт `0`, она пишет приветствие в лог, иначе возвращает `InvalidInstructionData`.

- Program ID: [`FeZzxWVqYBu7KTBqFCJZTD1m2XwnYoYsFfZa8VwtoZfS`](https://explorer.solana.com/address/FeZzxWVqYBu7KTBqFCJZTD1m2XwnYoYsFfZa8VwtoZfS?cluster=devnet)
- [Деплой](https://explorer.solana.com/tx/3ZM4KnmTQmVCdAsQvsKRkUYcCyzcnrdGBv5HEUwy99jR1wKjh3ZLv6a82EaDqsFuLy96VVJF4KE7WfvLYKkwXcPj?cluster=devnet), [вызов](https://explorer.solana.com/tx/4Zrww4DbNSGJbGhf3Zo29dczAJreqZMAjJvKb9vu2NU5Av1oqFxL2fBgmM6ejEMYmu5SwySv2du832Y8goqvS9aq?cluster=devnet). В логах вызова: `Program log: Hello from Emir's first Solana program!`

## 5. Счётчик на Anchor

`programs/anchor-counter`: инструкции `initialize`, `increment`, `decrement`. Менять счётчик может только владелец (`has_one = authority`), переполнение и уход в минус ловятся через `checked_add` / `checked_sub`.

- Program ID: [`BPj5PmjBAaCB2W5MYTiRip3ktFYNgWSUmHKNhzQmySVD`](https://explorer.solana.com/address/BPj5PmjBAaCB2W5MYTiRip3ktFYNgWSUmHKNhzQmySVD?cluster=devnet)
- Аккаунт счётчика: [`icXS1KBhLXqqQPAQxvknnebQHn9Nbnj5HSWiaPsT6mp`](https://explorer.solana.com/address/icXS1KBhLXqqQPAQxvknnebQHn9Nbnj5HSWiaPsT6mp?cluster=devnet), сейчас `count = 2`.
- [Деплой](https://explorer.solana.com/tx/3E7TN85HXj3js6JFzBWgtRfPKoDa7hBXRncQEvPhy1ri588k12eoywjiLkr3uX77QCGZ68PKm3t6qnfDpTnKo9d?cluster=devnet), [initialize](https://explorer.solana.com/tx/2CFzeFGoz77eE6VnDvjZGiAjB5Z2WsgAP7bBH6hr7qerMTDEDeUZca5eS2N3mF5WwAjMssPd3hrKGZum5o4YK7PL?cluster=devnet), [increment](https://explorer.solana.com/tx/43CADxS9ofqGdVq1siJvW791X1agmwW4Biktm2bqHBZJntLPcvZkB6m6PyAmdismWkSwgubNUdpLTm4kpzM8zCJJ?cluster=devnet), [increment](https://explorer.solana.com/tx/2brbEWY3kFDWP47aDYvYgz2DHqxEhnkc1wiaipnQ6aV8gBtNmGsX23ueHmta77N6sRTsS39oWdJ6ysp3GctbSX8P?cluster=devnet).

`clients/solana_client.py` считает дискриминатор инструкции (первые 8 байт sha256 от `global:increment`) и читает аккаунт счётчика по схеме Borsh.

## 6. Профиль на PDA

`programs/pda-profile`: `create_profile` и `update_profile`. Адрес профиля — PDA из seeds `["profile", authority]`, bump сохраняется в аккаунте. Изменить профиль может только владелец. Имя до 32 байт, описание до 160.

- Program ID: [`22NbKaaD3vLDEAi3jxM9FzwJdAJXR5kBzSmfq2mJi7AM`](https://explorer.solana.com/address/22NbKaaD3vLDEAi3jxM9FzwJdAJXR5kBzSmfq2mJi7AM?cluster=devnet)
- Профиль: [`5LzZuesGoaUX2jdZdZu284FTu5CrWyhcbEXp3JGtmVmA`](https://explorer.solana.com/address/5LzZuesGoaUX2jdZdZu284FTu5CrWyhcbEXp3JGtmVmA?cluster=devnet), username `emir_ds`, bio `AlmaU 3 course`.
- [Деплой](https://explorer.solana.com/tx/62cvCyPwy1VEwinwcJ6gg8hk8FVUqA9s3WUVfJnNEYg83Ub23M3fqYJXyVvpxw5CmBMjApnbzx5tgAbJXSJJsj79?cluster=devnet), [create_profile](https://explorer.solana.com/tx/2XFZZtGRb1prEeBYW9nxCNPmRhMAA7c88fYCCa7Tp5wd4AZQJshkq3HnJqwCzenWZMww822Y3cRuNuUCBH5Vrax4?cluster=devnet), [update_profile](https://explorer.solana.com/tx/2y6f4a2MuejYPVjprc7uyNSGD4spn2skeM54qgcYMMdpLM43yDuQ9WdxYgjZ2QiqhZqrGm9NBppgvzWXz5jzsC2T?cluster=devnet).

Тот же отчёт в PDF и DOCX лежит в `reports/`.
