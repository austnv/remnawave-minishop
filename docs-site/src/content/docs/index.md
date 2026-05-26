---
title: "Remnawave Minishop"
description: "Документация по запуску, настройке и сопровождению Telegram Mini App для Remnawave."
template: splash
hero:
  tagline: "Telegram-бот и Mini App для продажи подписок Remnawave: платежи, тарифы, админка, поддержка и инструкции подключения."
  image:
    alt: Интерфейс Remnawave Minishop
    html: '<img src="/remnawave-minishop.webp" alt="Интерфейс Remnawave Minishop" width="900" height="520" loading="eager" decoding="async" />'
  actions:
    - text: Быстрый старт
      link: /reference/deployment/
      icon: right-arrow
    - text: Настройка
      link: /reference/configuration/
      icon: setting
      variant: minimal
---

## Основные разделы

- **Запуск и окружение** - минимальный `.env`, Docker Compose, reverse proxy, обновления и резервные копии.
- **Web App / Mini App** - Telegram-авторизация, email-вход, инструкции установки и публичные ссылки.
- **Админка и тарифы** - управление пользователями, платежами, темами, каталогом тарифов и premium-сквадами.
- **Миграция** - перенос со старого `remnawave-tg-shop` на текущую split-архитектуру.

## Быстрые ссылки

- [Развертывание](/reference/deployment/)
- [Переменные окружения](/reference/env-vars/)
- [Тарифы](/reference/tariffs/)
- [Темы Web App](/reference/webapp-themes/)
