// VibeMart Main JavaScript

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('alert-dismissible')) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }
        });
    }, 5000);

    // Initialize any existing functionality
    initializeCartFunctionality();
    initializeQuantityControls();
    initializeImagePreview();
});

// Cart Functionality
function initializeCartFunctionality() {
    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = this.dataset.quantity || 1;
            addToCart(productId, quantity);
        });
    });
}

// Add product to cart
async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch('/add-to-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        const data = await response.json();
        
        if (data.success) {
            updateCartCount(data.cart_count);
            showNotification('Product added to cart!', 'success');
        } else {
            showNotification(data.message || 'Error adding product to cart', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error adding product to cart', 'error');
    }
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        cartCountElement.classList.add('animate__animated', 'animate__pulse');
    }
}

// Initialize quantity controls
function initializeQuantityControls() {
    const quantityControls = document.querySelectorAll('.quantity-controls');
    quantityControls.forEach(control => {
        const decreaseBtn = control.querySelector('.quantity-decrease');
        const increaseBtn = control.querySelector('.quantity-increase');
        const input = control.querySelector('.quantity-input');

        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value);
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    updateCartItem(input.dataset.cartItemId, input.value);
                }
            });
        }

        if (increaseBtn) {
            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value);
                const maxStock = parseInt(input.dataset.maxStock) || 99;
                if (currentValue < maxStock) {
                    input.value = currentValue + 1;
                    updateCartItem(input.dataset.cartItemId, input.value);
                }
            });
        }

        if (input) {
            input.addEventListener('change', function() {
                const value = parseInt(this.value);
                const maxStock = parseInt(this.dataset.maxStock) || 99;
                if (value < 1) {
                    this.value = 1;
                } else if (value > maxStock) {
                    this.value = maxStock;
                }
                updateCartItem(this.dataset.cartItemId, this.value);
            });
        }
    });
}

// Update cart item quantity
async function updateCartItem(cartItemId, quantity) {
    try {
        const response = await fetch('/update-cart-item/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                cart_item_id: cartItemId,
                quantity: quantity
            })
        });

        const data = await response.json();
        
        if (data.success) {
            updateCartTotals(data.cart_total, data.item_total);
        } else {
            showNotification(data.message || 'Error updating cart', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error updating cart', 'error');
    }
}

// Update cart totals
function updateCartTotals(cartTotal, itemTotal) {
    const cartTotalElement = document.getElementById('cart-total');
    const itemTotalElements = document.querySelectorAll('.item-total');
    
    if (cartTotalElement) {
        cartTotalElement.textContent = `$${cartTotal}`;
    }
    
    itemTotalElements.forEach(element => {
        if (element.dataset.itemId === itemTotal.item_id) {
            element.textContent = `$${itemTotal.total}`;
        }
    });
}

// Initialize image preview for file uploads
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('image-preview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                     type === 'error' ? 'alert-danger' : 
                     type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }
        }, 3000);
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Loading spinner utility
function showLoadingSpinner(element) {
    const originalText = element.textContent;
    element.innerHTML = '<span class="spinner"></span> Loading...';
    element.disabled = true;
    return originalText;
}

function hideLoadingSpinner(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            } else {
                if (searchResults) {
                    searchResults.style.display = 'none';
                }
            }
        });
    }
}

// Perform search
async function performSearch(query) {
    try {
        const response = await fetch(`/search/?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        const searchResults = document.getElementById('search-results');
        if (searchResults && data.results) {
            displaySearchResults(data.results);
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Display search results
function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-3">No products found</div>';
    } else {
        const resultsHTML = results.map(product => `
            <div class="search-result-item p-2">
                <a href="/shop/product/${product.id}/" class="text-decoration-none">
                    <div class="d-flex align-items-center">
                        <img src="${product.image || '/static/images/placeholder.jpg'}" 
                             alt="${product.name}" class="me-2" style="width: 40px; height: 40px; object-fit: cover;">
                        <div>
                            <div class="fw-bold">${product.name}</div>
                            <div class="text-muted small">$${product.price}</div>
                        </div>
                    </div>
                </a>
            </div>
        `).join('');
        
        searchResults.innerHTML = resultsHTML;
    }
    
    searchResults.style.display = 'block';
}

// Wallet functionality
function addMoneyToWallet() {
    const amount = prompt('Enter amount to add to wallet:');
    if (amount && !isNaN(amount) && parseFloat(amount) > 0) {
        fetch('/accounts/add-money/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                amount: parseFloat(amount)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showNotification(data.message || 'Error adding money', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error adding money to wallet', 'error');
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
}); 