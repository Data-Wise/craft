// Re-initialize Mermaid diagrams on mkdocs-material instant navigation.
// fence_code_format produces <pre class="mermaid"><code>...</code></pre>.
// Mermaid expects <pre class="mermaid">...</pre> (no <code> wrapper).
// Transform the DOM, then call mermaid.run() on every page navigation.
document$.subscribe(function() {
  if (typeof mermaid === "undefined") return;
  document.querySelectorAll("pre.mermaid > code").forEach(function(code) {
    var pre = code.parentElement;
    pre.textContent = code.textContent;
  });
  mermaid.run();
});
