let btn = document.querySelector("#add");
const drinkyList = document.querySelector("#drinky");
const drinkToAdd = document.querySelector("#drinkToAdd");

// append drinkToAdd to drinkyList
//eventlistener btn

document.addEventListener("DOMContentLoaded", function (event) {
  
  function pressIt() {
    add = drinkToAdd.innerText;
    drinkyList.append(add);
  }
  if(drinkToAdd){
    btn.addEventListener("click", pressIt);
  }
  
});

