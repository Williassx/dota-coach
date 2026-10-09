# Поведенческие проверки

[Подпункт](../README.md) · [orders.test.cjs](orders.test.cjs)

Из корня репозитория:

```sh
node --test creators/creator-2/02-coach-interface/02-status-orders/tests/orders.test.cjs
```

Реальные игровые JS выполняются в Node VM с моделью Panorama. Проверяются режимы,
адресаты, стадии/неопределённость, версии и cleanup. Игровые API перехватываются;
настоящая отправка, серверная авторизация и рендеринг не проверены.
