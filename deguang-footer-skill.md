---
name: inject-deguang-footer
description: 自动为当前项目集成 Li Deguang 的全局动态 SEO 友好 Footer
---

# Inject Deguang Footer Skill

## 目标
当前项目需要接入 `Li Deguang` 的应用矩阵全局 Footer。这个 Footer 是用来保持各个项目之间的互相连接（类似黄页网络的互联）。

## 资源地址
- **HTML 静态片段（用于 SEO 构建时拉取）**: `https://app.lideguang.com/footer-snippet.html`
- **Web Component (用于纯前端运行时拉取)**: `https://app.lideguang.com/deguang-footer.js`

## 执行指南 (Agent Instructions)

请按照以下步骤自动分析并为当前项目集成该 Footer：

1. **分析当前项目的技术栈与定位原 Footer**：
   - 检查当前项目使用的是什么框架（Hugo, Hexo, VitePress, Next.js, React 等）。
   - **必须**在源码中全局搜索原有的 Footer 占位符或组件（例如 `components/Footer.vue`, `Footer.jsx`, `layouts/partials/footer.html`，或者纯 HTML 的 `<footer>` 标签）。
   - **核心动作**：清除原有的全部版权声明（Copyright）、社交链接和无关导航，确保新 Footer 接入后**不会出现双 Footer 的重叠情况**。

2. **注入终极混合方案 (Hybrid SSR + CSR)**：
   - 如果项目有 `.github/workflows/` 下的自动化部署脚本，请在执行 `build` 打包步骤之前，利用 `curl` 将全局 Footer 拉取并替换到目标组件中：
     ```yaml
     - name: Fetch Hybrid Footer
       run: curl -sS https://app.lideguang.com/footer-snippet.html > ./path/to/layout/footer.html
     ```
   - 这样拉取到的代码既包含了供爬虫抓取的静态 `<a href>`（完美 SEO），又自带 `<script>` 脚本，当真实用户访问时会通过 Web Component 动态呈现最新矩阵，免去定时更新的烦恼。
   - 如果没有 CI/CD 或者无法在构建前拉取，请直接在 HTML 模板底部引入 `<script src="https://app.lideguang.com/deguang-footer.js" type="module" async></script>`，并在 DOM 底部放置 `<deguang-footer></deguang-footer>`。

3. **主题兼容性适配 (Theme Compatibility)**：
   - `deguang-footer` 默认自带明暗模式样式，并且通过媒体查询 `@media (prefers-color-scheme: dark)` 自动随操作系统切换。
   - **类名适配**：如果当前项目是通过给 `<html>` 或 `<body>` 添加 `class="dark"` 或 `data-theme="dark"` 来手动控制暗黑模式的，请注意 Web Component 的 Shadow DOM 是无法直接读取到这些外部类名的。
   - **适配方案**：你需要评估新 Footer 与当前项目背景色的融合度。如果存在违和感，可以在当前项目的全局 CSS 中，针对 `deguang-footer` 标签强制重写 CSS 变量，或者通过 JS 同步类名状态。由于新 Footer 采用透明背景设计（Transparent Background），大部分情况下可以直接自然融入宿主站点的主题。

4. **完成与检查**：
   - 运行测试构建确保原有 UI 未被破坏，且只显示一个全局 Footer。
   - 告知用户已经成功移除了旧 Footer，并完成了矩阵 Footer 的接入与主题融合。
