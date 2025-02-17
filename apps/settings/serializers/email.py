# coding: utf-8
# 

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

__all__ = ['MailTestSerializer', 'EmailSettingSerializer', 'EmailContentSettingSerializer']


class MailTestSerializer(serializers.Serializer):
    EMAIL_FROM = serializers.CharField(required=False, allow_blank=True)
    EMAIL_RECIPIENT = serializers.CharField(required=False, allow_blank=True)


class EmailSettingSerializer(serializers.Serializer):
    # encrypt_fields 现在使用 write_only 来判断了

    EMAIL_HOST = serializers.CharField(max_length=1024, required=True, label=_("SMTP host"))
    EMAIL_PORT = serializers.CharField(max_length=5, required=True, label=_("SMTP port"))
    EMAIL_HOST_USER = serializers.CharField(max_length=128, required=True, label=_("SMTP account"))
    EMAIL_HOST_PASSWORD = serializers.CharField(
        max_length=1024, write_only=True, required=False, label=_("SMTP password"),
        help_text=_("Tips: Some provider use token except password")
    )
    EMAIL_FROM = serializers.CharField(
        max_length=128, allow_blank=True, required=False, label=_('Send user'),
        help_text=_('Tips: Send mail account, default SMTP account as the send account')
    )
    EMAIL_RECIPIENT = serializers.CharField(
        max_length=128, allow_blank=True, required=False, label=_('Test recipient'),
        help_text=_('Tips: Used only as a test mail recipient')
    )
    EMAIL_USE_SSL = serializers.BooleanField(
        required=False, label=_('Use SSL'),
        help_text=_('If SMTP port is 465, may be select')
    )
    EMAIL_USE_TLS = serializers.BooleanField(
        required=False, label=_("Use TLS"),
        help_text=_('If SMTP port is 587, may be select')
    )
    EMAIL_SUBJECT_PREFIX = serializers.CharField(
        max_length=1024, required=True, label=_('Subject prefix')
    )


class EmailContentSettingSerializer(serializers.Serializer):
    EMAIL_CUSTOM_USER_CREATED_SUBJECT = serializers.CharField(
        max_length=1024, allow_blank=True, required=False,
        label=_('Create user email subject'),
        help_text=_('Tips: When creating a user, send the subject of the email (eg:Create account successfully)')
    )
    EMAIL_CUSTOM_USER_CREATED_HONORIFIC = serializers.CharField(
        max_length=1024, allow_blank=True, required=False,
        label=_('Create user honorific'),
        help_text=_('Tips: When creating a user, send the honorific of the email (eg:Hello)')
    )
    EMAIL_CUSTOM_USER_CREATED_BODY = serializers.CharField(
        max_length=4096, allow_blank=True, required=False,
        label=_('Create user email content'),
        help_text=_('Tips:When creating a user, send the content of the email')
    )
    EMAIL_CUSTOM_USER_CREATED_SIGNATURE = serializers.CharField(
        max_length=512, allow_blank=True, required=False, label=_('Signature'),
        help_text=_('Tips: Email signature (eg:jumpserver)')
    )
