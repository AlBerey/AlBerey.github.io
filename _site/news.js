
async function loadNews() {
  const response = await fetch("news.json");
  if (!response.ok) {
    console.error("Cannot load news.json");
    return;
  }

  const news = await response.json();

  const cutoff = new Date();
  cutoff.setMonth(cutoff.getMonth() - 6);

  news.sort((a, b) => b.date.localeCompare(a.date));

  const recent = document.getElementById("recent-news");
  const archive = document.getElementById("news-archive");

  function renderItem(item) {
    const row = document.createElement("p");

    const date = document.createElement("strong");
    date.textContent = new Date(item.date + "T00:00:00")
      .toLocaleDateString("en-US", {
        month: "short",
        year: "numeric"
      }) + " — ";

    row.appendChild(date);
    row.appendChild(document.createTextNode(item.text));

    if (item.links && item.links.length > 0) {
      for (const link of item.links) {
        row.appendChild(document.createTextNode(" "));

        const a = document.createElement("a");
        a.href = link.url;
        a.textContent = link.label;
        a.target = "_blank";
        a.rel = "noopener noreferrer";

        row.appendChild(a);
      }
    }

    return row;
  }

  for (const item of news) {
    const itemDate = new Date(item.date + "T00:00:00");

    if (itemDate >= cutoff && recent) {
      recent.appendChild(renderItem(item));
    } else if (itemDate < cutoff && archive) {
      archive.appendChild(renderItem(item));
    }
  }
}

document.addEventListener("DOMContentLoaded", loadNews);

document.addEventListener("DOMContentLoaded", () => {
  const footerYear = document.getElementById("footer-year");
  if (footerYear) footerYear.textContent = new Date().getFullYear();
});
