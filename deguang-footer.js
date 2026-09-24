class DeguangFooter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }
    connectedCallback() {
        const year = new Date().getFullYear();
        this.shadowRoot.innerHTML = `
            <style>
        :host, .deguang-footer-fallback { display: block; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        .footer { margin-top: 4rem; padding: 4rem 1.5rem 2rem; background-color: var(--dg-bg-subtle, transparent); border-top: 1px solid var(--dg-border, #eaeaea); display: flex; flex-direction: column; align-items: center; }
        .footer-content { width: 100%; max-width: 900px; display: flex; flex-direction: column; gap: 2.5rem; }
        .matrix-section { display: flex; flex-direction: column; gap: 1.5rem; width: 100%; }
        .matrix-heading { margin: 0; font-size: 0.875rem; font-weight: 600; color: var(--dg-heading, #111827); letter-spacing: 0.05em; text-transform: uppercase; }
        .matrix-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem 2rem; }
        @media (min-width: 640px) { .matrix-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 768px) { .matrix-grid { grid-template-columns: repeat(4, 1fr); } }
        .matrix-grid a { color: var(--dg-muted, #6b7280); font-size: 0.875rem; text-decoration: none; transition: color 0.2s ease, transform 0.2s ease; display: inline-block; }
        .matrix-grid a:hover { color: var(--dg-main, #111827); transform: translateX(3px); }
        .footer-divider { border: 0; height: 1px; background: var(--dg-border, #eaeaea); width: 100%; margin: 0; }
        .footer-bottom { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1.5rem; font-size: 0.875rem; color: var(--dg-muted, #9ca3af); }
        .footer-links { display: flex; gap: 1.5rem; flex-wrap: wrap; }
        .footer-links a { color: var(--dg-muted, #9ca3af); text-decoration: none; transition: color 0.2s ease; }
        .footer-links a:hover { color: var(--dg-main, #111827); }
        @media (prefers-color-scheme: dark) {
            .footer { --dg-border: #2a2e37; --dg-heading: #f3f4f6; --dg-muted: #9ca3af; --dg-main: #ffffff; }
        }
</style>

            <footer class="footer">
                <div class="footer-content">
                    <div class="matrix-section">
                        <h3 class="matrix-heading">App Matrix</h3>
                        <div class="matrix-grid">
                            <a href="https://app.lideguang.com/link-and-title-copy-pro/" target="_blank" rel="noopener">Link & Title Copy Pro</a><a href="https://app.lideguang.com/gemini-graph-viewer/" target="_blank" rel="noopener">Gemini Graph Viewer</a><a href="https://app.lideguang.com/query-params-viewer/" target="_blank" rel="noopener">Query Params Viewer</a><a href="https://app.lideguang.com/keep-scroll-sync/" target="_blank" rel="noopener">Keep Scroll Sync</a><a href="https://page.lideguang.com/" target="_blank" rel="noopener">EdgeForm</a><a href="https://github.com/Deguang/vue-pdf-reader" target="_blank" rel="noopener">Vue PDF Reader</a>
                        </div>
                    </div>
                    <hr class="footer-divider" />
                    <div class="footer-bottom">
                        <div class="footer-copyright">&copy; ${year} Li Deguang</div>
                        <div class="footer-links">
                            <a href="https://app.lideguang.com" target="_blank" rel="noopener">Dashboard</a>
                            <a href="https://github.com/Deguang" target="_blank" rel="noopener">GitHub</a>
                            <a href="https://x.com/deguang_li" target="_blank" rel="noopener">X</a>
                        </div>
                    </div>
                </div>
            </footer>

        `;
    }
}
customElements.define('deguang-footer', DeguangFooter);
