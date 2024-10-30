document.addEventListener('DOMContentLoaded', function() {
    const nav = document.querySelector('.main-nav');
    const featuredImage = document.querySelector('.featured-image-container');
    const contextMenu = document.querySelector('.context_menu');
    const contentHolder = document.querySelector('.content_holder');
    let contextMenuInitialOffset = contentHolder.offsetTop;
    
    function updateContextMenuPosition() {
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

    // Add scroll listener for context menu position
    window.addEventListener('scroll', updateContextMenuPosition);

    // New function to toggle featured image visibility
    function toggleFeaturedImage() {
        featuredImage.classList.toggle('hidden');
        contentHolder.classList.toggle('no-featured-image');
        window.dispatchEvent(new CustomEvent('contentLayoutChange'));
    }

    // Recalculate contextMenuInitialOffset on window resize
    window.addEventListener('resize', function() {
        contextMenuInitialOffset = contentHolder.offsetTop;
        updateContextMenuPosition();
    });

    // Initial positioning of the context menu
    contextMenu.style.top = `${contentHolder.offsetTop}px`;

    const hamburger = document.querySelector('.hamburger-menu');
    const slidingMenu = document.querySelector('.sliding-menu');
    const menuOverlay = document.querySelector('.menu-overlay');
    const menuItems = document.querySelectorAll('.sliding-menu a');

    function toggleMenu() {
        slidingMenu.classList.toggle('open');
        menuOverlay.classList.toggle('open');
        
        // Add a small delay before showing menu items when opening
        if (slidingMenu.classList.contains('open')) {
            menuItems.forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('visible');
                }, 50); // Small delay for synchronization
            });
        } else {
            menuItems.forEach(item => {
                item.classList.remove('visible');
            });
        }
        
        document.body.style.overflow = slidingMenu.classList.contains('open') ? 'hidden' : '';
    }

    hamburger.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    });

    menuOverlay.addEventListener('click', toggleMenu);

    // Function to toggle login state
    function toggleLoginState() {
        const navComponent = document.getElementById('main-nav');
        if (navComponent.hasAttribute('logged-in')) {
            navComponent.removeAttribute('logged-in');
        } else {
            navComponent.setAttribute('logged-in', '');
        }
    }

    document.addEventListener('click', function(event) {
        if (event.target.closest('.login_btn') || event.target.closest('.dropdown-toggle')) {
            toggleLoginState();
        }
    });

    // Initial call to set opacity
    window.onscroll();
});