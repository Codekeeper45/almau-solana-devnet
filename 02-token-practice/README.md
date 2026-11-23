# Практика 12 октября: SPL-токен

Яппаров Эмир DS

Делал по примеру лектора: https://github.com/0xnurda/solana-practice. Всё в Devnet, мой скрипт — `lecture_practice.py`.

1. Перевёл 0,01 SOL с memo «Hello Solana»: [транзакция](https://explorer.solana.com/tx/4WSdRV5fMGUUpXLv3k2wn9C2GiZka4TqRV3v5yuacZDrEt7PezKnCGMrE6pDW8xCtdvfTFqDEyVBwobU8uc3eiJf?cluster=devnet).
2. Создал свой SPL-токен: mint [`HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe`](https://explorer.solana.com/address/HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe?cluster=devnet), 6 знаков после запятой. Выпустил 10 000 токенов и сжёг 50.
3. Отправил по 100 токенов трём однокурсникам:
   - `8sJ49ZVUw8QXfxogwHRkXC1nfm6ZT7vrTWwq6xztBkVV`: [транзакция](https://explorer.solana.com/tx/2pMVPGVwFUZppkmZFXvZuRbwnyGvHWQ5vwfqdUfGwPDoEchqChvu8JxvBqA1cXxmVJFvDagKipESixVtDgDb46sm?cluster=devnet)
   - `DRx11A6yZPoJXvFmwbu9posT1RN5GmW4f6J25PJADHbv`: [транзакция](https://explorer.solana.com/tx/251HzPCTEXbAZFMcLkWMAzzZ8XyeLHVKWJFzwsmd5pBK2iXn5CnSdvuKkZ7kQSW19ZLnQkv6grXED3Dkf1HU6PRC?cluster=devnet)
   - `HMwMf283jQjEPafskVa8kLSTANpDHQW8MmTp2C9UtzYX`: [транзакция](https://explorer.solana.com/tx/3gvqerjTnctGxwVS8vYUi1DAVndYJCjSKPsjHJuRZwU8x46HAVVynSJ59ZEAcz372KamexxHaxCoaJWm8w6f9Whh?cluster=devnet)

В итоге у меня осталось 9 650 токенов, всего выпущено 9 950.

Название MYCOIN, как и у лектора, есть только в коде. Метаданные токена (имя, символ, картинка) я сделал отдельно на неделе 7: `06-week7-metadata`.
