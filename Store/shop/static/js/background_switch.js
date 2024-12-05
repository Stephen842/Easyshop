// Background Switcher.js

const modeSwitch = document.getElementById('modeSwitch');
const themeIcon = document.getElementById('themeIcon');

// Check for saved theme preference
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);

// Set the correct icon based on the current theme
themeIcon.className = currentTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';

modeSwitch.addEventListener('click', () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Change the icon based on the new theme
    themeIcon.className = newTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
});
