export function readJsonScript(id) {
  const node = document.getElementById(id);
  if (!node || !node.textContent) return null;
  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.warn(`Failed to parse JSON config from #${id}`, error);
    return null;
  }
}

export function structuredCloneSafe(value) {
  try {
    return structuredClone(value);
  } catch {
    return JSON.parse(JSON.stringify(value));
  }
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function applyFavicon(logoUrl, emoji) {
  if (typeof document === 'undefined') return;
  const favicon = document.getElementById('app-favicon');
  if (!favicon) return;

  const normalizedLogoUrl = String(logoUrl || '').trim();
  if (normalizedLogoUrl) {
    favicon.setAttribute('href', normalizedLogoUrl);
    return;
  }

  const normalizedEmoji = String(emoji || '????').trim() || '????';
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" font-size="52">${escapeHtml(normalizedEmoji)}</text></svg>`;
  const encoded = encodeURIComponent(svg);
  favicon.setAttribute('href', `data:image/svg+xml,${encoded}`);
}
