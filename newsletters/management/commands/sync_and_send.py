from django.core.management.base import BaseCommand, CommandError
from newsletters.tasks import sync_all, send_newsletters

class Command(BaseCommand):
    help = 'Syncs all sources and sends newsletter'

    def handle(self, *args, **options):
        sync_all()
        sent = send_newsletters()
        if sent:
            messages = []
            for nl, num in sent.items():
                messages.append("Sent %s entries to %s" % (num, nl))
            msg = "\n".join(messages)
        else:
            msg = "Nothing to send."
        self.stdout.write(self.style.SUCCESS(msg))
