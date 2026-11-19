# Неделя 11: свой пул Raydium CLMM

Яппаров Эмир DS

В Solana Devnet созданы два тестовых SPL-токена с 6 знаками после запятой и выпущен миллион каждого. Для пары создан CLMM-пул со стартовой ценой 1:1, шагом тика 60 и комиссией 0,25%. Контракт vault не менялся. Ликвидность пока нулевая: на этой неделе требовалось только создание пула.

- [Пул в Explorer](https://explorer.solana.com/address/5d9XKBYg3VJkZjYsyCpWyfTht8KTipWLRhnPgDPrUMac?cluster=devnet)
- [Транзакция создания пула](https://explorer.solana.com/tx/CJhPVguSBLEEeq3vpqFHX5rYYiidVGP6WfjETxcARWDZfJC3DwwjBoyQcc6A91uXJzDh3KHuQPRxoJ6yqNPwYCw?cluster=devnet)
- [Транзакция выпуска токенов](https://explorer.solana.com/tx/5LqHrXQV922pnzZMhhNd3bnYwm8hDG9cDGF83fnrCkwuob2N9CptmudhgaLXPumkywYRDsiXkGqBc1Pb3hmjn3MP?cluster=devnet)
- Публичные адреса: [`evidence/devnet-pool.json`](evidence/devnet-pool.json)

`npm ci --ignore-scripts` устанавливает зависимости. `npm test` проверяет, что код принимает Devnet и не допускает Mainnet. `npm run verify` читает Devnet и сверяет обе подтверждённые транзакции, программу-владельца пула, токены, цену и комиссию. Для этой проверки кошелёк не нужен.

Для создания нового пула укажи в `ANCHOR_WALLET` путь к отдельному тестовому кошельку с балансом Devnet и запусти `npm run create-pool`. Повторный запуск в том же каталоге не отправляет транзакции, если уже сохранён локальный `devnet-pool.json`. Не передавай приватный ключ в репозиторий.

Условие: [шаблон курса, неделя 11](https://github.com/0xnurda/vault-dev/tree/fe2adcf7385866e6f585e69e719979ba423640ec#неделя-11--свои-токены-и-свой-clmm-пул-на-raydium).
