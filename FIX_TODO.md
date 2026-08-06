# TinyPalette 修复记录 - 2026-08-07

## 现象（用户昨晚报）
popup 运行时报了两个错：
1. `normalizeHex` 被传了非字符串值
2. `hslToHex` 未定义却被调用

## 诊断结论
- 当前磁盘上的 `popup.js` 中 `normalizeHex` 和 `hslToHex` 均已正确定义、逻辑自洽。
- 两个报错极可能来自**浏览器加载了旧的/缓存截断的 popup.js 版本**（未 Reload 生效）。
- 验证：用 Node `vm` 在 mock DOM 下完整加载 `popup.js`，`init()` 与全部函数定义成功执行，无"未定义"错误。

## 已修复（防御性）
1. `normalizeHex` 开头加 `if (typeof raw !== "string") return null;` —— 非字符串入参直接返回 null，避免 `.trim()` 抛错。
2. `hslToHex` 入参加 `Number(x) || 0` 归一化 —— 非数值也不产生 NaN 色值。

## 验证
- `node -e` 解析 popup.js 语法 OK。
- mock DOM 完整加载 OK，无 undefined function 错误。

## 用户需做
- 打开 `chrome://extensions` 找到 TinyPalette 点 **Reload**，再开 popup 确认 Console 无报错。
- 若仍报错，大概率是扩展未 Reload 或 Chrome 缓存旧包，强制 Reload / 重新加载解压版即可。

## 备注
- 已 commit。
