from django.db import models
from django.conf import settings

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='campaigns/logos/')
    main_photo = models.ImageField(upload_to='campaigns/main_photos/')
    leader_name = models.CharField(max_length=100)
    leader_photo = models.ImageField(upload_to='campaigns/leader_photos/')
    city = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Vote(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} voted for {self.campaign}'
