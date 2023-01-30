const modal = document.body.querySelector(".modal");

const showText = document.body.querySelector("#show-text");
showText.addEventListener("click", () => {
  modal.style.visibility = "visible";
});

const hideText = document.body.querySelector("#hide-text");
hideText.addEventListener("click", () => {
  modal.style.visibility = "hidden";
});