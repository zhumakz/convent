from django.apps import AppConfig


class StaticPagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'static_pages'

    # def ready(self):
    #     from .models import StaticPage
    #     StaticPage.create_static_pages()
