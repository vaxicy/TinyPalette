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
      recent: "Recent",
      copied: "Copied!",
      cssCopied: "CSS copied!",
      invalid: "Invalid HEX",
      empty: "Nothing here yet",
      delRecent: "Remove",
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
      recent: "最近使用",
      copied: "已复制！",
      cssCopied: "已复制 CSS！",
      invalid: "无效 HEX",
      empty: "暂无记录",
      delRecent: "删除",
      copyHex: "复制 HEX"
    }
  };

  const STORAGE_KEYS = Object.freeze({
    RECENT: "tp_recent"
  });
  const MAX_RECENT = 12;

  // ---- DOM ----
  const el = {
    input: document.getElementById("hexInput"),
    picker: document.getElementById("colorPicker"),
    previewDot: document.getElementById("previewDot"),
    hexValue: document.getElementById("hexValue"),
    rgbValue: document.getElementById("rgbValue"),
    hslValue: document.getElementById("hslValue"),
    copyCss: document.getElementById("copyCssBtn"),
    recentList: document.getElementById("recentList"),
    recentPanel: document.getElementById("recentPanel"),
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
    el.previewDot.title = t("copyHex");
    el.previewDot.setAttribute("aria-label", t("copyHex"));
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

  // contrast text color for swatches
  function luminance(hex) {
    const { r, g, b } = hexToRgb(hex);
    const a = [r, g, b].map((v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
  }

  function t(key) {
    return (I18N[lang] || I18N.en)[key];
  }

  // ---- render ----
  function render(hex) {
    currentHex = hex;
    const { r, g, b } = hexToRgb(hex);
    const hsl = rgbToHsl(r, g, b);

    el.previewDot.style.backgroundColor = hex;
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

  // ---- storage ----
  function getRecent() {
    return new Promise((res) => {
      chrome.storage.local.get(STORAGE_KEYS.RECENT, (d) =>
        res(Array.isArray(d[STORAGE_KEYS.RECENT]) ? d[STORAGE_KEYS.RECENT] : []));
    });
  }
  function setRecent(arr) {
    chrome.storage.local.set({ [STORAGE_KEYS.RECENT]: arr });
  }

  function pushRecent(hex) {
    getRecent().then((list) => {
      const next = [hex, ...list.filter((c) => c !== hex)].slice(0, MAX_RECENT);
      setRecent(next);
      renderRecent(next);
    });
  }

  function renderRecent(list) {
    el.recentList.innerHTML = "";
    if (!list.length) {
      el.recentPanel.hidden = true;
      return;
    }
    el.recentPanel.hidden = false;
    list.forEach((hex) => {
      const sw = makeSwatch(hex);
      el.recentList.appendChild(sw);
    });
  }

  function makeSwatch(hex) {
    const sw = document.createElement("div");
    sw.className = "swatch";
    sw.style.backgroundColor = hex;
    sw.style.borderColor = luminance(hex) > 0.6 ? "rgba(255,255,255,0.9)" : "rgba(74,70,80,0.18)";
    sw.title = hex;
    sw.addEventListener("click", () => {
      const norm = normalizeHex(hex);
      if (norm) { render(norm); pushRecent(norm); }
    });
    const del = document.createElement("button");
    del.className = "del-btn";
    del.type = "button";
    del.textContent = "×";
    del.setAttribute("aria-label", t("delRecent"));
    del.title = t("delRecent");
    del.addEventListener("click", (e) => {
      e.stopPropagation();
      removeRecent(hex);
    });
    sw.appendChild(del);
    return sw;
  }

  function removeRecent(hex) {
    getRecent().then((list) => {
      const next = list.filter((c) => c !== hex);
      setRecent(next);
      renderRecent(next);
    });
  }

  // ---- events ----
  el.input.addEventListener("input", () => {
    const norm = normalizeHex(el.input.value);
    if (norm) {
      render(norm);
      pushRecent(norm);
    }
  });

  el.picker.addEventListener("input", () => {
    const norm = normalizeHex(el.picker.value);
    if (norm) {
      render(norm);
      pushRecent(norm);
    }
  });

  el.previewDot.addEventListener("click", () => {
    if (currentHex) copyText(currentHex.toUpperCase());
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
      stored = localStorage.getItem("tp_lang") || (navigator.language || "en");
    } catch (e) {}
    lang = stored.indexOf("zh") === 0 ? "zh_CN" : "en";
    applyI18n();

    // Start empty: values show "--", no default color applied.
    el.hexValue.textContent = "--";
    el.rgbValue.textContent = "--";
    el.hslValue.textContent = "--";
    el.previewDot.style.backgroundColor = "#EFE9ED";

    getRecent().then(renderRecent);
  }

  init();
})();
