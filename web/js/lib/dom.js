// Tiny DOM helper: h("button.primary", {onclick, title}, "text", childNode)

/**
 * @param {string} tag  tag name with optional .class suffixes, e.g. "div.cell.busy"
 * @param {Record<string, any> | null} [props]
 * @param {...(Node | string | number | null | undefined | false)} children
 * @returns {HTMLElement}
 */
export function h(tag, props, ...children) {
  const [name, ...classes] = tag.split(".");
  const el = document.createElement(name || "div");
  if (classes.length) el.className = classes.join(" ");
  for (const [key, value] of Object.entries(props ?? {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key.startsWith("on") && typeof value === "function") {
      el.addEventListener(key.slice(2), value);
    } else if (key === "dataset") {
      Object.assign(el.dataset, value);
    } else if (key in el && key !== "list") {
      /** @type {any} */ (el)[key] = value;
    } else {
      el.setAttribute(key, value === true ? "" : String(value));
    }
  }
  for (const child of children) {
    if (child === null || child === undefined || child === false) continue;
    el.append(typeof child === "string" || typeof child === "number" ? String(child) : child);
  }
  return el;
}
