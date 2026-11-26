// Canvas preview of a clip's notes (no per-note DOM nodes).

/**
 * @param {HTMLCanvasElement} canvas
 * @param {Array<{t: number, p: number, d: number, v: number}>} notes
 * @param {number} lengthTicks
 * @param {number} barLength  ticks per bar
 * @param {boolean} isDrum
 */
export function drawClip(canvas, notes, lengthTicks, barLength, isDrum) {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 160;
  const height = canvas.clientHeight || 44;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);
  const style = getComputedStyle(canvas);
  const grid = style.getPropertyValue("--clip-grid").trim() || "#8884";
  const fill = style.getPropertyValue("--clip-note").trim() || "#4a7";

  ctx.fillStyle = grid;
  for (let tick = barLength; tick < lengthTicks; tick += barLength) {
    ctx.fillRect(Math.round((tick / lengthTicks) * width), 0, 1, height);
  }
  if (!notes.length) return;

  let low = Infinity;
  let high = -Infinity;
  for (const n of notes) {
    low = Math.min(low, n.p);
    high = Math.max(high, n.p);
  }
  const span = Math.max(high - low, isDrum ? 1 : 12);
  const rowHeight = Math.max(2, Math.min(6, (height - 4) / (span + 1)));
  ctx.fillStyle = fill;
  for (const n of notes) {
    const x = (n.t / lengthTicks) * width;
    const w = Math.max(2, (n.d / lengthTicks) * width - 1);
    const y = height - 2 - ((n.p - low) / span) * (height - 4 - rowHeight) - rowHeight;
    ctx.globalAlpha = 0.45 + 0.55 * (n.v / 127);
    ctx.fillRect(x, y, w, rowHeight);
  }
  ctx.globalAlpha = 1;
}
