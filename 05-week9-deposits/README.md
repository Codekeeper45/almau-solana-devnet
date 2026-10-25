# Неделя 9. Депозит и share-токены

Яппаров Эмир DS

Условия: https://github.com/0xnurda/vault-dev/tree/students-vault-card, раздел «Задания для практики». Преподаватель объявил обновление 21.10.2026: https://t.me/c/4381437854/195. Методическое руководство: методичка из Telegram (сообщение 168), раздел «09 Депозит и share-токены».

## Реализация

Контракт принимает SPL-токен и выпускает shares. Из суммы депозита удерживается 1% в пользу закреплённого при создании vault токен-аккаунта fee_wallet. Shares начисляются только на чистую сумму. Комиссия округляется вниз в минимальных единицах токена.

Первый депозит: shares = net. Следующие: shares = net * total_shares / total_tokens. Для промежуточного умножения используется u128, для счётчиков checked_add.

Минимальный депозит равен одному целому токену: 10^decimals минимальных единиц. Администратор управляет paused через set_paused. Посторонний пользователь не может менять паузу. При паузе запрещены депозиты и создание карточек. Карточка сохраняет created_at; закрытие с активными shares запрещено, чтобы не потерять учёт позиции.

fee_wallet нельзя подменить при депозите. Проверяются mint и владелец пользовательских токен-аккаунтов, адреса PDA и связь карточки с пользователем и vault.

## Проверено в Solana Devnet

Программа развёрнута в официальной сети Solana Devnet (BPFLoaderUpgradeable), инициализирована и протестирована реальной транзакцией депозита:

- **Program ID:** [`A3wEuZYxJDy5kENCvsEj7JjcjjX4Ejm5nxhQVuXHzeud`](https://explorer.solana.com/address/A3wEuZYxJDy5kENCvsEj7JjcjjX4Ejm5nxhQVuXHzeud?cluster=devnet)
- **Token Mint:** [`4oDpT49f5SEzjU69vef2ZtoHfs21ydy72EnvrvJzLp2n`](https://explorer.solana.com/address/4oDpT49f5SEzjU69vef2ZtoHfs21ydy72EnvrvJzLp2n?cluster=devnet)
- **VaultState PDA:** [`6BKdhJi4cdsZK7PhSoEAmrKnqKrhpsRxJACqKKpG38SU`](https://explorer.solana.com/address/6BKdhJi4cdsZK7PhSoEAmrKnqKrhpsRxJACqKKpG38SU?cluster=devnet)
- **Vault Token Account PDA:** [`8jouRqaj3KuNbPDLfiCdb8MeF5JUiYXXDmLLTHDTpgA1`](https://explorer.solana.com/address/8jouRqaj3KuNbPDLfiCdb8MeF5JUiYXXDmLLTHDTpgA1?cluster=devnet)
- **Share Mint PDA:** [`7FpUfUcVV7giFVVbpBY4bqyEZVx42izxcnjdv7QkMpUc`](https://explorer.solana.com/address/7FpUfUcVV7giFVVbpBY4bqyEZVx42izxcnjdv7QkMpUc?cluster=devnet)
- **User Card PDA:** [`2tH5xuNuFcmLgQLc39prCD6uViNw1RgSPAqWGKnsjY9h`](https://explorer.solana.com/address/2tH5xuNuFcmLgQLc39prCD6uViNw1RgSPAqWGKnsjY9h?cluster=devnet)

### Транзакции в Explorer:
1. **Инициализация хранилища (initialize_vault):**
   [`nk4euN3Zf11jYuWkFJBdEtxArJgWYaxEqS8CfjuX1zsuDXaLNHF1LZ5qgACnqtk4mZ4hVLL9FQzkMFiLzmp8FMy`](https://explorer.solana.com/tx/nk4euN3Zf11jYuWkFJBdEtxArJgWYaxEqS8CfjuX1zsuDXaLNHF1LZ5qgACnqtk4mZ4hVLL9FQzkMFiLzmp8FMy?cluster=devnet)
2. **Создание карточки пользователя (create_user_card):**
   [`3Ntz93JQBiuK9qTSWeJY75a1TfxvJm85EFaxSq2tQiVbKkNxgLMbdg5SMdW8DomD7rYWPFe8fd9FWRVzUULiLaD6`](https://explorer.solana.com/tx/3Ntz93JQBiuK9qTSWeJY75a1TfxvJm85EFaxSq2tQiVbKkNxgLMbdg5SMdW8DomD7rYWPFe8fd9FWRVzUULiLaD6?cluster=devnet)
3. **Реальный депозит (deposit):**
   [`4EsAmwBdCgHdkZaKmnTb2MVFdoeLvjqtwSyh1jDGtPkZxzdRnatEXMiVyugfNLK9UmxCWSgCRmfyJ5qhU2LMzLCJ`](https://explorer.solana.com/tx/4EsAmwBdCgHdkZaKmnTb2MVFdoeLvjqtwSyh1jDGtPkZxzdRnatEXMiVyugfNLK9UmxCWSgCRmfyJ5qhU2LMzLCJ?cluster=devnet)

Параметры транзакции депозита:
- Внесено пользователем: 100 токенов (100 * 10^6).
- Удержана комиссия 1%: 1 токен (переведён на fee_wallet).
- Зачислено в пул хранилища: 99 токенов.
- Выпущено и зачислено пользователю: 99 share-токенов.

### Вопросы для самопроверки из методички:
- **Почему поздний вкладчик может получить share-токенов меньше, чем внёс токенов?**
  Потому что если пул заработал прибыль (доход от торговли или комиссий), общая стоимость активов в vault (`total_tokens`) возрастает относительно неизменного количества долей (`total_shares`). Каждый существующий share-токен обеспечен большим количеством базовых токенов. Новый вкладчик покупает долю по возросшей цене, чтобы не размывать прибыль первых участников.
- **Почему перевод подписывает пользователь, а выпуск share-токенов — программа?**
  Базовые токены принадлежат личному аккаунту пользователя, поэтому списать их со счёта может только владелец своей криптографической подписью. Выпуск (mint_to) share-токенов контролируется логикой протокола: авторитетом share_mint назначен PDA программы (`vault_state`), поэтому программа подписывает выпуск через Cross-Program Invocation (CPI) с программными сидами.
- **Какие программы участвовали в транзакции депозита?**
  В транзакции участвовали две программы: наша программа хранилища `Simple Vault` (`A3wEuZYxJDy5kENCvsEj7JjcjjX4Ejm5nxhQVuXHzeud`) и системная программа токенов `SPL Token Program` (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`), вызываемая через CPI для трансфера и минта.

## Локальная регрессия (LiteSVM)

Скомпилированный SBF исполняется также в LiteSVM с настоящими CPI в SPL Token.
Команда запуска:
```bash
python test_svm.py
```
Проверены 19 сценариев:
- Создание vault и карточек пользователей.
- Запрет депозита без карточки пользователя.
- Запрет нулевого депозита и депозита ниже минимума (1 токен).
- Управление флагом паузы администратором и отказ при попытке паузы посторонним.
- Блокировка депозитов и создания новых карточек во время паузы.
- Запрет подмены fee_wallet и чужого share-аккаунта.
- Три последовательных депозита трёх пользователей (100, 200, 300 токенов), начисление долей 1/6, 1/3, 1/2 и удержание 1% комиссии.
- Запрет закрытия карточки с ненулевым балансом долей.
- Откат состояния при превышении баланса.
Все 19 сценариев успешно пройдены.
