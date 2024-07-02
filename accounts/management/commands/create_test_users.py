import random
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from accounts.models import User, City

FIRST_NAMES = [
    "Aibek", "Almas", "Anar", "Asel", "Ayan", "Baurzhan", "Bolat", "Dana", "Daulet", "Dinara",
    "Ermek", "Gulnar", "Kamila", "Karlygash", "Marat", "Murat", "Nurgul", "Nurlan", "Raushan", "Saule",
    "Serik", "Svetlana", "Talgat", "Yerzhan", "Zhanna"
]

LAST_NAMES = [
    "Akhmetov", "Alibekov", "Baizhanov", "Bektasov", "Dosmukhamedov", "Esimov", "Imanov", "Kairatov", "Kenzhebekov",
    "Kurmanov",
    "Makhambetov", "Mukashev", "Nurgaliyev", "Omarov", "Suleimenov", "Temirbekov", "Utegenov", "Zhaksylykov",
    "Zhanturin", "Zhumagulov"
]


class Command(BaseCommand):
    help = 'Create 10 test users with random names and phone numbers'

    def handle(self, *args, **kwargs):
        users_created = 0
        cities = list(City.objects.all())
        for i in range(10):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            phone_number = f'+77475{str(random.randint(100000, 999999)).zfill(6)}'
            username = f'{first_name.lower()}{last_name.lower()}{i}'
            email = f'{username}@example.com'
            password = get_random_string(length=10)
            city = random.choice(cities) if cities else None

            User.objects.create_user(
                phone_number=phone_number,
                name=first_name,
                surname=last_name,
                age=random.randint(18, 65),
                city=city,
                password=password,
            )
            users_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {users_created} users'))
