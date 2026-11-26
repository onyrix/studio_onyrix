import { applyTranslations, t } from "./lib/i18n.js";

applyTranslations();

const status = /** @type {HTMLElement} */ (document.getElementById("status"));
status.textContent = t("status.pending");

try {
  const response = await fetch("/api/health");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const health = await response.json();
  status.textContent = t("status.ok", { version: health.version });
  status.dataset.state = "ok";
} catch {
  status.textContent = t("status.error");
  status.dataset.state = "error";
}
