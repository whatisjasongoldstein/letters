from multiprocessing import Pool

from .models import Newsletter, Source


def sync(source_id):
    source = Source.objects.get(id=source_id)
    source.update()


def sync_all(newsletter=None):
    pool = Pool(5)
    qs = Source.objects.all()
    if newsletter:
        qs = qs.filter(newsletter=newsletter)
    ids = list(qs.values_list("id", flat=True))
    pool.map(sync, ids)


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
