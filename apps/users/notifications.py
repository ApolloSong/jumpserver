from urllib.parse import urljoin

from django.utils import timezone
from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.loader import render_to_string

from common.utils import reverse, get_request_ip_or_data, get_request_user_agent
from notifications.notifications import UserMessage


class UserCreatedMsg(UserMessage):
    def get_html_msg(self) -> dict:
        user = self.user
        subject = _('Create account successfully')
        if settings.EMAIL_CUSTOM_USER_CREATED_SUBJECT:
            subject = settings.EMAIL_CUSTOM_USER_CREATED_SUBJECT

        honorific = settings.EMAIL_CUSTOM_USER_CREATED_HONORIFIC or _('Hello {}').format(user.name)
        signature = settings.EMAIL_CUSTOM_USER_CREATED_SIGNATURE or 'JumpServer'

        context = {
            'honorific': honorific,
            'signature':  signature,
            'username': user.username,
            'rest_password_url': reverse('authentication:reset-password', external=True),
            'rest_password_token': user.generate_reset_token(),
            'forget_password_url': reverse('authentication:forgot-password', external=True),
            'email': user.email,
            'login_url': reverse('authentication:login', external=True),
        }
        message = render_to_string('users/_msg_user_created.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        user = cls.get_test_user()
        return cls(user)


class ResetPasswordMsg(UserMessage):
    def __init__(self, user):
        super().__init__(user)
        self.reset_passwd_token = user.generate_reset_token()

    def get_html_msg(self) -> dict:
        user = self.user
        subject = _('Reset password')
        context = {
            'user': user,
            'rest_password_url': reverse('authentication:reset-password', external=True),
            'rest_password_token': self.reset_passwd_token,
            'forget_password_url': reverse('authentication:forgot-password', external=True),
            'login_url': reverse('authentication:login', external=True),
        }
        message = render_to_string('authentication/_msg_reset_password.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        user = User.objects.first()
        return cls(user)


class ResetPasswordSuccessMsg(UserMessage):
    def __init__(self, user, request):
        super().__init__(user)
        self.ip_address = get_request_ip_or_data(request)
        self.browser = get_request_user_agent(request)

    def get_html_msg(self) -> dict:
        user = self.user

        subject = _('Reset password success')
        context = {
            'name': user.name,
            'ip_address': self.ip_address,
            'browser': self.browser,
        }
        message = render_to_string('authentication/_msg_rest_password_success.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        factory = APIRequestFactory()
        request = Request(factory.get('/notes/'))
        user = User.objects.first()
        return cls(user, request)


class PasswordExpirationReminderMsg(UserMessage):
    def get_html_msg(self) -> dict:
        user = self.user
        subject = _('Password is about expire')

        date_password_expired_local = timezone.localtime(user.date_password_expired)
        update_password_url = urljoin(settings.SITE_URL, '/ui/#/users/profile/?activeTab=PasswordUpdate')
        date_password_expired = date_password_expired_local.strftime('%Y-%m-%d %H:%M:%S')
        context = {
            'name': user.name,
            'date_password_expired': date_password_expired,
            'update_password_url': update_password_url,
            'forget_password_url': reverse('authentication:forgot-password', external=True),
            'email': user.email,
            'login_url': reverse('authentication:login', external=True),
        }
        message = render_to_string('users/_msg_password_expire_reminder.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        user = User.objects.get(username='admin')
        return cls(user)


class UserExpirationReminderMsg(UserMessage):
    def get_html_msg(self) -> dict:
        subject = _('Account is about expire')
        date_expired_local = timezone.localtime(self.user.date_password_expired)
        date_expired = date_expired_local.strftime('%Y-%m-%d %H:%M:%S')
        context = {
            'name': self.user.name,
            'date_expired': date_expired
        }
        message = render_to_string('users/_msg_account_expire_reminder.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        user = User.objects.get(username='admin')
        return cls(user)


class ResetSSHKeyMsg(UserMessage):
    def get_html_msg(self) -> dict:
        subject = _('Reset SSH Key')
        update_url = urljoin(settings.SITE_URL, '/ui/#/users/profile/?activeTab=SSHUpdate')
        context = {
            'name': self.user.name,
            'url': update_url,
        }
        message = render_to_string('users/_msg_reset_ssh_key.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        user = User.objects.get(username='admin')
        return cls(user)


class ResetMFAMsg(UserMessage):
    def get_html_msg(self) -> dict:
        subject = _('Reset MFA')
        context = {
            'name': self.user.name,
            'url': reverse('authentication:user-otp-enable-start', external=True),
        }
        message = render_to_string('users/_msg_reset_mfa.html', context)
        return {
            'subject': subject,
            'message': message
        }

    @classmethod
    def gen_test_msg(cls):
        from users.models import User
        user = User.objects.get(username='admin')
        return cls(user)
