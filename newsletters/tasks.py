import asyncio
from .models import Newsletter, Source


async def sync(source_id):
    source = Source.objects.get(id=source_id)
    await asyncio.sleep(0)
    source.update()


def sync_all(newsletter=None):
    qs = Source.objects.all()
    if newsletter:
        qs = qs.filter(newsletter=newsletter)
    ids = list(qs.values_list("id", flat=True))

    # Sync each one asynchronously
    loop = asyncio.get_event_loop()
    tasks = [sync(i) for i in ids]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


def send_newsletters():
    """
    Sends all newsletters.
    Returns number of items sent.
    If 0, nothing was sent.
    """
    results = {}
    for newsletter in Newsletter.objects.all():
        num = newsletter.num_unsent_entries
        if num:
            newsletter.send()
            results[str(newsletter)] = num
    return results
