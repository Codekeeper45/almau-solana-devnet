# Week 7: SPL Token + on-chain metadata (Devnet)

Яппаров Эмир DS

Задание недели 7: создание SPL-токена, выпуск (mint), создание аккаунта метаданных (Metaplex Token Metadata) в сети Solana Devnet.

## Проверено в Solana Devnet

Токен и метаданные успешно созданы и зафиксированы ончейн:

- **Mint:** [`G77KQEeVfvh1zbF9pBkH71iEbyEYkMvZhBCsGUeA44fe`](https://explorer.solana.com/address/G77KQEeVfvh1zbF9pBkH71iEbyEYkMvZhBCsGUeA44fe?cluster=devnet)
- **Metadata Account:** [`F5xsxQN9j5MJmX4D5ogA81Die6SU9eADGCc6NPW4ABb2`](https://explorer.solana.com/address/F5xsxQN9j5MJmX4D5ogA81Die6SU9eADGCc6NPW4ABb2?cluster=devnet)
- **Metadata Program:** [`metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s`](https://explorer.solana.com/address/metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s?cluster=devnet) (Metaplex Token Metadata)
- **Token Account (ATA):** [`HuqjbCKhMMtd7eZzX2eBF6pWRH7AGGBk2Z1UNXoCJa9E`](https://explorer.solana.com/address/HuqjbCKhMMtd7eZzX2eBF6pWRH7AGGBk2Z1UNXoCJa9E?cluster=devnet)
- **Metadata URI:** https://raw.githubusercontent.com/Codekeeper45/almau-solana-devnet/main/06-week7-metadata/metadata.json

### Транзакции в Explorer:
1. **Создание и инициализация Mint:**
   [`2tcfj9aRe7a4YF16RpkQgUB7nhU2vst4ChoXfREEQA33C9Fizxhkn6VyBsNuexiofVBRhJiwhbgjFCsrBtRLbcDY`](https://explorer.solana.com/tx/2tcfj9aRe7a4YF16RpkQgUB7nhU2vst4ChoXfREEQA33C9Fizxhkn6VyBsNuexiofVBRhJiwhbgjFCsrBtRLbcDY?cluster=devnet)
2. **Создание ассоциированного токен-аккаунта (ATA):**
   [`4oY2ut5cALfkaaHEbmS4RDUAR3Pyjh2Fjz7SYjJfZVcXYoVd4BDt1vaia2CtVowQn4bq7rcxd5z3DG1QxMAHunVM`](https://explorer.solana.com/tx/4oY2ut5cALfkaaHEbmS4RDUAR3Pyjh2Fjz7SYjJfZVcXYoVd4BDt1vaia2CtVowQn4bq7rcxd5z3DG1QxMAHunVM?cluster=devnet)
3. **Эмиссия токенов (MintTo 1,000 токенов):**
   [`guyH4rnv1ViYpu8VVFzppdBzGfzCJFtXVyGESdbWf6S4LChpcW6YoW85XDDHzVjN2NfXGNAgqFQXZbPmkPfwRnk`](https://explorer.solana.com/tx/guyH4rnv1ViYpu8VVFzppdBzGfzCJFtXVyGESdbWf6S4LChpcW6YoW85XDDHzVjN2NfXGNAgqFQXZbPmkPfwRnk?cluster=devnet)
4. **Создание ончейн-метаданных (CreateMetadataAccountV3):**
   [`3WHTfuPWphSSXDpCMfEpUf3LmJgjwVnYNCSCp6axf546UyaCEFajqaXMGsdJEFdidPhbCB7Npak85UgsB1acPbuw`](https://explorer.solana.com/tx/3WHTfuPWphSSXDpCMfEpUf3LmJgjwVnYNCSCp6axf546UyaCEFajqaXMGsdJEFdidPhbCB7Npak85UgsB1acPbuw?cluster=devnet)

Файл свидетельств: `evidence/week7-devnet.json`. Все критерии полностью подтверждены через RPC.
