from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import User, City
from .forms import RegistrationForm, LoginForm, VerificationForm, ProfileEditForm, ModeratorLoginForm
from .services import UserService


class AccountsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(name="Test City")
        self.user = User.objects.create_user(
            phone_number="+77475000795",
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
            'phone_number': '+77475000796',
            'name': 'Jane',
            'surname': 'Doe',
            'age': 25,
            'city': self.city.id
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(phone_number='+77475000796').exists())

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Test with existing user
        data = {
            'phone_number': self.user.phone_number,
        }
        response = self.client.post(reverse('login'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="verifyPopup"', html=True)

        # Test with non-existing user
        data = {
            'phone_number': '0000000000',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь с таким номером телефона не найден.')

        # Test with invalid phone number
        data = {
            'phone_number': 'invalid',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введите правильный номер телефона.')

    def test_verify_login_view(self):
        self.client.post(reverse('login'), {'phone_number': self.user.phone_number})
        session = self.client.session
        session['sms_code'] = '1234'
        session.save()

        response = self.client.post(reverse('verify_login'), {'sms_code': '1234'})
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


class FormTests(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="Test City")

    def test_registration_form(self):
        form_data = {
            'phone_number': '+77475000795',
            'name': 'John',
            'surname': 'Doe',
            'age': 30,
            'city': self.city.id
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form(self):
        form_data = {'phone_number': '+77475000795'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_verification_form(self):
        form_data = {'sms_code': '1234'}
        form = VerificationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_form(self):
        form_data = {
            'name': 'John',
            'surname': 'Doe',
            'age': 30,
            'city': self.city.id,
            'profile_picture': None
        }
        form = ProfileEditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_moderator_login_form(self):
        # Создадим пользователя с группами
        moderator_group = Group.objects.create(name='AddModerators')
        user = User.objects.create_user(
            phone_number="+77475000795",
            name="John",
            surname="Doe",
            age=30,
            password="password"
        )
        user.groups.add(moderator_group)

        form_data = {
            'phone_number': '+77475000795',
            'password': 'password'
        }
        form = ModeratorLoginForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)


class ServiceTests(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="Test City")
        self.user = User.objects.create_user(
            phone_number="+77475000795",
            name="John",
            surname="Doe",
            age=30,
            city=self.city,
            password="password"
        )

    def test_create_user(self):
        user = UserService.create_user(
            phone_number="+77475000796",
            name="Jane",
            surname="Doe",
            age=25,
            city=self.city,
            password="password"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number, "+77475000796")

    def test_verify_phone_number(self):
        self.assertTrue(UserService.verify_phone_number(self.user.phone_number))

    def test_get_user_by_phone_number(self):
        user = UserService.get_user_by_phone_number(self.user.phone_number)
        self.assertEqual(user, self.user)
