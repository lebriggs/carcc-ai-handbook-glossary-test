// Reset glossary tooltips when Back/Forward restores a cached page.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;

  document.querySelectorAll("a.glossary-link abbr").forEach((term) => {
    const tooltipId = term.getAttribute("aria-describedby");
    const tooltip = tooltipId
      ? document.getElementById(tooltipId)
      : null;

    // Let Material clear its own hover state and remove the tooltip.
    tooltip?.dispatchEvent(new MouseEvent("mouseleave"));
    term.dispatchEvent(new MouseEvent("mouseleave"));
  });
});