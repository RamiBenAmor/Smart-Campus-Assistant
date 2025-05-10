const container = document.getElementById('container');
const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');

signUpButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
});
// Wait until page fully loads
window.addEventListener("load", function () {
    const loader = document.getElementById("loader-wrapper");
    loader.classList.add("fade-out");
  
    // Optional: remove the loader from DOM after fade-out
    setTimeout(() => {
      loader.style.display = "none";
    }, 500);
  });
  
