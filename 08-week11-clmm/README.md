# Неделя 11: свой пул Raydium CLMM

Яппаров Эмир DS

В Solana Devnet созданы два тестовых SPL-токена с 6 знаками после запятой и выпущен миллион каждого. Для пары создан CLMM-пул со стартовой ценой 1:1, шагом тика 60 и комиссией 0,25%. Контракт vault на этой неделе не менялся.

- [Пул в Explorer](https://explorer.solana.com/address/5d9XKBYg3VJkZjYsyCpWyfTht8KTipWLRhnPgDPrUMac?cluster=devnet)
- [Транзакция создания пула](https://explorer.solana.com/tx/CJhPVguSBLEEeq3vpqFHX5rYYiidVGP6WfjETxcARWDZfJC3DwwjBoyQcc6A91uXJzDh3KHuQPRxoJ6yqNPwYCw?cluster=devnet)
- [Транзакция выпуска токенов](https://explorer.solana.com/tx/5LqHrXQV922pnzZMhhNd3bnYwm8hDG9cDGF83fnrCkwuob2N9CptmudhgaLXPumkywYRDsiXkGqBc1Pb3hmjn3MP?cluster=devnet)
- Публичные адреса: [`evidence/devnet-pool.json`](evidence/devnet-pool.json)

## Позиция и диапазон

Чтобы в пуле появилась ликвидность, открыл со своего кошелька одну позицию скриптом `seed-liquidity.mjs` (Raydium SDK V2):

- [Транзакция открытия позиции](https://explorer.solana.com/tx/2nCiKNsmAUuHfHRdEFpGcdBWZnUYv8mHaXc3icLWUhgKYQWpwNaNiFqM8ZaRSGRwnzG37PXNuiAgx3deHdg3guck?cluster=devnet)
- Позиция: [`D93iV2KQUDijXqMPdui2KoAYLGuzyd9fvz21RUxSmnvu`](https://explorer.solana.com/address/D93iV2KQUDijXqMPdui2KoAYLGuzyd9fvz21RUxSmnvu?cluster=devnet), NFT позиции: [`qKNJR8Vs69sHnLMW3NuoutUU3h6Ma5bgrunZaBHkXkw`](https://explorer.solana.com/address/qKNJR8Vs69sHnLMW3NuoutUU3h6Ma5bgrunZaBHkXkw?cluster=devnet)
- Текущая цена при открытии: 1 B за 1 A (тик 0).
- Диапазон: тики от −1020 до 960, то есть цена примерно от 0,903 до 1,101. Это около ±10 % от текущей цены.

Почему такой диапазон: оба токена тестовые, и цена должна держаться около 1. Запас ±10 % нужен, чтобы обмены на неделе 12 не вывели цену за границы. При этом диапазон не слишком широкий, и ликвидность не «размазывается» по ценам, до которых пул не дойдёт. Шаг тика у пула 60, поэтому границы кратны 60. Данные позиции — в [`evidence/devnet-seed-position.json`](evidence/devnet-seed-position.json).

`npm ci --ignore-scripts` устанавливает зависимости. `npm test` проверяет, что код принимает Devnet и не допускает Mainnet. `npm run verify` читает Devnet и сверяет обе подтверждённые транзакции, программу-владельца пула, токены, цену и комиссию. Для этой проверки кошелёк не нужен.

Для создания нового пула укажи в `ANCHOR_WALLET` путь к отдельному тестовому кошельку с балансом Devnet и запусти `npm run create-pool`. Повторный запуск в том же каталоге не отправляет транзакции, если уже сохранён локальный `devnet-pool.json`. Не передавай приватный ключ в репозиторий.

Условие: [шаблон курса, неделя 11](https://github.com/0xnurda/vault-dev/tree/fe2adcf7385866e6f585e69e719979ba423640ec#неделя-11--свои-токены-и-свой-clmm-пул-на-raydium).
