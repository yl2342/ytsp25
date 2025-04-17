// Main JavaScript for Yale Trading Simulation Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Stock detail page - Trade form quantity validation
    const tradeForm = document.getElementById('trade-form');
    if (tradeForm) {
        const quantityInput = document.getElementById('quantity');
        const actionSelect = document.getElementById('action');
        const maxShares = parseFloat(document.getElementById('user-shares')?.dataset?.shares || 0);
        
        // Update validation based on buy/sell action
        if (actionSelect) {
            actionSelect.addEventListener('change', function() {
                if (this.value === 'sell') {
                    if (quantityInput) quantityInput.setAttribute('max', maxShares);
                    if (quantityInput) quantityInput.setAttribute('data-bs-toggle', 'tooltip');
                    if (quantityInput) quantityInput.setAttribute('data-bs-placement', 'top');
                    if (quantityInput) quantityInput.setAttribute('title', `Maximum: ${maxShares} shares`);
                    if (quantityInput) new bootstrap.Tooltip(quantityInput);
                } else {
                    if (quantityInput) quantityInput.removeAttribute('max');
                    const tooltip = quantityInput ? bootstrap.Tooltip.getInstance(quantityInput) : null;
                    if (tooltip) {
                        tooltip.dispose();
                    }
                    if (quantityInput) quantityInput.removeAttribute('data-bs-toggle');
                    if (quantityInput) quantityInput.removeAttribute('title');
                }
            });
        }
        
        // Form validation
        tradeForm.addEventListener('submit', function(e) {
            if (actionSelect.value === 'sell' && parseFloat(quantityInput.value) > maxShares) {
                e.preventDefault();
                alert(`You can only sell a maximum of ${maxShares} shares.`);
            }
        });
    }

    // Stock detail page - Update stock price periodically
    const stockPriceElement = document.getElementById('current-price');
    if (stockPriceElement) {
        const ticker = stockPriceElement.dataset.ticker;
        
        // Periodically update the stock price (every 30 seconds)
        setInterval(function() {
            fetchStockPrice(ticker);
        }, 30000);
        
        // Fetch stock price and update UI
        function fetchStockPrice(ticker) {
            fetch(`/api/stock/price/${ticker}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const oldPrice = parseFloat(stockPriceElement.dataset.price);
                        const newPrice = data.price;
                        
                        stockPriceElement.dataset.price = newPrice;
                        stockPriceElement.textContent = `$${newPrice.toFixed(2)}`;
                        
                        // Show price change indication
                        if (newPrice > oldPrice) {
                            stockPriceElement.classList.remove('price-down');
                            stockPriceElement.classList.add('price-up');
                            setTimeout(() => stockPriceElement.classList.remove('price-up'), 1000);
                        } else if (newPrice < oldPrice) {
                            stockPriceElement.classList.remove('price-up');
                            stockPriceElement.classList.add('price-down');
                            setTimeout(() => stockPriceElement.classList.remove('price-down'), 1000);
                        }
                        
                        // Update hidden price input in trade form
                        const priceInput = document.getElementById('price');
                        if (priceInput) {
                            priceInput.value = newPrice;
                        }
                    }
                })
                .catch(error => console.error('Error fetching stock price:', error));
        }
    }

    // Social interaction - Like/Dislike posts via AJAX
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const counterElement = this.querySelector('.counter');
            const isLike = this.classList.contains('like-btn');
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.text())
            .then(html => {
                // Update the counter
                counterElement.outerHTML = html;
                
                // Toggle button classes
                if (isLike) {
                    this.classList.toggle('btn-outline-primary');
                    this.classList.toggle('btn-primary');
                } else {
                    this.classList.toggle('btn-outline-secondary');
                    this.classList.toggle('btn-secondary');
                }
            })
            .catch(error => console.error('Error updating like/dislike:', error));
        });
    });

    // Toggle comment replies
    document.querySelectorAll('.toggle-replies').forEach(button => {
        button.addEventListener('click', function() {
            const repliesContainer = document.getElementById(`replies-${this.dataset.commentId}`);
            if (repliesContainer) {
                repliesContainer.classList.toggle('d-none');
                this.textContent = repliesContainer.classList.contains('d-none') 
                    ? 'Show Replies' 
                    : 'Hide Replies';
            }
        });
    });

    // Initialize any stock charts on the page
    initializeStockCharts();
});

// Initialize stock price charts
function initializeStockCharts() {
    const chartCanvas = document.getElementById('stock-price-chart');
    if (!chartCanvas) return;
    
    const ticker = chartCanvas.dataset.ticker;
    const historicalDataStr = chartCanvas.dataset.history;
    
    try {
        const historicalData = JSON.parse(historicalDataStr);
        
        if (!historicalData || historicalData.length === 0) {
            console.error('No historical data available');
            return;
        }
        
        const dates = historicalData.map(item => item.date);
        const prices = historicalData.map(item => item.close);
        
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: `${ticker} Price`,
                    data: prices,
                    borderColor: '#0f4d92',
                    backgroundColor: 'rgba(15, 77, 146, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `$${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 10
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing stock chart:', error);
    }
} 