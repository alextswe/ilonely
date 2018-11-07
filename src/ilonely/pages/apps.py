from django.apps import AppConfig


class pagesConfig(AppConfig):
    name = 'pages'

    def ready(self):
        import pages.signals