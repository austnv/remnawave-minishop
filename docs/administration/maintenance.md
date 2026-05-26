# Обслуживание

Плановое обслуживание обычно сводится к обновлению образов, проверке миграций, логов и резервных копий PostgreSQL.

## Обновление

```bash
docker compose pull
docker compose up -d
docker compose logs -f migrate backend worker
```

## Резервная копия PostgreSQL

```bash
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > backup.sql
```

## Проверки после работ

- `docker compose ps`
- `docker compose logs -f backend worker frontend`
- `/healthz` на backend-домене
- вход в Mini App и админку
- тестовый платеж или тестовая активация

## Синхронизация GitLab-зеркала

Основное место работы - GitHub remote `origin`. GitLab remote `gitlab` используется как запасное зеркало.

После пуша в GitHub синхронизируйте зеркало:

```bash
bash scripts/sync-gitlab-mirror.sh
```

PowerShell-вариант:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-gitlab-mirror.ps1
```

По умолчанию скрипт делает `git fetch origin --prune --tags`, пушит все ветки из `origin/*` в `gitlab` и пушит теги. Он не удаляет ветки в GitLab и не делает force-push. Для строгого зеркалирования доступны флаги:

```bash
bash scripts/sync-gitlab-mirror.sh --force --prune
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-gitlab-mirror.ps1 -Force -Prune
```

Перед опасными режимами можно посмотреть команды без выполнения:

```bash
bash scripts/sync-gitlab-mirror.sh --force --prune --dry-run
```

Подробности: [развертывание](../deployment.md) и [логи](../troubleshooting/logs.md).
