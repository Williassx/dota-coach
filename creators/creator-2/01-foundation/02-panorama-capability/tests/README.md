# Проверки поведения диагностической панели

[Подпункт](../README.md). Node.js 18+ и встроенные node:test/vm, без npm-пакетов.
Исполняются настоящие игровые JS; только GameEvents, Panel и Schedule заменены
моделью недоступного движка. Это не рендеринг, компиляция Source 2 или сервер Lua.

```sh
node --test creators/creator-2/01-foundation/02-panorama-capability/tests/*.test.cjs
```
