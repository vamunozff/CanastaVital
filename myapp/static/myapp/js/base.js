//Toggle

//let MenuBtn = document.getElementById('MenuBtn')

//MenuBtn.addEventListener('click', function(e){
 //   document.querySelector('body').classList.toggle('mobile-nav-active');
//    this.classList.toggle('fa-xmark')
//})

const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});