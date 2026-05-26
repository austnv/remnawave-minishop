import { copyFile, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const repoRoot = path.resolve(siteRoot, '..');
const sourceDir = path.join(repoRoot, 'docs');
const outputDir = path.join(siteRoot, 'src', 'content', 'docs', 'reference');

const descriptions = {
  'admin.md': 'Возможности админ-панели, управление пользователями, настройками, тарифами и поддержкой.',
  'architecture.md': 'Краткая архитектура backend, frontend, worker и инфраструктурных сервисов.',
  'configuration.md': 'Минимальный .env, bootstrap-секреты и настройка через Web App админку.',
  'deployment.md': 'Docker Compose, reverse proxy, TLS, образы, обновления и резервные копии.',
  'env-vars.md': 'Полный справочник переменных окружения Remnawave Minishop.',
  'migration-to-minishop.md': 'Перенос данных со старого remnawave-tg-shop на split-архитектуру Minishop.',
  'support.md': 'Пользовательские тикеты, админский inbox, уведомления и лимиты поддержки.',
  'tariffs.md': 'Каталог тарифов, period/traffic-модели, premium-сквады и HWID-устройства.',
  'webapp.md': 'Telegram Mini App, авторизация, публичные инструкции и проксирование.',
  'webapp-themes.md': 'Кастомные темы, CSS-токены, ассеты и пайплайн создания темы.',
};

const imageExtensions = new Set(['.avif', '.gif', '.jpeg', '.jpg', '.png', '.svg', '.webp']);

function yamlString(value) {
  return JSON.stringify(value);
}

function slugFor(fileName) {
  return fileName.replace(/\.md$/i, '');
}

function extractTitle(fileName, content) {
  const match = content.match(/^#\s+(.+?)\s*$/m);
  return match?.[1] ?? slugFor(fileName);
}

function stripFirstHeading(content) {
  return content.replace(/^#\s+.+?\s*\r?\n+/, '');
}

function rewriteMarkdownLinks(markdown) {
  return markdown.replace(/\]\((?!https?:\/\/|mailto:|tel:|\/|#)([^)\s]+\.md)(#[^)]+)?\)/g, (match, target, hash = '') => {
    const slug = slugFor(path.posix.basename(target));
    return `](/reference/${slug}/${hash})`;
  });
}

function normalizeCodeFences(markdown) {
  return markdown
    .replace(/^```env\s*$/gim, '```ini')
    .replace(/^```caddyfile\s*$/gim, '```txt');
}

function frontmatter({ title, description, fileName }) {
  const editUrl = `https://gitlab.com/3252a8/remnawave-minshop/-/edit/main/docs/${encodeURIComponent(fileName)}`;
  return [
    '---',
    `title: ${yamlString(title)}`,
    `description: ${yamlString(description)}`,
    `editUrl: ${yamlString(editUrl)}`,
    '---',
    '',
  ].join('\n');
}

async function syncMarkdown(entries) {
  for (const entry of entries.filter((item) => item.name.endsWith('.md'))) {
    const sourcePath = path.join(sourceDir, entry.name);
    const content = await readFile(sourcePath, 'utf8');
    const title = extractTitle(entry.name, content);
    const body = normalizeCodeFences(rewriteMarkdownLinks(stripFirstHeading(content).trimStart()));
    const output = frontmatter({
      title,
      description: descriptions[entry.name] ?? title,
      fileName: entry.name,
    });

    await writeFile(path.join(outputDir, entry.name), `${output}${body}\n`, 'utf8');
  }
}

async function syncImages(entries) {
  for (const entry of entries.filter((item) => imageExtensions.has(path.extname(item.name).toLowerCase()))) {
    await copyFile(path.join(sourceDir, entry.name), path.join(outputDir, entry.name));
  }
}

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });

const entries = await readdir(sourceDir, { withFileTypes: true });
await syncMarkdown(entries);
await syncImages(entries);

console.log(`Synced documentation from ${path.relative(repoRoot, sourceDir)} to ${path.relative(repoRoot, outputDir)}`);
