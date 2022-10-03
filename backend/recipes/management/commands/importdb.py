from django.core.management.base import BaseCommand
from django.conf import settings
import json
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует в БД sqlite'

    def handle(self, *args, **kwargs):
        BASE_DIR = settings.BASE_DIR
        file = BASE_DIR + '\data\ingredients.json'
        with open(file, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            for i in data:
                ingredient = Ingredient(name=i['name'], measurement_unit=i['measurement_unit'])
                ingredient.save()
