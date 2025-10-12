document.addEventListener('DOMContentLoaded', () => {
    const featureCards = document.querySelectorAll('.feature-card');
    const themeWrapper = document.getElementById('theme-wrapper');
    const themeToggleBtn = document.getElementById('theme-toggle');

    // --- 1. Theme Toggle Logic ---
    const savedTheme = localStorage.getItem('theme');
    
    // Function to set the theme
    const setTheme = (theme) => {
        if (theme === 'dark') {
            themeWrapper.classList.add('dark-mode');
            themeToggleBtn.innerHTML = '🌙'; // Moon icon for dark mode
        } else {
            themeWrapper.classList.remove('dark-mode');
            themeToggleBtn.innerHTML = '☀️'; // Sun icon for light mode
        }
    };

    // Apply saved theme on load, or default to light
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Default to light mode if no preference is saved
        setTheme('light'); 
    }

    // Toggle button event listener
    themeToggleBtn.addEventListener('click', () => {
        if (themeWrapper.classList.contains('dark-mode')) {
            setTheme('light');
            localStorage.setItem('theme', 'light');
        } else {
            setTheme('dark');
            localStorage.setItem('theme', 'dark');
        }
    });


    // --- 2. Feature Card Animation Logic (Updated for Squared Look) ---
    featureCards.forEach(card => {
        // Function to handle the mouse movement (3D tilt is disabled)
        function handleMouseMove(e) {
            // No 3D transformation
            card.style.transform = `none`; 
        }

        // Function to reset the card style
        function handleMouseLeave() {
            card.style.transform = `none`;
            card.style.boxShadow = 'none'; // Ensure shadow is gone
            card.style.borderColor = 'var(--color-card-border)'; // Reset border
        }

        // Add event listeners
        card.addEventListener('mousemove', handleMouseMove);
        card.addEventListener('mouseleave', handleMouseLeave);
        
        // Handle subtle lift and accent border on hover
        card.addEventListener('mouseenter', () => {
             card.style.borderColor = 'var(--color-accent)'; 
             // In light mode, shadow is 'none'. In dark mode, CSS will apply the glow via :hover.
             card.style.boxShadow = 'none'; 
             card.style.transform = 'translateY(-3px)'; // Apply subtle CSS lift
        });
        
        card.addEventListener('mouseleave', () => {
             card.style.borderColor = 'var(--color-card-border)';
             card.style.boxShadow = 'none';
             card.style.transform = 'none';
        });
    });
});