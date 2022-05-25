import jwt
from datetime import timedelta, datetime
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models

from shop import settings
from django.dispatch import receiver
from django.urls import reverse

from django.core.mail import send_mail
from decouple import config

DOMAIN = config('DOMAIN')

class UserManager(BaseUserManager):
    def _create(self, email, password, name, last_name, **extra_fields):
        if not email:
            raise ValueError('Email cannot be empty')
        user = self.model(email=email, name=name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, name, last_name, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        return self._create(email, password, name, last_name, **extra_fields)

    def create_superuser(self, email, password, name, last_name, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        return self._create(email, password, name, last_name, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=8, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, obj):
        return self.is_staff

    @staticmethod
    def generate_activation_code():
        from django.utils.crypto import get_random_string
        code = get_random_string(8)
        return code

    def set_activation_code(self):
        code = self.generate_activation_code()
        if User.objects.filter(activation_code=code).exists():
            self.set_activation_code()
        else:
            self.activation_code = code
            self.save()

    def send_activation_email(self):
        activation_url = f'{DOMAIN}/api/v1/account/activate/{self.activation_code}/'
        message = f'''
                    Thank you for signing up.
                    Please, activate your account.
                    Activation link: {activation_url}
                    '''
        send_mail(
            'Activate your account',
            message,
            'test@makers.kg',
            [self.email, ],
            fail_silently=False
        )
    
    def send_verification_email(self):
        activation_url = f'{DOMAIN}/api/v1/account/forgot_password_complete/{self.email}/{self.activation_code}/'
        message = f'''
                    If you forgot your password, please follow this link:
                    {activation_url}
                    Otherwise, ignore this message
                    '''
        send_mail(
            'Forgot password',
            message,
            'test@makers.kg',
            [self.email, ],
            fail_silently=False
        )

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()


    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def send_new_password(self, new_password):
        message = f'Ваш новый пароль: {new_password}'
        send_mail(
            'Восстановление пароля',
            message,
            'test@gmail.com',
            [self.email]
        )
