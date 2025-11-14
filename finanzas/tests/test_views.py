"""
Tests for finanzas views
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from finanzas.legacy_models import PerfilFinanciero


class DashboardViewTest(TestCase):
    """Test cases for dashboard view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('finanzas:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_accessible_when_logged_in(self):
        """Test that dashboard is accessible when logged in"""
        response = self.client.get(reverse('finanzas:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finanzas/dashboard.html')


class PerfilFinancieroViewTest(TestCase):
    """Test cases for financial profile views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_perfil_creation_view(self):
        """Test that profile creation view works"""
        response = self.client.get(reverse('finanzas:perfil_financiero'))
        self.assertEqual(response.status_code, 200)


class AccountViewTest(TestCase):
    """Test cases for account views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_account_list_view(self):
        """Test account list view"""
        response = self.client.get(reverse('finanzas:account_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finanzas/account_list.html')

    def test_account_create_view_get(self):
        """Test account create view GET request"""
        response = self.client.get(reverse('finanzas:account_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finanzas/account_form.html')
