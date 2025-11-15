from django.core.management.base import BaseCommand
from auth_app.models import User, UserRole

class Command(BaseCommand):
    help = 'Creates test users'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            email='admin@mail.ru',
            defaults={'name': 'Admin'}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            UserRole.objects.create(user=admin, role='admin')
            print('Admin has been created: admin@mail.ru / admin123')

        user, created = User.objects.get_or_create(
            email='user@mail.ru',
            defaults={'name': 'User'}
        )
        if created:
            user.set_password('user123')
            user.save()
            UserRole.objects.create(user=user, role='user')
            print('User has been created: user@mail.ru / user123')

