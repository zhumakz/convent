from django.apps import AppConfig

class CoinsConfig(AppConfig):
    name = 'coins'

    def ready(self):
        import coins.signals  # Подключение сигналов без запросов к базе данных
