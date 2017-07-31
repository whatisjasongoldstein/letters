from django.core.management.base import BaseCommand, CommandError
from newsletters.models import Newsletter

class Command(BaseCommand):
    help = 'Syncs all sources and sends newsletter'

    def handle(self, *args, **options):
        for newsletter in Newsletter.objects.all():
            newsletter.update_sources()
            num = newsletter.num_unsent_entries
            if num:
                newsletter.send()
                msg = "Sent %s entries to %s" % (num, newsletter.email)
            else:
                msg = "Nothing to send %s" % newsletter.email
            self.stdout.write(self.style.SUCCESS(msg))
