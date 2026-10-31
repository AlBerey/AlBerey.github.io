document.addEventListener("DOMContentLoaded", function () {
  const logo = document.querySelector(".navbar-brand");
  if (logo) {
    logo.setAttribute("target", "_blank");
    logo.setAttribute("rel", "noopener noreferrer");
  }
});