class IngredientAnalyzer {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.scanner = null;
        this.loadDummyHistory();
    }

    initializeElements() {
        // Buttons
        this.scanBtn = document.getElementById('scanBtn');
        this.manualBtn = document.getElementById('manualBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.compareBtn = document.getElementById('compareBtn');
        this.logoutBtn = document.getElementById('logoutBtn');

        // Containers
        this.ingredientInput = document.getElementById('ingredientInput');
        this.scannerView = document.getElementById('scannerView');
        this.resultsSection = document.getElementById('resultsSection');
        this.historyTableBody = document.getElementById('historyTableBody');

        // Modals
        this.analyzeModal = new bootstrap.Modal(document.getElementById('analyzeModal'));
        this.compareModal = new bootstrap.Modal(document.getElementById('compareModal'));
    }

    attachEventListeners() {
        this.scanBtn.addEventListener('click', () => this.toggleScanner(true));
        this.manualBtn.addEventListener('click', () => this.toggleManualInput(true));
        this.analyzeBtn.addEventListener('click', () => this.analyzeIngredients());
        this.compareBtn.addEventListener('click', () => this.compareProducts());
        this.logoutBtn.addEventListener('click', () => this.logout());
    }

    toggleScanner(show) {
        this.scannerView.classList.toggle('d-none', !show);
        this.ingredientInput.classList.add('d-none');
        
        if (show) {
            this.initializeScanner();
        } else if (this.scanner) {
            this.scanner.getTracks().forEach(track => track.stop());
        }
    }

    toggleManualInput(show) {
        this.ingredientInput.classList.toggle('d-none', !show);
        this.scannerView.classList.add('d-none');
        if (this.scanner) {
            this.scanner.getTracks().forEach(track => track.stop());
        }
    }

    async initializeScanner() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const videoElement = document.getElementById('scanner');
            videoElement.srcObject = stream;
            videoElement.play();
            this.scanner = stream;
        } catch (error) {
            console.error('Camera access error:', error);
            alert('Could not access camera. Please use manual input.');
            this.toggleManualInput(true);
        }
    }

    getDummyAnalysisData() {
        return {
            healthyPercentage: Math.floor(Math.random() * 41) + 60, // 60-100
            categories: [
                {
                    name: 'Natural Ingredients',
                    percentage: Math.floor(Math.random() * 31) + 50, // 50-80
                    ingredients: ['Water', 'Salt', 'Sugar', 'Wheat Flour']
                },
                {
                    name: 'Additives',
                    percentage: Math.floor(Math.random() * 16) + 5, // 5-20
                    ingredients: ['E100', 'E200', 'E300']
                },
                {
                    name: 'Preservatives',
                    percentage: Math.floor(Math.random() * 11) + 5, // 5-15
                    ingredients: ['Sodium Benzoate', 'Potassium Sorbate']
                },
                {
                    name: 'Artificial Colors',
                    percentage: Math.floor(Math.random() * 6) + 2, // 2-7
                    ingredients: ['Red 40', 'Yellow 5']
                }
            ],
            healthScore: Math.floor(Math.random() * 41) + 60, // 60-100
            warnings: [
                'Contains artificial colors',
                'High sodium content'
            ]
        };
    }

    async analyzeIngredients() {
        const data = this.getDummyAnalysisData();
        this.displayResults(data);
        this.analyzeModal.hide();
        this.addToHistory(data);
    }

    async compareProducts() {
        const product1 = this.getDummyAnalysisData();
        const product2 = this.getDummyAnalysisData();
        
        this.displayComparisonResults({
            product1,
            product2
        });
        
        this.compareModal.hide();
    }

    displayResults(data) {
        this.resultsSection.classList.remove('d-none');
        this.resultsSection.innerHTML = this.generateResultsHTML(data);
        this.initializeCharts(data);
    }

    generateResultsHTML(data) {
        return `
            <div class="card fade-in">
                <div class="card-body">
                    <h4 class="gradient-text text-center mb-4">Analysis Results</h4>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="text-center mb-4">
                                <h5 class="gradient-text">Health Score</h5>
                                <div class="circular-progress">
                                    <canvas id="healthScore"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h5 class="gradient-text mb-3">Ingredient Categories</h5>
                            <div id="categoryBars">
                                ${data.categories.map(category => `
                                    <div class="category-bar">
                                        <div class="d-flex justify-content-between mb-2">
                                            <span>${category.name}</span>
                                            <span class="gradient-text">${category.percentage}%</span>
                                        </div>
                                        <div class="category-progress">
                                            <div class="category-progress-fill" style="width: ${category.percentage}%"></div>
                                        </div>
                                        <small class="text-muted">${category.ingredients.join(', ')}</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    ${data.warnings.length ? `
                        <div class="mt-4">
                            <h5 class="gradient-text mb-3">Warnings</h5>
                            <ul class="list-unstyled">
                                ${data.warnings.map(warning => `
                                    <li><i class="bi bi-exclamation-triangle text-warning me-2"></i>${warning}</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    displayComparisonResults(data) {
        this.resultsSection.classList.remove('d-none');
        this.resultsSection.innerHTML = `
            <div class="card fade-in">
                <div class="card-body">
                    <h4 class="gradient-text text-center mb-4">Product Comparison</h4>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="gradient-text text-center mb-3">Product 1</h5>
                                    ${this.generateComparisonHTML(data.product1)}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="gradient-text text-center mb-3">Product 2</h5>
                                    ${this.generateComparisonHTML(data.product2)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Initialize charts for both products
        this.initializeCharts(data.product1, 'product1');
        this.initializeCharts(data.product2, 'product2');
    }

    generateComparisonHTML(data) {
        return `
            <div class="circular-progress mb-4">
                <canvas id="healthScore_${data.id || Math.random().toString(36).substr(2, 9)}"></canvas>
            </div>
            <div id="categoryBars">
                ${data.categories.map(category => `
                    <div class="category-bar">
                        <div class="d-flex justify-content-between mb-2">
                            <span>${category.name}</span>
                            <span class="gradient-text">${category.percentage}%</span>
                        </div>
                        <div class="category-progress">
                            <div class="category-progress-fill" style="width: ${category.percentage}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    initializeCharts(data, prefix = '') {
        const chartId = prefix ? `healthScore_${prefix}` : 'healthScore';
        const ctx = document.getElementById(chartId).getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Healthy', 'Unhealthy'],
                datasets: [{
                    data: [data.healthyPercentage, 100 - data.healthyPercentage],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(244, 67, 54, 0.8)'
                    ],
                    borderColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(244, 67, 54, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                cutout: '70%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
    }

    loadDummyHistory() {
        const dummyHistory = [
            { date: '2024-12-24', product: 'Cereal A', healthScore: 85 },
            { date: '2024-12-23', product: 'Snack B', healthScore: 65 },
            { date: '2024-12-22', product: 'Drink C', healthScore: 75 }
        ];

        this.historyTableBody.innerHTML = dummyHistory.map(item => `
            <tr>
                <td>${item.date}</td>
                <td>${item.product}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="category-progress me-2" style="width: 100px">
                            <div class="category-progress-fill" style="width: ${item.healthScore}%"></div>
                        </div>
                        <span>${item.healthScore}%</span>
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-light" onclick="analyzer.viewHistoryItem(${JSON.stringify(item)})">
                        View
                    </button>
                </td>
            </tr>
        `).join('');
    }

    addToHistory(data) {
        const today = new Date().toISOString().split('T')[0];
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${today}</td>
            <td>Product Analysis</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="category-progress me-2" style="width: 100px">
                        <div class="category-progress-fill" style="width: ${data.healthScore}%"></div>
                    </div>
                    <span>${data.healthScore}%</span>
                </div>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-light" onclick="analyzer.viewHistoryItem(${JSON.stringify(data)})">
                    View
                </button>
            </td>
        `;
        this.historyTableBody.insertBefore(newRow, this.historyTableBody.firstChild);
    }

    viewHistoryItem(data) {
        this.displayResults(data);
    }

    async logout() {
        try {
            const response = await fetch('/logout', {
                method: 'POST'
            });

            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
}

// Initialize the application
const analyzer = new IngredientAnalyzer();
