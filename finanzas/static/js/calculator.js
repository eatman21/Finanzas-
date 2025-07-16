// Modern Financial Calculator JavaScript
class FinancialCalculator {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.setupAnimations();
        this.loadSavedData();
    }

    initializeElements() {
        // Input elements
        this.propertyValue = document.getElementById('property-value');
        this.downPayment = document.getElementById('down-payment');
        this.interestRate = document.getElementById('interest-rate');
        this.loanTerm = document.getElementById('loan-term');
        this.additionalCosts = document.getElementById('additional-costs');
        this.monthlyIncome = document.getElementById('monthly-income');
        this.monthlyExpenses = document.getElementById('monthly-expenses');

        // Range sliders
        this.downPaymentRange = document.getElementById('down-payment-range');
        this.interestRateRange = document.getElementById('interest-rate-range');
        this.loanTermRange = document.getElementById('loan-term-range');

        // Display elements
        this.downPaymentDisplay = document.getElementById('down-payment-display');
        this.interestRateDisplay = document.getElementById('interest-rate-display');
        this.loanTermDisplay = document.getElementById('loan-term-display');

        // Results elements
        this.resultsSection = document.getElementById('results-section');
        this.monthlyPayment = document.getElementById('monthly-payment');
        this.totalPayment = document.getElementById('total-payment');
        this.totalInterest = document.getElementById('total-interest');
        this.loanAmount = document.getElementById('loan-amount');
        this.viabilityIndicator = document.getElementById('viability-indicator');
        this.viabilityIcon = document.getElementById('viability-icon');
        this.viabilityText = document.getElementById('viability-text');

        // Buttons
        this.calculateBtn = document.getElementById('calculate-btn');
        this.resetBtn = document.getElementById('reset-btn');

        // Amortization table
        this.amortizationTable = document.getElementById('amortization-table');
    }

    bindEvents() {
        // Real-time range slider updates
        this.downPaymentRange.addEventListener('input', (e) => {
            this.updateDownPayment(e.target.value);
        });

        this.interestRateRange.addEventListener('input', (e) => {
            this.updateInterestRate(e.target.value);
        });

        this.loanTermRange.addEventListener('input', (e) => {
            this.updateLoanTerm(e.target.value);
        });

        // Input field updates
        this.propertyValue.addEventListener('input', () => this.updateCalculations());
        this.downPayment.addEventListener('input', () => this.updateCalculations());
        this.interestRate.addEventListener('input', () => this.updateCalculations());
        this.loanTerm.addEventListener('input', () => this.updateCalculations());
        this.additionalCosts.addEventListener('input', () => this.updateCalculations());
        this.monthlyIncome.addEventListener('input', () => this.updateCalculations());
        this.monthlyExpenses.addEventListener('input', () => this.updateCalculations());

        // Button events
        this.calculateBtn.addEventListener('click', () => this.performCalculation());
        this.resetBtn.addEventListener('click', () => this.resetCalculator());

        // Auto-save on input
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => this.saveData());
        });
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Observe elements for animation
        document.querySelectorAll('.calculator-card, .result-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease-out';
            observer.observe(el);
        });
    }

    updateDownPayment(value) {
        const propertyValue = parseFloat(this.propertyValue.value) || 0;
        const downPaymentAmount = (propertyValue * value / 100);

        this.downPayment.value = downPaymentAmount.toFixed(2);
        this.downPaymentDisplay.textContent = `${value}%`;
        this.updateCalculations();
    }

    updateInterestRate(value) {
        this.interestRate.value = value;
        this.interestRateDisplay.textContent = `${value}%`;
        this.updateCalculations();
    }

    updateLoanTerm(value) {
        this.loanTerm.value = value;
        this.loanTermDisplay.textContent = `${value} años`;
        this.updateCalculations();
    }

    updateCalculations() {
        // Real-time calculation updates
        const propertyValue = parseFloat(this.propertyValue.value) || 0;
        const downPaymentAmount = parseFloat(this.downPayment.value) || 0;
        const loanAmount = propertyValue - downPaymentAmount;

        if (loanAmount > 0) {
            this.loanAmount.textContent = this.formatCurrency(loanAmount);
        }
    }

    performCalculation() {
        this.showLoading();

        // Simulate calculation delay for better UX
        setTimeout(() => {
            const results = this.calculateLoan();
            this.displayResults(results);
            this.hideLoading();
            this.saveData();
        }, 800);
    }

    calculateLoan() {
        const propertyValue = parseFloat(this.propertyValue.value) || 0;
        const downPaymentAmount = parseFloat(this.downPayment.value) || 0;
        const interestRate = parseFloat(this.interestRate.value) || 0;
        const loanTerm = parseFloat(this.loanTerm.value) || 0;
        const additionalCosts = parseFloat(this.additionalCosts.value) || 0;
        const monthlyIncome = parseFloat(this.monthlyIncome.value) || 0;
        const monthlyExpenses = parseFloat(this.monthlyExpenses.value) || 0;

        const loanAmount = propertyValue - downPaymentAmount;
        const monthlyRate = interestRate / 100 / 12;
        const numberOfPayments = loanTerm * 12;

        let monthlyPayment = 0;
        if (monthlyRate > 0) {
            monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
                (Math.pow(1 + monthlyRate, numberOfPayments) - 1);
        } else {
            monthlyPayment = loanAmount / numberOfPayments;
        }

        const totalPayment = monthlyPayment * numberOfPayments + additionalCosts;
        const totalInterest = totalPayment - loanAmount - additionalCosts;
        const monthlyCapacity = monthlyIncome - monthlyExpenses;
        const isViable = monthlyPayment <= monthlyCapacity * 0.35; // 35% rule

        return {
            monthlyPayment,
            totalPayment,
            totalInterest,
            loanAmount,
            isViable,
            monthlyCapacity,
            amortizationSchedule: this.calculateAmortizationSchedule(loanAmount, monthlyRate, numberOfPayments, monthlyPayment)
        };
    }

    calculateAmortizationSchedule(principal, monthlyRate, numberOfPayments, monthlyPayment) {
        const schedule = [];
        let balance = principal;

        for (let month = 1; month <= Math.min(numberOfPayments, 12); month++) {
            const interest = balance * monthlyRate;
            const principalPayment = monthlyPayment - interest;
            balance -= principalPayment;

            schedule.push({
                month,
                payment: monthlyPayment,
                principal: principalPayment,
                interest,
                balance: Math.max(0, balance)
            });
        }

        return schedule;
    }

    displayResults(results) {
        // Update result cards with animation
        this.animateValue(this.monthlyPayment, results.monthlyPayment);
        this.animateValue(this.totalPayment, results.totalPayment);
        this.animateValue(this.totalInterest, results.totalInterest);
        this.animateValue(this.loanAmount, results.loanAmount);

        // Update viability indicator
        this.updateViabilityIndicator(results.isViable, results.monthlyPayment, results.monthlyCapacity);

        // Show results section
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Generate amortization table
        this.generateAmortizationTable(results.amortizationSchedule);
    }

    animateValue(element, targetValue) {
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const currentValue = startValue + (targetValue - startValue) * this.easeOutQuart(progress);
            element.textContent = this.formatCurrency(currentValue);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    updateViabilityIndicator(isViable, monthlyPayment, monthlyCapacity) {
        const maxAffordable = monthlyCapacity * 0.35;

        if (isViable) {
            this.viabilityIcon.className = 'viability-icon viable fas fa-check-circle';
            this.viabilityText.textContent = '¡Crédito Viable!';
            this.viabilityIndicator.className = 'viability-indicator viable';
        } else {
            this.viabilityIcon.className = 'viability-icon not-viable fas fa-times-circle';
            this.viabilityText.textContent = 'Crédito No Viable';
            this.viabilityIndicator.className = 'viability-indicator not-viable';
        }

        // Add detailed information
        const details = document.createElement('div');
        details.className = 'viability-details';
        details.innerHTML = `
            <small class="text-muted">
                Pago mensual: ${this.formatCurrency(monthlyPayment)} | 
                Capacidad máxima: ${this.formatCurrency(maxAffordable)}
            </small>
        `;

        const existingDetails = this.viabilityIndicator.querySelector('.viability-details');
        if (existingDetails) {
            existingDetails.remove();
        }
        this.viabilityIndicator.appendChild(details);
    }

    generateAmortizationTable(schedule) {
        const tbody = this.amortizationTable.querySelector('tbody');
        tbody.innerHTML = '';

        schedule.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.month}</td>
                <td>${this.formatCurrency(row.payment)}</td>
                <td>${this.formatCurrency(row.principal)}</td>
                <td>${this.formatCurrency(row.interest)}</td>
                <td>${this.formatCurrency(row.balance)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 2
        }).format(amount);
    }

    showLoading() {
        this.calculateBtn.innerHTML = '<span class="loading"></span> Calculando...';
        this.calculateBtn.disabled = true;
    }

    hideLoading() {
        this.calculateBtn.innerHTML = '<i class="fas fa-calculator me-2"></i>Calcular';
        this.calculateBtn.disabled = false;
    }

    resetCalculator() {
        // Reset all inputs
        const inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
        inputs.forEach(input => input.value = '');

        // Reset range sliders
        this.downPaymentRange.value = 20;
        this.interestRateRange.value = 10;
        this.loanTermRange.value = 20;

        // Reset displays
        this.downPaymentDisplay.textContent = '20%';
        this.interestRateDisplay.textContent = '10%';
        this.loanTermDisplay.textContent = '20 años';

        // Hide results
        this.resultsSection.style.display = 'none';

        // Clear saved data
        localStorage.removeItem('financialCalculatorData');
    }

    saveData() {
        const data = {
            propertyValue: this.propertyValue.value,
            downPayment: this.downPayment.value,
            interestRate: this.interestRate.value,
            loanTerm: this.loanTerm.value,
            additionalCosts: this.additionalCosts.value,
            monthlyIncome: this.monthlyIncome.value,
            monthlyExpenses: this.monthlyExpenses.value
        };
        localStorage.setItem('financialCalculatorData', JSON.stringify(data));
    }

    loadSavedData() {
        const savedData = localStorage.getItem('financialCalculatorData');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    element.value = data[key];
                }
            });

            // Update range sliders
            if (data.interestRate) {
                this.interestRateRange.value = data.interestRate;
                this.interestRateDisplay.textContent = `${data.interestRate}%`;
            }
            if (data.loanTerm) {
                this.loanTermRange.value = data.loanTerm;
                this.loanTermDisplay.textContent = `${data.loanTerm} años`;
            }
        }
    }
}

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FinancialCalculator();
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
}); 