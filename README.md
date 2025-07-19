# Finansas - Financial Management Application

A comprehensive Django-based financial management application with multi-currency support, REST API, and modern UI.

## 🌟 Features

### 💰 Financial Management

- **Multi-Currency Support**: 100+ currencies including COP, MXN, USD, EUR, and more
- **Debt Tracking**: Monitor loans, credit cards, and other debts
- **Financial Goals**: Set and track savings goals
- **Credit Simulations**: Calculate loan payments and amortization tables
- **Financial Recommendations**: AI-powered financial advice

### 🚀 Technical Features

- **REST API**: Complete API for mobile apps and integrations
- **Modern UI**: Bootstrap 5 with responsive design
- **Real-time Calculations**: Interactive financial calculator
- **Data Export**: Excel/CSV export capabilities
- **Charts & Visualizations**: Interactive financial charts
- **Multi-language Support**: Spanish and English

### 🔒 Security & Performance

- **Production Ready**: Security settings and optimizations
- **Authentication**: User management and permissions
- **CORS Support**: Cross-origin request handling
- **Caching**: Redis-based caching
- **Logging**: Comprehensive logging system

## 🛠️ Technology Stack

- **Backend**: Django 4.2.11
- **Database**: PostgreSQL (production), SQLite (development)
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5, JavaScript, CSS3
- **Charts**: Plotly, Chart.js
- **Data Processing**: Pandas, OpenPyXL
- **Money Handling**: Django Money, Py-moneyed
- **Caching**: Redis
- **Deployment**: Gunicorn, WhiteNoise

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Redis (optional, for caching)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/finansas.git
cd finansas
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# For development
pip install -r requirements/development.txt

# For production
pip install -r requirements/production.txt
```

### 4. Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
finansas/
├── .env                    # Environment variables
├── .env.example           # Environment template
├── requirements/          # Split requirements by environment
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── finansas/             # Project configuration
│   ├── settings/         # Split settings by environment
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── finanzas/             # Financial app
│   ├── models/           # Split models into modules
│   ├── views/            # Split views by feature
│   ├── serializers/      # API serializers
│   ├── forms/            # Forms by feature
│   ├── tests/            # Comprehensive tests
│   └── utils/            # Utility functions
├── api/                  # API app
├── static/               # Project-wide static files
├── templates/            # Project-wide templates
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django settings
DJANGO_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=finansas_db
DB_USER=finansas_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (optional)
REDIS_URL=redis://127.0.0.1:6379/1
```

## 📚 API Documentation

### Authentication

All API endpoints require authentication. Use session authentication or basic authentication.

### Endpoints

#### Dashboard

- `GET /api/perfiles/dashboard/` - Get dashboard summary

#### Financial Profiles

- `GET /api/perfiles/` - List profiles
- `POST /api/perfiles/` - Create profile
- `GET /api/perfiles/{id}/` - Get profile details
- `PUT /api/perfiles/{id}/` - Update profile
- `DELETE /api/perfiles/{id}/` - Delete profile

#### Debts

- `GET /api/deudas/` - List debts
- `POST /api/deudas/` - Create debt
- `GET /api/deudas/summary/` - Get debt summary
- `GET /api/deudas/{id}/` - Get debt details
- `PUT /api/deudas/{id}/` - Update debt
- `DELETE /api/deudas/{id}/` - Delete debt

#### Financial Goals

- `GET /api/objetivos/` - List goals
- `POST /api/objetivos/` - Create goal
- `GET /api/objetivos/summary/` - Get goals summary
- `GET /api/objetivos/{id}/` - Get goal details
- `PUT /api/objetivos/{id}/` - Update goal
- `DELETE /api/objetivos/{id}/` - Delete goal

#### Credit Simulations

- `GET /api/simulaciones/` - List simulations
- `POST /api/simulaciones/` - Create simulation
- `GET /api/simulaciones/{id}/amortizacion/` - Get amortization table
- `GET /api/simulaciones/summary/` - Get simulations summary

#### Recommendations

- `GET /api/recomendaciones/` - List recommendations
- `GET /api/recomendaciones/active/` - Get active recommendations

## 🧪 Testing

Run tests with:

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=finanzas

# Run specific test file
python manage.py test finanzas.tests.test_models
```

## 🚀 Deployment

### Production Deployment

1. **Set Environment Variables**

   ```bash
   DJANGO_ENV=production
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ```

2. **Install Production Dependencies**

   ```bash
   pip install -r requirements/production.txt
   ```

3. **Collect Static Files**

   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

5. **Start Production Server**

   ```bash
   gunicorn finansas.wsgi:application
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email <support@finansas.com> or create an issue in the repository.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the UI components
- All contributors and users of this project

---

**Made with ❤️ for better financial management**
