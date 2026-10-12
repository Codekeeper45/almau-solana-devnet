# Глава 8: Liquidity Vault

Яппаров Эмир DS

## Что реализовано

Anchor-программа с двумя инструкциями:
- `create_vault`: создаёт конфигурацию, PDA authority, share mint и token vault для базового SPL токена.
- `open_position`: создаёт PDA позиции пользователя с нулевым deposited_amount.

Это каркас главы 8. Депозиты, вывод, выпуск долей при депозите, swaps и Raydium/CLMM относятся к следующим этапам и здесь не реализованы.

## Итоговый результат

Программа размещена в Solana Devnet: `Xu7JJXtKWyA1LfNpc1tcCNfEiZJQQYWn5Ymo96j9vHa`.

[Программа в Explorer](https://explorer.solana.com/address/Xu7JJXtKWyA1LfNpc1tcCNfEiZJQQYWn5Ymo96j9vHa?cluster=devnet)

Обе инструкции выполнены в публичной Devnet. Подписи, созданные адреса и ответы RPC находятся в `evidence/manifest.json`, `evidence/create_vault.json` и `evidence/open_position.json`. После create_vault конфигурация содержит администратора, базовый mint, share mint и total_deposited=0. После open_position позиция связана с пользователем и конфигурацией, deposited_amount=0.

## Проверка

```sh
python3 tests/verify_scaffold.py
```

Это четыре проверки структуры исходника, не Anchor integration tests. Байт-код получен облачной SBF-сборкой; публичный deployment и вызовы подтверждены RPC. Локальная Anchor-сборка не заявляется. `evidence/vault.so` содержит размещённый байт-код.

## Архитектура

```text
admin
  config PDA [config, admin]
    authority PDA [vault-authority, config]
      share mint PDA [share, config]
      token vault PDA [token-vault, config]
    position PDA [position, config, user]
```

Seed-строки выбраны для этой реализации. Работа подготовлена по методичке; обещанный преподавателем шаблон на момент подготовки ещё не опубликован в просмотренных сообщениях.

## Документы

PDF и DOCX находятся в `reports/`. Ключи кошелька и секреты не публикуются. Только тестовая Devnet, без реальных средств. Повторное выполнение create_vault/open_position на тех же PDA завершится ошибкой уже существующего аккаунта, поэтому для проверки использованы сохранённые транзакции и чтение RPC.
