const container = document.querySelector('.carousel-container');
const prevButton = document.querySelector('.prev');
const nextButton = document.querySelector('.next');
//const addButtons = document.querySelectorAll('.add-btn');
const Popup = document.getElementById('fullscreen-popup');
const PopupImg = document.getElementById('fullscreen-popup-img');
const PopupTitle = document.getElementById('fullscreen-popup-title');
const PopupPrice = document.getElementById('fullscreen-popup-price');
const PopupDescription = document.getElementById('fullscreen-popup-description');
const closePopup = document.querySelector('.close-fullscreen');

prevButton.addEventListener('click', function() {
    container.scrollBy({
        left: -300, // Adjust scroll amount for better alignment
        behavior: 'smooth'
    });
});

nextButton.addEventListener('click', function() {
    container.scrollBy({
        left: 300, // Adjust scroll amount for better alignment
        behavior: 'smooth'
    });
});


container.addEventListener('wheel', (event) => {
    event.preventDefault();
    container.scrollBy({
        left: event.deltaY < 0 ? -100 : 100, // Adjust scroll amount
        behavior: 'smooth'
    });
});

// Show popup
// addButtons.forEach(button => {
//     button.addEventListener('click', function() {
//         const item = button.parentElement;
//         const title = item.getAttribute('data-title');
//         const price = item.getAttribute('data-price');
//         const description = item.getAttribute('data-description');
//         const imgSrc = item.getAttribute('data-img');
//
//         PopupImg.src = imgSrc;
//         PopupTitle.textContent = title;
//         PopupPrice.textContent = price;
//         PopupDescription.textContent = description;
//
//         Popup.style.display = 'block';
//     });
// });

closePopup.addEventListener('click', function() {
    Popup.style.display = 'none';
});

window.addEventListener('click', function(event) {
    if (event.target === Popup) {
        Popup.style.display = 'none';
    }
});
