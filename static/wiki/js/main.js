console.log('JavaScript is running');
// Rest of your main.js code...

document.addEventListener('DOMContentLoaded', function() {
    const nav = document.querySelector('.main-nav');
    const hamburger = document.querySelector('.hamburger-menu');
    const slidingMenu = document.querySelector('.sliding-menu');
    const menuOverlay = document.querySelector('.menu-overlay');
    const contextMenu = document.querySelector('.context_menu');
    const contentHolder = document.querySelector('.content_holder');
    const featuredImage = document.querySelector('.featured-image');

    // Navigation background opacity
    function updateNavBackground() {
        if (!featuredImage) return;
        
        const featuredImageRect = featuredImage.getBoundingClientRect();
        const featuredImageBottom = featuredImageRect.bottom;
        const navHeight = nav.offsetHeight;
        
        if (featuredImageBottom <= navHeight) {
            nav.style.backgroundColor = 'rgba(0, 0, 0, 1)';
        } else {
            const scrollProgress = 1 - (featuredImageBottom - navHeight) / (featuredImage.offsetHeight - navHeight);
            const opacity = Math.min(Math.max(scrollProgress, 0), 1);
            nav.style.backgroundColor = `rgba(0, 0, 0, ${opacity})`;
        }
    }

    // Context menu positioning
    function updateContextMenuPosition() {
        if (!contextMenu || !contentHolder) return;
        
        const scrollPosition = window.scrollY;
        const navHeight = nav.offsetHeight;
        const contentTop = contentHolder.offsetTop;

        if (scrollPosition + navHeight >= contentTop) {
            contextMenu.classList.add('sticky');
            contextMenu.style.top = `${navHeight}px`;
        } else {
            contextMenu.classList.remove('sticky');
            contextMenu.style.top = `${contentTop}px`;
        }
    }

    // Mobile menu toggle
    function toggleMenu() {
        slidingMenu.classList.toggle('open');
        menuOverlay.classList.toggle('open');
        document.body.style.overflow = slidingMenu.classList.contains('open') ? 'hidden' : '';
    }

    // Event listeners
    window.addEventListener('scroll', updateNavBackground);
    window.addEventListener('scroll', updateContextMenuPosition);

    hamburger.addEventListener('click', toggleMenu);
    menuOverlay.addEventListener('click', toggleMenu);

    // Initial calls
    updateNavBackground();
    updateContextMenuPosition();
});
