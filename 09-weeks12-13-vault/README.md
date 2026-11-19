# Solana: недели 12 и 13

Яппаров Эмир DS

[Пул Raydium CLMM в Devnet](https://explorer.solana.com/address/5d9XKBYg3VJkZjYsyCpWyfTht8KTipWLRhnPgDPrUMac?cluster=devnet) создан на неделе 11. Для обменов в пул добавлена [тестовая ликвидность](https://explorer.solana.com/tx/2nCiKNsmAUuHfHRdEFpGcdBWZnUYv8mHaXc3icLWUhgKYQWpwNaNiFqM8ZaRSGRwnzG37PXNuiAgx3deHdg3guck?cluster=devnet). Это отдельная позиция кошелька, не позиция vault.

## Неделя 12: обмен

Vault хранит базовый и котируемый SPL-токены на двух счетах. Администратор может запустить обмен только в выбранном пуле. Расход токенов подписывает адрес программы (PDA), а не кошелёк администратора. Скрипт рассчитывает ожидаемый результат с помощью Raydium SDK, выставляет `min_out` с допуском 1% и показывает цену до обмена и после него. Если Raydium не может выдать минимум, вся транзакция откатывается.

## Неделя 13: позиция

Администратор выбирает тики и максимальный расход каждого токена. NFT позиции принадлежит PDA vault. `collect_fees` вызывает Raydium с нулевым выводом ликвидности, поэтому в vault возвращаются только накопленные комиссии. Для закрытия скрипт в одной транзакции выводит остаток ликвидности с проверкой минимальных сумм и закрывает позицию. В учебной версии депозит и вывод заблокированы, пока открыта позиция или vault держит котируемый токен.

## Запуск

Из этого каталога: `cargo build --locked --target sbpf-solana-solana --release` (Anza platform-tools). Клиентский код и зависимости находятся в `../08-week11-clmm/`. Переменные `ANCHOR_WALLET` и `PROGRAM_KEY` указывают на отдельные локальные файлы ключей Devnet; их нельзя добавлять в Git. `run-vault-devnet.mjs --week12` останавливает сценарий после проверки swap; запуск без флага проверяет и позицию. Скрипты проверяют genesis сети до подписи транзакций.

## Результат 12-й недели в Devnet

[Деплой vault](https://explorer.solana.com/tx/4v8NjFXX3orJ8VE6P3a7jUPv2RvpLs9ktU9WYuYjphthCSTB7ir558tpD8XSJbmvoSS4hMTQAFV7TJ4JqKv6oWye?cluster=devnet) финализирован. Байты программы в сети сверены с локальной сборкой.

- [Успешный обмен](https://explorer.solana.com/tx/DhyYy6V221h196MemMStov6YzxgHUZuF1sLezmhviYzvb2d6q9Uvz2oWEv5hZg6PydTowSdFYD9Yxgsgp23f5j8?cluster=devnet): отдали 30 токенов A, получили 29,880291 токена B при минимуме 29,581488. Цена пула изменилась с 1 до 0,9970142029182 B за A.
- [Отклонённый обмен](https://explorer.solana.com/tx/3qTuiHcrUk2HUnKpSd6JKpTHQNms4bLz7dbVzuMbY2oEDFVJCmEhgbTKr4hhmX4vqQUGcTWWqoSJ2KEMFQPnvLHd?cluster=devnet): Raydium отклонил завышенный минимум, балансы токенов vault не изменились.
- [Попытка обмена без прав администратора](https://explorer.solana.com/tx/W82bbmx7vG6ubKCNuvj8P2PDpepwG1az8RaxoSaYN5sDo584icbUUWmFTQAQRmk6QDFaW4Q7XWEriwNoWM4di8Q?cluster=devnet): vault отклонил вызов.

Полный сценарий 13-й недели ещё проверяется.
