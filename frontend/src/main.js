import { mount } from "svelte";

import App from "./App.svelte";
import "./styles.css";
import { isExternalAppLaunchPath } from "./lib/webapp/appLinks.js";

async function loadBootstrap() {
  if (document.getElementById("webapp-config")) return;
  try {
    const response = await fetch("/api/bootstrap?i18n_scope=webapp", {
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return;
    const payload = await response.json();
    for (const [id, value] of [
      ["webapp-config", payload.config],
      ["i18n", payload.i18n],
    ]) {
      const script = document.createElement("script");
      script.id = id;
      script.type = "application/json";
      script.textContent = JSON.stringify(value || {});
      document.head.appendChild(script);
    }
  } catch (_error) {
    void _error;
  }
}

const target = document.getElementById("app");
const skipBootstrap = isExternalAppLaunchPath(window.location.pathname);

if (target) {
  (skipBootstrap ? Promise.resolve() : loadBootstrap()).finally(() => {
    target.replaceChildren();
    mount(App, { target });
  });
}
