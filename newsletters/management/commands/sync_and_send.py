from django.core.management.base import BaseCommand, CommandError
from newsletters.models import Newsletter

class Command(BaseCommand):
    help = 'Syncs all sources and sends newsletter'

    def handle(self, *args, **options):
        for newsletter in Newsletter.objects.all():
            newsletter.update_sources()
            newsletter.send()
            self.stdout.write(self.style.SUCCESS('Sent to %s') % newsletter.email)
