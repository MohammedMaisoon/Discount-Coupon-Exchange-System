// Coupon filtering and search functionality
document.addEventListener("DOMContentLoaded", function() {
    const searchForm = document.getElementById('searchForm');
    const categoryFilter = document.getElementById('categoryFilter');
    const sortFilter = document.getElementById('sortFilter');
    const couponCards = document.querySelectorAll('.coupon-card');
    
    // Filter coupons by search term
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            couponCards.forEach(card => {
                const title = card.querySelector('.coupon-title').innerText.toLowerCase();
                const description = card.querySelector('.coupon-description').innerText.toLowerCase();
                const store = card.querySelector('.store-name').innerText.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm) || store.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Filter coupons by category
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const selectedCategory = this.value;
            
            if (selectedCategory === 'all') {
                couponCards.forEach(card => {
                    card.style.display = 'block';
                });
                
                return;
            }
            
            couponCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                if (cardCategory === selectedCategory) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Sort coupons
    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            const selectedSort = this.value;
            const couponGrid = document.querySelector('.grid-container');
            const couponCardsArray = Array.from(couponCards);
            
            if (selectedSort === 'newest') {
                couponCardsArray.sort((a, b) => {
                    const dateA = new Date(a.getAttribute('data-date'));
                    const dateB = new Date(b.getAttribute('data-date'));
                    return dateB - dateA;
                });
            } else if (selectedSort === 'expiring') {
                couponCardsArray.sort((a, b) => {
                    const dateA = new Date(a.getAttribute('data-expiry'));
                    const dateB = new Date(b.getAttribute('data-expiry'));
                    return dateA - dateB;
                });
            } else if (selectedSort === 'discount') {
                couponCardsArray.sort((a, b) => {
                    const discountA = parseFloat(a.getAttribute('data-discount'));
                    const discountB = parseFloat(b.getAttribute('data-discount'));
                    return discountB - discountA;
                });
            } else if (selectedSort === 'popular') {
                couponCardsArray.sort((a, b) => {
                    const ratingA = parseFloat(a.getAttribute('data-rating'));
                    const ratingB = parseFloat(b.getAttribute('data-rating'));
                    return ratingB - ratingA;
                });
            }
            
            // Remove all coupons
            couponCards.forEach(card => {
                card.remove();
            });
            
            // Append sorted coupons
            couponCardsArray.forEach(card => {
                couponGrid.appendChild(card);
            });
        });
    }
    
    // Coupon expiration countdown
    const countdownElements = document.querySelectorAll('.countdown');
    
    countdownElements.forEach(element => {
        const expiryDate = new Date(element.getAttribute('data-expiry'));
        
        // Update countdown every second
        const countdownInterval = setInterval(() => {
            const now = new Date();
            const distance = expiryDate - now;
            
            // Time calculations
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            // Display countdown
            if (distance < 0) {
                clearInterval(countdownInterval);
                element.innerHTML = 'EXPIRED';
                element.classList.add('expired');
            } else if (days > 0) {
                element.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            } else {
                element.innerHTML = `${hours}h ${minutes}m ${seconds}s`;
                element.classList.add('urgent');
            }
        }, 1000);
    });
});