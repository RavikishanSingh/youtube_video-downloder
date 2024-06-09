// JavaScript to trigger fade-out animation when leaving a page
document.addEventListener('DOMContentLoaded', function () {
    document.body.classList.add('fade-out');
});

// JavaScript to trigger fade-in animation when entering a new page
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        // If the page is cached, don't trigger animation
        return;
    }
    document.body.classList.remove('fade-out');
    document.body.classList.add('fade-in');
});
