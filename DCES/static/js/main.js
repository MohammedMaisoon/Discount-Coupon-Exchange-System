document.addEventListener("DOMContentLoaded", function() {
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }
    
    // Flash message dismissal
    const closeButtons = document.querySelectorAll('.close-btn');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.opacity = '0';
            setTimeout(() => {
                this.parentElement.style.display = 'none';
            }, 300);
        });
    });

    // Tabs functionality
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and tab contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            
            // Add active class to current tab and tab content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Admin tabs functionality
    const adminTabs = document.querySelectorAll('.admin-tab');
    
    adminTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and tab contents
            document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.admin-content').forEach(tc => tc.classList.remove('active'));
            
            // Add active class to current tab and tab content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Expiration date highlighting
    const expiryDates = document.querySelectorAll('.expiry-date');
    
    expiryDates.forEach(date => {
        const expiryDate = new Date(date.getAttribute('data-date'));
        const today = new Date();
        const diffDays = Math.round((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (diffDays <= 7 && diffDays >= 0) {
            date.classList.add('expiring-soon');
            date.innerHTML += ' <span>(Expiring soon!)</span>';
        }
    });
});

// Coupon code copy functionality
function copyCode(element) {
    const codeElement = element;
    const code = codeElement.innerText;
    
    navigator.clipboard.writeText(code).then(() => {
        // Change the message
        const originalText = codeElement.innerHTML;
        codeElement.innerHTML = 'Copied!';
        
        // Reset after 2 seconds
        setTimeout(() => {
            codeElement.innerHTML = originalText;
        }, 2000);
    }, (err) => {
        console.error('Could not copy text: ', err);
    });
}

// Star rating functionality
function setRating(rating) {
    document.getElementById('ratingValue').value = rating;
    const stars = document.querySelectorAll('.star');
    
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}