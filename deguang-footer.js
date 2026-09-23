class DeguangFooter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }
    connectedCallback() {
        const year = new Date().getFullYear();
        const style = `
            :host { display: block; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
            .footer { text-align: center; margin-top: 3.5rem; padding: 1.5rem 0; color: #6b7280; font-size: 0.85rem; }
            .footer a { color: #4f46e5; text-decoration: none; transition: color 0.15s ease; }
            .footer a:hover { text-decoration: underline; color: #4338ca; }
            @media (prefers-color-scheme: dark) {
                .footer { color: #9ca3af; }
                .footer a { color: #818cf8; }
                .footer a:hover { color: #a5b4fc; }
            }
        `;
        this.shadowRoot.innerHTML = `
            <style>${style}</style>
            <footer class="footer">
                <div class="matrix-links" style="margin-bottom: 12px; line-height: 1.8;">
                    <span style="color:#6b7280; font-weight: 500; margin-right: 8px;">Matrix:</span>
                    <a href="https://app.lideguang.com/token-speed-visual/" target="_blank" rel="noopener">token-speed-visual</a> &middot; <a href="https://app.lideguang.com/iphone-lockstage/" target="_blank" rel="noopener">iphone-lockstage</a> &middot; <a href="https://app.lideguang.com/tug/" target="_blank" rel="noopener">tug</a> &middot; <a href="https://app.lideguang.com/gemini-graph-viewer/" target="_blank" rel="noopener">gemini-graph-viewer</a> &middot; <a href="https://app.lideguang.com/link-and-title-copy-pro/" target="_blank" rel="noopener">link-and-title-copy-pro</a> &middot; <a href="https://app.lideguang.com/doc-parser/" target="_blank" rel="noopener">doc-parser</a> &middot; <a href="https://app.lideguang.com/agent-course/" target="_blank" rel="noopener">agent-course</a> &middot; <a href="https://app.lideguang.com/query-params-viewer/" target="_blank" rel="noopener">query-params-viewer</a> &middot; <a href="https://app.lideguang.com/keep-scroll-sync/" target="_blank" rel="noopener">keep-scroll-sync</a> &middot; <a href="https://app.lideguang.com/snap-kit/" target="_blank" rel="noopener">snap-kit</a> &middot; <a href="https://app.lideguang.com/learn-vue/" target="_blank" rel="noopener">learn-vue</a> &middot; <a href="https://app.lideguang.com/merry-xmas/" target="_blank" rel="noopener">merry-xmas</a> &middot; <a href="https://app.lideguang.com/single-page-app/" target="_blank" rel="noopener">single-page-app</a>
                </div>
                <div style="border-top: 1px dashed #d1d5db; margin: 12px auto; max-width: 60%; opacity: 0.3;"></div>
                <p>&copy; ${year} Li Deguang &middot; 
                <a href="https://app.lideguang.com" target="_blank" rel="noopener">App Dashboard</a> &middot; 
                <a href="https://github.com/Deguang" target="_blank" rel="noopener">GitHub</a> &middot; 
                <a href="https://x.com/deguang_li" target="_blank" rel="noopener">X</a></p>
            </footer>
        `;
    }
}
customElements.define('deguang-footer', DeguangFooter);
