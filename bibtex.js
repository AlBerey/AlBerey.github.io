
async function copyBibtex(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  textarea.remove();

  if (!copied) throw new Error("Clipboard access was denied");
}

document.addEventListener("DOMContentLoaded", async () => {
  const links = document.querySelectorAll(".bibtex-copy");
  if (links.length === 0) return;

  let entries;

  try {
    const response = await fetch("bibtex.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    entries = await response.json();
  } catch (error) {
    console.error("Failed to load BibTeX entries:", error);
    return;
  }

  links.forEach(link => {
    link.addEventListener("click", async event => {
      event.preventDefault();

      const bibtex = entries[link.dataset.bibId];

      if (!bibtex) {
        console.error(
          "BibTeX entry not found:",
          link.dataset.bibId
        );
        link.textContent = "Not found";
        return;
      }

      try {
        await copyBibtex(bibtex);
        link.textContent = "Copied!";
      } catch (error) {
        console.error("Clipboard error:", error);
        link.textContent = "Copy failed";
      }
    });
  });
});
