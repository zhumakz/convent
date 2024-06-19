from django.test import TestCase, Client
from django.urls import reverse
from .models import User, City


class AccountsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(name="Test City")
        self.user = User.objects.create_user(
            phone_number="1234567890",
            name="John",
            surname="Doe",
            age=30,
            city=self.city,
            password="password"
        )

    def test_registration_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')

        data = {
            'phone_number': '0987654321',
            'name': 'Jane',
            'surname': 'Doe',
            'age': 25,
            'city': self.city.id
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(phone_number='0987654321').exists())

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Test with existing user
        data = {
            'phone_number': self.user.phone_number,
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_login'))

        # Test with non-existing user
        data = {
            'phone_number': '0000000000',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь не найден')

    def test_verify_login_view(self):
        self.client.post(reverse('login'), {'phone_number': self.user.phone_number})
        sms_code = self.client.session['sms_code']

        response = self.client.post(reverse('verify_login'), {'sms_code': sms_code})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_profile_view(self):
        self.client.login(phone_number=self.user.phone_number, password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_edit_view(self):
        self.client.login(phone_number=self.user.phone_number, password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'John',
            'surname': 'Doe',
            'age': 31,
            'city': self.city.id,
            'profile_picture': ''
        }
        response = self.client.post(reverse('profile_edit'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 31)

    def test_logout_view(self):
        self.client.login(phone_number=self.user.phone_number, password='password')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
