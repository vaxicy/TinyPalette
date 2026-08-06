(function () {
  "use strict";

  // ---- i18n ----
  const I18N = {
    en: {
      brand: "TinyPalette",
      tagline: "a tiny color companion",
      tapToCopy: "Tap to copy",
      hex: "HEX",
      rgb: "RGB",
      hsl: "HSL",
      copyCss: "Copy CSS",
      enterHex: "ENTER HEX",
      copied: "Copied!",
      cssCopied: "CSS copied!",
      invalid: "Invalid HEX",
      copyHex: "Copy HEX",
      ok: "OK",
      switchLang: "Switch to Chinese",
      switchLangTip: "EN / ZH"
    },
    zh_CN: {
      brand: "TinyPalette",
      tagline: "小巧的色彩小助手",
      tapToCopy: "点击复制",
      hex: "HEX",
      rgb: "RGB",
      hsl: "HSL",
      copyCss: "复制 CSS",
      enterHex: "ENTER HEX",
      copied: "已复制！",
      cssCopied: "已复制 CSS！",
      invalid: "无效 HEX",
      copyHex: "复制 HEX",
      ok: "确定",
      switchLang: "切换到英文",
      switchLangTip: "ZH / EN"
    }
  };

  const STORAGE_KEYS = Object.freeze({
    LANG: "tp_lang",
    THEME: "tp_theme_color"
  });

  const DEFAULT_THEME = "#E8A0BF";

  // ---- DOM ----
  const el = {
    input: document.getElementById("hexInput"),
    picker: document.getElementById("colorPicker"),
    hexValue: document.getElementById("hexValue"),
    rgbValue: document.getElementById("rgbValue"),
    hslValue: document.getElementById("hslValue"),
    copyCss: document.getElementById("copyCssBtn"),
    themePicker: document.getElementById("themePicker"),
    toast: document.getElementById("toast"),
    panel: document.getElementById("pickerPanel"),
    svCanvas: document.getElementById("svCanvas"),
    hueCanvas: document.getElementById("hueCanvas"),
    preview: document.getElementById("pickerPreview"),
    pickerHex: document.getElementById("pickerHex"),
    pickerOk: document.getElementById("pickerOk"),
    langToggle: document.getElementById("langToggle")
  };

  let currentHex = null;
  let lang = "en";

  // ---- i18n apply ----
  function applyI18n() {
    const t = I18N[lang] || I18N.en;
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.getAttribute("data-i18n");
      if (t[key]) node.textContent = t[key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      const key = node.getAttribute("data-i18n-placeholder");
      if (t[key]) node.placeholder = t[key];
    });
    document.documentElement.lang = lang === "zh_CN" ? "zh-CN" : "en";
    if (el.langToggle) {
      el.langToggle.setAttribute("data-tooltip", t.switchLangTip);
      el.langToggle.setAttribute("aria-label", t.switchLang);
    }
  }

  // ---- color utils ----
  function normalizeHex(raw) {
    if (typeof raw !== "string") return null;
    if (!raw) return null;
    let h = raw.trim().replace(/^#/, "").toUpperCase();
    if (/^[0-9A-F]{3}$/.test(h)) {
      h = h.split("").map((c) => c + c).join("");
    }
    if (/^[0-9A-F]{6}$/.test(h)) return "#" + h;
    return null;
  }

  function hexToRgb(hex) {
    const h = hex.replace("#", "");
    return {
      r: parseInt(h.slice(0, 2), 16),
      g: parseInt(h.slice(2, 4), 16),
      b: parseInt(h.slice(4, 6), 16)
    };
  }

  function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        default: h = (r - g) / d + 4;
      }
      h /= 6;
    }
    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  }

  function hslToHex(h, s, l) {
    h = Number(h) || 0; s = Number(s) || 0; l = Number(l) || 0;
    h = ((h % 360) + 360) % 360; s = clamp(s, 0, 100) / 100; l = clamp(l, 0, 100) / 100;
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;
    let r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; }
    else if (h < 120) { r = x; g = c; }
    else if (h < 180) { g = c; b = x; }
    else if (h < 240) { g = x; b = c; }
    else if (h < 300) { r = x; b = c; }
    else { r = c; b = x; }
    const to = (v) => Math.round((v + m) * 255).toString(16).padStart(2, "0").toUpperCase();
    return "#" + to(r) + to(g) + to(b);
  }

  function hexToRgba(hex, a) {
    const { r, g, b } = hexToRgb(normalizeHex(hex) || "#000000");
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }

  function t(key) {
    return (I18N[lang] || I18N.en)[key];
  }

  // ---- render ----
  function render(hex) {
    currentHex = hex;
    const { r, g, b } = hexToRgb(hex);
    const hsl = rgbToHsl(r, g, b);

    el.hexValue.textContent = hex.toUpperCase();
    el.rgbValue.textContent = `${r}, ${g}, ${b}`;
    el.hslValue.textContent = `${hsl.h}°, ${hsl.s}%, ${hsl.l}%`;
    el.input.value = hex.replace("#", "").toUpperCase();
    el.picker.style.background = hex;
  }

  // ---- toast ----
  let toastTimer = null;
  function showToast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.toast.classList.remove("show"), 1500);
  }

  // ---- copy ----
  function copyText(text) {
    const done = () => showToast(t("copied"));
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  function cssString(hex) {
    const { r, g, b } = hexToRgb(hex);
    return `background-color: ${hex.toUpperCase()};\n/* rgb(${r}, ${g}, ${b}) */`;
  }

  // ---- theme color (UI accent) ----
  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function relativeLuminance(rr, gg, bb) {
    const tr = (c) => {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * tr(rr) + 0.7152 * tr(gg) + 0.0722 * tr(bb);
  }

  // Convert an accent hex into a same-hue creamy "handheld" palette so the
  // whole background follows the chosen color while keeping the pixel vibe.
  function setThemeColor(hex) {
    const norm = normalizeHex(hex);
    if (!norm) return;
    const { r, g, b } = hexToRgb(norm);
    let { h, s, l } = rgbToHsl(r, g, b);

    // Derive a soft, light background from the accent hue.
    const bgS = clamp(s * 0.28, 6, 35);        // low saturation creamy
    const bgL = clamp(l * 0.98 + 60, 90, 97);  // near-white, follows brightness
    const bg = hslToHex(h, bgS, bgL);

    // Panel slightly whiter than bg.
    const panel = hslToHex(h, clamp(s * 0.18, 4, 22), clamp(bgL + 2, 92, 99));

    // Darker accent for borders / pixel details.
    const primaryDark = hslToHex(h, clamp(s * 0.85, 18, 85), clamp(l * 0.66, 22, 52));

    // Strongly darkened accent for text sitting directly on the accent background.
    const deepAccent = hslToHex(h, clamp(s * 0.9, 20, 100), clamp(l * 0.35, 10, 35));

    // Text: pick a readable deep tone based on accent lightness.
    const textL = clamp(l > 62 ? l * 0.32 : l * 0.28, 14, 30);
    const text = hslToHex(h, clamp(s * 0.7, 12, 60), textL);
    const textSoft = hslToHex(h, clamp(s * 0.55, 10, 50), clamp(textL + 22, 38, 56));

    // Smart button text: white on dark accents, darkened accent on light accents.
    const lum = relativeLuminance(r, g, b);
    const isDark = lum < 0.45;
    const btnText = isDark ? "#FFFFFF" : deepAccent;
    const btnTextShadow = isDark ? "rgba(0, 0, 0, 0.25)" : `rgba(${r}, ${g}, ${b}, 0.35)`;
    const btnTextHover = "#FFFFFF";

    const root = document.documentElement.style;
    root.setProperty("--primary", norm);
    root.setProperty("--primary-rgb", `${r}, ${g}, ${b}`);
    root.setProperty("--primary-dark", primaryDark);
    root.setProperty("--bg", bg);
    root.setProperty("--panel", panel);
    root.setProperty("--text", text);
    root.setProperty("--text-soft", textSoft);
    root.setProperty("--primary-soft", `rgba(${r}, ${g}, ${b}, 0.16)`);
    root.setProperty("--primary-soft-2", `rgba(${r}, ${g}, ${b}, 0.3)`);
    root.setProperty("--primary-shadow", `rgba(${r}, ${g}, ${b}, 0.35)`);
    root.setProperty("--primary-shadow-hover", `rgba(${r}, ${g}, ${b}, 0.45)`);
    root.setProperty("--field-border", `rgba(${r}, ${g}, ${b}, 0.3)`);
    root.setProperty("--field-border-strong", `rgba(${r}, ${g}, ${b}, 0.5)`);
    // Placeholder: readable tint of accent hue. Dark accents get a soft
    // light tint, light accents get a muted darker tint for contrast.
    const placeholder = isDark
      ? hslToHex(h, clamp(s * 0.4, 10, 60), clamp(l * 1.1 + 55, 70, 88))
      : hslToHex(h, clamp(s * 0.5, 12, 55), clamp(l * 0.6, 45, 62));
    root.setProperty("--placeholder", placeholder);
    root.setProperty("--shadow-sm", `2px 2px 0 ${hexToRgba(primaryDark, 0.18)}`);
    root.setProperty("--btn-text", btnText);
    root.setProperty("--btn-text-shadow", btnTextShadow);
    root.setProperty("--btn-text-hover", btnTextHover);
    el.themePicker.style.background = norm;
  }

  function loadThemeColor(cb) {
    try {
      chrome.storage.local.get(STORAGE_KEYS.THEME, (data) => {
        const saved = data[STORAGE_KEYS.THEME];
        if (saved && normalizeHex(saved)) {
          cb(normalizeHex(saved));
        } else {
          cb(DEFAULT_THEME);
        }
      });
    } catch (e) {
      cb(DEFAULT_THEME);
    }
  }

  function saveThemeColor(hex) {
    try {
      chrome.storage.local.set({ [STORAGE_KEYS.THEME]: hex });
    } catch (e) {}
  }

  // ---- events ----
  el.input.addEventListener("input", () => {
    const norm = normalizeHex(el.input.value);
    if (norm) {
      render(norm);
    }
  });

  el.picker.addEventListener("click", (e) => {
    e.stopPropagation();
    openPanel(currentHex || "#E8A0BF", (hex) => {
      render(hex);
    }, (hex) => {
      render(hex);
    });
  });

  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!currentHex) return;
      const type = btn.getAttribute("data-copy");
      if (type === "hex") copyText(currentHex.toUpperCase());
      else if (type === "rgb") copyText(el.rgbValue.textContent);
      else if (type === "hsl") copyText(el.hslValue.textContent);
    });
  });

  el.copyCss.addEventListener("click", () => {
    if (!currentHex) { showToast(t("invalid")); return; }
    copyText(cssString(currentHex));
    showToast(t("cssCopied"));
  });

  el.themePicker.addEventListener("click", (e) => {
    e.stopPropagation();
    openPanel(el.themePicker.style.background || DEFAULT_THEME, (hex) => {
      setThemeColor(hex);
      saveThemeColor(hex);
    }, (hex) => {
      setThemeColor(hex);
    });
  });

  // ---- language toggle ----
  function switchLang() {
    lang = lang === "zh_CN" ? "en" : "zh_CN";
    try { localStorage.setItem(STORAGE_KEYS.LANG, lang); } catch (e) {}
    applyI18n();
  }

  el.langToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    switchLang();
  });

  // ---- custom tooltip ----
  const tip = document.createElement("div");
  tip.className = "tp-tooltip";
  tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);

  function showTip(target) {
    const text = target.getAttribute("data-tooltip");
    if (!text) return;
    tip.textContent = text;
    const r = target.getBoundingClientRect();
    tip.classList.add("show");
    const tr = tip.getBoundingClientRect();
    let left = r.left + r.width / 2 - tr.width / 2;
    left = Math.max(6, Math.min(left, window.innerWidth - tr.width - 6));
    tip.style.left = left + "px";
    tip.style.top = (r.bottom + 6) + "px";
  }

  function hideTip() {
    tip.classList.remove("show");
  }

  document.addEventListener("mouseover", (e) => {
    const node = e.target.closest("[data-tooltip]");
    if (node) showTip(node);
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest("[data-tooltip]")) hideTip();
  });
  document.addEventListener("focusin", (e) => {
    const node = e.target.closest("[data-tooltip]");
    if (node) showTip(node);
  });
  document.addEventListener("focusout", hideTip);

  // ---- custom pixel color picker panel ----
  let panelState = { h: 0, s: 0, l: 0, onPick: null, onLive: null, originalHex: null, committed: false, hueDrag: false, svDrag: false };

  function drawSV() {
    const ctx = el.svCanvas.getContext("2d");
    const w = el.svCanvas.width, h = el.svCanvas.height;
    const base = hslToHex(panelState.h, 100, 50);
    // horizontal saturation gradient (white -> full hue)
    const gx = ctx.createLinearGradient(0, 0, w, 0);
    gx.addColorStop(0, "#FFFFFF");
    gx.addColorStop(1, base);
    ctx.fillStyle = gx;
    ctx.fillRect(0, 0, w, h);
    // vertical lightness gradient (transparent -> black)
    const gy = ctx.createLinearGradient(0, 0, 0, h);
    gy.addColorStop(0, "rgba(0,0,0,0)");
    gy.addColorStop(1, "rgba(0,0,0,1)");
    ctx.fillStyle = gy;
    ctx.fillRect(0, 0, w, h);
  }

  function drawHue() {
    const ctx = el.hueCanvas.getContext("2d");
    const w = el.hueCanvas.width, h = el.hueCanvas.height;
    const g = ctx.createLinearGradient(0, 0, w, 0);
    for (let i = 0; i <= 6; i++) {
      g.addColorStop(i / 6, hslToHex(i * 60, 100, 50));
    }
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  }

  function panelRender() {
    const hex = hslToHex(panelState.h, panelState.s, panelState.l);
    el.preview.style.background = hex;
    el.pickerHex.value = hex.replace("#", "").toUpperCase();
    if (panelState.onLive) panelState.onLive(hex);
  }

  function openPanel(initialHex, onPick, onLive) {
    const original = normalizeHex(initialHex);
    const norm = original || DEFAULT_THEME;
    const { r, g, b } = hexToRgb(norm);
    const hsl = rgbToHsl(r, g, b);
    panelState.h = hsl.h;
    panelState.s = hsl.s;
    panelState.l = hsl.l;
    panelState.onPick = onPick;
    panelState.onLive = onLive;
    panelState.originalHex = original;
    panelState.committed = false;
    drawSV();
    drawHue();
    panelRender();
    el.panel.hidden = false;
    if (typeof chrome !== "undefined" && chrome.runtime) {
      chrome.runtime.getManifest(); // no-op keep SW alive
    }
  }

  function closePanel() {
    if (!panelState.committed && panelState.originalHex && panelState.onLive) {
      panelState.onLive(panelState.originalHex);
    }
    el.panel.hidden = true;
    panelState.onPick = null;
    panelState.onLive = null;
    panelState.originalHex = null;
    panelState.committed = false;
  }

  function svFromEvent(e) {
    const rect = el.svCanvas.getBoundingClientRect();
    const x = clamp((e.clientX - rect.left) / rect.width, 0, 1);
    const y = clamp((e.clientY - rect.top) / rect.height, 0, 1);
    panelState.s = Math.round(x * 100);
    panelState.l = Math.round((1 - y) * 100);
    panelRender();
  }

  function hueFromEvent(e) {
    const rect = el.hueCanvas.getBoundingClientRect();
    const x = clamp((e.clientX - rect.left) / rect.width, 0, 1);
    panelState.h = Math.round(x * 360);
    drawSV();
    panelRender();
  }

  el.svCanvas.addEventListener("pointerdown", (e) => {
    panelState.svDrag = true;
    el.svCanvas.setPointerCapture(e.pointerId);
    svFromEvent(e);
  });
  el.svCanvas.addEventListener("pointermove", (e) => {
    if (panelState.svDrag) svFromEvent(e);
  });
  el.svCanvas.addEventListener("pointerup", () => { panelState.svDrag = false; });

  el.hueCanvas.addEventListener("pointerdown", (e) => {
    panelState.hueDrag = true;
    el.hueCanvas.setPointerCapture(e.pointerId);
    hueFromEvent(e);
  });
  el.hueCanvas.addEventListener("pointermove", (e) => {
    if (panelState.hueDrag) hueFromEvent(e);
  });
  el.hueCanvas.addEventListener("pointerup", () => { panelState.hueDrag = false; });

  el.pickerHex.addEventListener("input", () => {
    const norm = normalizeHex(el.pickerHex.value);
    if (norm) {
      const { r, g, b } = hexToRgb(norm);
      const hsl = rgbToHsl(r, g, b);
      panelState.h = hsl.h; panelState.s = hsl.s; panelState.l = hsl.l;
      drawSV();
      panelRender();
    }
  });

  el.pickerOk.addEventListener("click", (e) => {
    e.stopPropagation();
    const norm = normalizeHex(el.pickerHex.value) || hslToHex(panelState.h, panelState.s, panelState.l);
    panelState.committed = true;
    const cb = panelState.onPick;
    closePanel();
    if (cb) cb(norm);
  });

  // close panel when clicking outside
  document.addEventListener("click", (e) => {
    if (el.panel.hidden) return;
    if (!el.panel.contains(e.target) && e.target !== el.picker && e.target !== el.themePicker) {
      closePanel();
    }
  });

  // ---- init ----
  function init() {
    let stored = "en";
    try {
      stored = localStorage.getItem(STORAGE_KEYS.LANG) || (navigator.language || "en");
    } catch (e) {}
    lang = stored.indexOf("zh") === 0 ? "zh_CN" : "en";
    applyI18n();

    // Apply stored theme color (or default) to the whole UI accent.
    loadThemeColor((hex) => {
      setThemeColor(hex);
    });

    // Start empty: values show "--", no default color applied.
    el.hexValue.textContent = "--";
    el.rgbValue.textContent = "--";
    el.hslValue.textContent = "--";
  }

  init();
})();
