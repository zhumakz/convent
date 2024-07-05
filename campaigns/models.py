from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from qrcode_generator.utils import generate_qr_code

class Campaign(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    logo = models.ImageField(upload_to='campaigns/logos/', verbose_name=_("Logo"), blank=True, null=True)
    main_photo = models.ImageField(upload_to='campaigns/main_photos/', blank=True, null=True, verbose_name=_("Main Photo"))
    leader_name = models.CharField(max_length=100, verbose_name=_("Leader Name"))
    leader_photo = models.ImageField(upload_to='campaigns/leader_photos/', blank=True, null=True, verbose_name=_("Leader Photo"))
    phone = models.CharField(max_length=100, verbose_name=_("Phone"))
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    qr_code = models.ImageField(upload_to='campaigns/qr_codes/', blank=True, null=True, verbose_name=_("QR Code"))

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        if not self.qr_code:
            qr_data = {"campaign_vote": self.id}
            filebuffer = generate_qr_code(qr_data, f"campaign_{self.id}_vote")
            self.qr_code.save(f"campaign_{self.id}_vote_qr.png", filebuffer, save=False)
    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    @staticmethod
    def create_default_campaigns():
        campaigns_data = [
            {"id": 1, "name": "Настоящий мужчина", "leader_name": "Ильяс", "phone": "+7 702 254 76 93"},
            {"id": 2, "name": "Antitrash", "leader_name": "Бауыржан", "phone": "87761812020"},
            {"id": 3, "name": "Халық қаһары", "leader_name": "Алихан", "phone": "87474645224"},
            {"id": 4, "name": "Ставки на Стоп", "leader_name": "Асем", "phone": "+7 747 616 46 70"},
            {"id": 5, "name": "Тілге сақтық", "leader_name": "Мади", "phone": "+7 705 201 38 70"},
            {"id": 6, "name": "ЖОҚ", "leader_name": "Ғазиза", "phone": "87782787622"},
            {"id": 7, "name": "Вандализм OFF", "leader_name": "Ақерке", "phone": "+7 702 826 26 15"},
            {"id": 8, "name": "Заң.Дүкендер", "leader_name": "Мирас", "phone": "87769773767"},
            {"id": 9, "name": "Зайцам - нет", "leader_name": "Алишер", "phone": "87082575303"},
            {"id": 10, "name": "Время истекло", "leader_name": "Мадина", "phone": "+7 747 471 71 34"},
            {"id": 11, "name": "Город", "leader_name": "Қуаныш", "phone": "87064227667"},
            {"id": 12, "name": "Tumar", "leader_name": "Галия", "phone": "87089880954"},
        ]

        for data in campaigns_data:
            campaign, created = Campaign.objects.update_or_create(
                id=data['id'],
                defaults={
                    'name': data['name'],
                    'leader_name': data['leader_name'],
                    'phone': data['phone'],
                }
            )
            if created:
                print(f"Created campaign with id {data['id']}: {data['name']}")
            else:
                print(f"Updated campaign with id {data['id']}: {data['name']}")

class Vote(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='votes', on_delete=models.CASCADE, verbose_name=_("Campaign"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes', on_delete=models.CASCADE,
                             verbose_name=_("User"))
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Voted At"))

    def __str__(self):
        return f'{self.user} voted for {self.campaign}'

    class Meta:
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")
