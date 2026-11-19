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

## Результат 13-й недели в Devnet

[Обновление vault](https://explorer.solana.com/tx/5uUkRjM2ufzFHMV2Gd46Kg1taUs5hescdvxiNNsVRishrPefMYxEZ5qQo1syqm2WkjcJ4afFBtJPg1YtqwrxBVEB?cluster=devnet) прошло; байты программы в сети совпали с локальным бинарником после `llvm-strip --strip-unneeded`.

- [Открытие](https://explorer.solana.com/tx/c8jJ7hoqm9bb6m9yo6Rt4CB2XzesXwYAv8fvkZPL3y9uqUjRrMZEwe4ncTYawh6FbpiJGsW8bPEPSQhvwUKrXKD?cluster=devnet): тики от −660 до 540. Vault внёс 7,033424 A и 7,741458 B. NFT принадлежит PDA. На счетах vault не осталось делегата.
- После трёх обменов с другого кошелька vault [собрал комиссии](https://explorer.solana.com/tx/3GzSHd1pJq3Nj5jeUNSH6FarxJLuc8aYv9vmxELbyKBb8BbjcDYYWrQds3s6oiRLbzs8vKw7vji1SDDFHLwQ1VrC?cluster=devnet): 0,000907 A и 0,000259 B.
- При [закрытии](https://explorer.solana.com/tx/w69Zzo6SXBpNWfpDcFmVNcgS9NQQHJk3355BnsuPmyCfnhwyPEofwcjQNbmi8xAWzYtjY7N1Qh86dhmjq8GZvFY?cluster=devnet) вернулись 7,340743 A и 7,435431 B. NFT и аккаунт позиции закрыты.
- Для ребалансировки цена опустилась до тика −251 и вышла из диапазона от −180 до 60. Vault закрыл узкую позицию и [открыл новую](https://explorer.solana.com/tx/SYngzDndQoRAsYTfmPpUn58dyiKkHSNNKWSYSnVW1vJdy16xk9EfS1hkwkqa7fRmhDJ4zoXmBYPLhmwYBxSddLL?cluster=devnet) в диапазоне от −900 до 300, который включает текущую цену. Новая тестовая позиция осталась открытой.

Все подписи транзакций и суммы в минимальных единицах: [`devnet-weeks12-13.json`](../08-week11-clmm/evidence/devnet-weeks12-13.json).
