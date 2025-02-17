# Generated by Django 3.1.12 on 2021-09-26 02:47
import django
from django.conf import settings
from django.db import migrations, models, transaction
from acls.models import LoginACL

LOGIN_CONFIRM_ZH = '登录复核'
LOGIN_CONFIRM_EN = 'Login confirm'

DEFAULT_TIME_PERIODS = [{'id': i, 'value': '00:00~00:00'} for i in range(7)]


def has_zh(name: str) -> bool:
    for i in name:
        if u'\u4e00' <= i <= u'\u9fff':
            return True
    return False


def migrate_login_confirm(apps, schema_editor):
    login_acl_model = apps.get_model("acls", "LoginACL")
    login_confirm_model = apps.get_model("authentication", "LoginConfirmSetting")

    with transaction.atomic():
        for instance in login_confirm_model.objects.filter(is_active=True):
            user = instance.user
            reviewers = instance.reviewers.all()
            login_confirm = LOGIN_CONFIRM_ZH if has_zh(user.name) else LOGIN_CONFIRM_EN
            date_created = instance.date_created.strftime('%Y-%m-%d %H:%M:%S')
            if reviewers.count() == 0:
                continue
            data = {
                'user': user,
                'name': f'{user.name}-{login_confirm} ({date_created})',
                'created_by': instance.created_by,
                'action': LoginACL.ActionChoices.confirm,
                'rules': {'ip_group': ['*'], 'time_period': DEFAULT_TIME_PERIODS}
            }
            instance = login_acl_model.objects.create(**data)
            instance.reviewers.set(reviewers)


def migrate_ip_group(apps, schema_editor):
    login_acl_model = apps.get_model("acls", "LoginACL")
    updates = list()
    with transaction.atomic():
        for instance in login_acl_model.objects.exclude(action=LoginACL.ActionChoices.confirm):
            instance.rules = {'ip_group': instance.ip_group, 'time_period': DEFAULT_TIME_PERIODS}
            updates.append(instance)
        login_acl_model.objects.bulk_update(updates, ['rules', ])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('acls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginacl',
            name='action',
            field=models.CharField(choices=[('reject', 'Reject'), ('allow', 'Allow'), ('confirm', 'Login confirm')],
                                   default='reject', max_length=64, verbose_name='Action'),
        ),
        migrations.AddField(
            model_name='loginacl',
            name='reviewers',
            field=models.ManyToManyField(blank=True, related_name='login_confirm_acls',
                                         to=settings.AUTH_USER_MODEL, verbose_name='Reviewers'),
        ),
        migrations.AlterField(
            model_name='loginacl',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='login_acls', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.RunPython(migrate_login_confirm),
        migrations.AddField(
            model_name='loginacl',
            name='rules',
            field=models.JSONField(default=dict, verbose_name='Rule'),
        ),
        migrations.RunPython(migrate_ip_group),
        migrations.RemoveField(
            model_name='loginacl',
            name='ip_group',
        ),
    ]
