// const drinkDiv = document.querySelector('.drink');
const btn = document.querySelector("#add");
const drinkyList = document.querySelector("#drinky");
const drinkToAdd = document.querySelector("#drinkToAdd");

// append drinkToAdd to drinkyList
//eventlistener btn


document.addEventListener("DOMContentLoaded", function (event) {
  btn.addEventListener("click", pressIt);

  function pressIt() {
    add = drinkToAdd.innerText;
    drinkyList.append(add);
  }
});