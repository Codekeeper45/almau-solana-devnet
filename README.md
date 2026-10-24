# AlmaU: Solana Devnet

Яппаров Эмир DS

Три самостоятельные работы:
- [Задания 1-6](01-weeks-1-6): кошелёк, анализ транзакций, Rust CLI, native program, Anchor Counter и PDA profile. Итог: три executable программы; Counter count=2; профиль emir_ds / AlmaU 3 course.
- [Практика 12 октября](02-token-practice): Memo-перевод, SPL mint, mint/burn и переводы трём однокурсникам. Итог: выпуск 9950, баланс автора 9650, три перевода по 100.
- [Глава 8: Liquidity Vault](03-liquidity-vault): create_vault и open_position. Итог: программа размещена, вызовы выполнены; total_deposited=0, deposited_amount=0.

В каждом каталоге исходники, доказательства и reports с PDF/DOCX. Только Devnet. Ключи не публикуются. Практика выполнена через Python/solders; TypeScript/Helius и metadata не заявляются. Для vault выполнены облачная SBF-сборка и публичные транзакции, не локальные Anchor integration tests.


## Неделя 9

[05-week9-deposits](05-week9-deposits/): комиссия 1%, минимальный депозит, административная пауза и проверка shares трёх вкладчиков. Скомпилированный SBF проверен в LiteSVM с SPL Token CPI, 19 сценариев. Публичный Devnet-деплой новой версии не заявляется. Отчёт PDF/DOCX и логи находятся в каталоге работы.

## Обновление недели 8

Актуальная работа по опубликованному шаблону преподавателя и трём расширениям находится в [04-week8-official](04-week8-official/). Предыдущий 03-liquidity-vault сохранён как ранняя самостоятельная реализация, не заменяет новый шаблон.
