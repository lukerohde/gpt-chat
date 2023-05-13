import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Create an associated auth token for an existing superuser'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise CommandError(f'No such user "{username}"')

        token, _ = Token.objects.get_or_create(user=user)
        print(token.key)
