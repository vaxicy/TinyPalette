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
      copied: "Copied!",
      cssCopied: "CSS copied!",
      invalid: "Invalid HEX",
      copyHex: "Copy HEX"
    },
    zh_CN: {
      brand: "TinyPalette",
      tagline: "小巧的色彩小助手",
      tapToCopy: "点击复制",
      hex: "HEX",
      rgb: "RGB",
      hsl: "HSL",
      copyCss: "复制 CSS",
      copied: "已复制！",
      cssCopied: "已复制 CSS！",
      invalid: "无效 HEX",
      copyHex: "复制 HEX"
    }
  };

  const STORAGE_KEYS = Object.freeze({
    LANG: "tp_lang"
  });

  // ---- DOM ----
  const el = {
    input: document.getElementById("hexInput"),
    picker: document.getElementById("colorPicker"),
    hexValue: document.getElementById("hexValue"),
    rgbValue: document.getElementById("rgbValue"),
    hslValue: document.getElementById("hslValue"),
    copyCss: document.getElementById("copyCssBtn"),
    toast: document.getElementById("toast")
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
    document.documentElement.lang = lang === "zh_CN" ? "zh-CN" : "en";
  }

  // ---- color utils ----
  function normalizeHex(raw) {
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
    el.picker.value = hex;
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

  // ---- events ----
  el.input.addEventListener("input", () => {
    const norm = normalizeHex(el.input.value);
    if (norm) {
      render(norm);
    }
  });

  el.picker.addEventListener("input", () => {
    const norm = normalizeHex(el.picker.value);
    if (norm) {
      render(norm);
    }
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

  // ---- init ----
  function init() {
    let stored = "en";
    try {
      stored = localStorage.getItem(STORAGE_KEYS.LANG) || (navigator.language || "en");
    } catch (e) {}
    lang = stored.indexOf("zh") === 0 ? "zh_CN" : "en";
    applyI18n();

    // Start empty: values show "--", no default color applied.
    el.hexValue.textContent = "--";
    el.rgbValue.textContent = "--";
    el.hslValue.textContent = "--";
  }

  init();
})();
