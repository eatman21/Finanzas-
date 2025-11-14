# Finansas - Financial Management System

A comprehensive Django-based financial management application for tracking debts, managing accounts, budgets, transactions, and achieving financial goals.

## Features

### Legacy Financial Management
- **Financial Profile**: Track monthly income, expenses, and calculate savings capacity
- **Debt Management**: Manage multiple debts (credit cards, personal loans, mortgages, etc.)
- **Financial Goals**: Set and track progress towards financial objectives
- **Credit Simulations**: Simulate loans with amortization tables and viability analysis
- **Smart Recommendations**: Get AI-powered financial advice

### Modern Financial Management
- **Multi-Account Support**: Manage checking, savings, credit cards, and investment accounts
- **Transaction Tracking**: Record income, expenses, and transfers with categories
- **Budget Planning**: Create monthly, quarterly, or yearly budgets
- **Category Management**: Organize transactions with hierarchical categories
- **Reports & Analytics**: Generate financial reports and visualizations

### RESTful API
- Complete REST API for all features
- Interactive API documentation (Swagger/ReDoc)
- Token-based authentication
- Filtering, search, and pagination support

## Tech Stack

- **Backend**: Django 4.2.11
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **API**: Django REST Framework with drf-spectacular
- **Forms**: django-crispy-forms with Bootstrap 5
- **Task Queue**: Celery with Redis
- **Testing**: pytest with coverage reporting
- **Code Quality**: black, flake8, isort, pre-commit
- **Visualization**: Plotly, django-chartjs
- **Data Export**: pandas, openpyxl, xlsxwriter

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL (for production)
- Redis (for background tasks)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/eatman21/Finanzas-.git
   cd finansas
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## API Documentation

When running in DEBUG mode, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=finanzas

# Generate HTML coverage report
pytest --cov=finanzas --cov-report=html
```

## Recent Updates

### November 2024
- ✅ Added comprehensive test suite
- ✅ Integrated drf-spectacular for API documentation
- ✅ Enhanced API with modern ViewSets for all models
- ✅ Fixed field reference errors in views
- ✅ Added pytest configuration with coverage reporting
- ✅ Created comprehensive .gitignore

## License

This project is licensed under the MIT License.
