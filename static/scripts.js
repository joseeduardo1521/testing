const loginBtn = document.getElementById('login');
const topacBtn = document.getElementById('topac');

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('topac').addEventListener('click', function (event) {
        event.preventDefault(); // Evita el comportamiento predeterminado del botón
        document.getElementById('loading-animation').style.display = 'block';
    });
});
