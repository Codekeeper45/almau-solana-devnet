Яппаров Эмир DS

Практика лектора от 12 октября 2026

Источник: https://github.com/0xnurda/solana-practice, Telegram сообщение 164.

В Devnet выполнен перевод 0.01 SOL с Memo Hello Solana на собственный тестовый адрес.

Создан SPL mint HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe, decimals=6. Выпущено 10000 единиц, сожжено 50.

Трём однокурсникам отправлено по 100 токенов:

8sJ49ZVUw8QXfxogwHRkXC1nfm6ZT7vrTWwq6xztBkVV

https://explorer.solana.com/tx/2pMVPGVwFUZppkmZFXvZuRbwnyGvHWQ5vwfqdUfGwPDoEchqChvu8JxvBqA1cXxmVJFvDagKipESixVtDgDb46sm?cluster=devnet

DRx11A6yZPoJXvFmwbu9posT1RN5GmW4f6J25PJADHbv

https://explorer.solana.com/tx/251HzPCTEXbAZFMcLkWMAzzZ8XyeLHVKWJFzwsmd5pBK2iXn5CnSdvuKkZ7kQSW19ZLnQkv6grXED3Dkf1HU6PRC?cluster=devnet

HMwMf283jQjEPafskVa8kLSTANpDHQW8MmTp2C9UtzYX

https://explorer.solana.com/tx/3gvqerjTnctGxwVS8vYUi1DAVndYJCjSKPsjHJuRZwU8x46HAVVynSJ59ZEAcz372KamexxHaxCoaJWm8w6f9Whh?cluster=devnet

Повторное чтение RPC: собственный баланс 9650, общий выпуск 9950. Все три перевода проверены через getTransaction: meta.err=null.

Примечание: выполнено через Python/solders с теми же инструкциями System, Memo, SPL Token и Associated Token. Полная установка TypeScript/Anchor/Helius не заявляется.

Как в коде лектора, имя MYCOIN существует только в тексте: on-chain metadata не создавалась. Это отчёт по текущему примеру лектора, не полное закрытие недели 7 силлабуса, где metadata требуется отдельно.