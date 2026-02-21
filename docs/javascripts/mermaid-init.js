// Re-initialize Mermaid diagrams on mkdocs-material instant navigation
// Material loads pages via XHR, so DOMContentLoaded doesn't fire again.
// The document$ observable notifies on every page load/navigation.
document$.subscribe(function() {
  if (typeof mermaid !== "undefined") {
    mermaid.run();
  }
});
