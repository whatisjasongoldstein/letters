# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests
import pytz
import json
import feedparser
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


class Newsletter(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_sent = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Newsletter for %s" % self.email

    def update_sources(self):
        for source in self.source_set.all():
            source.update()

    def get_unsent_entries(self):
        return Entry.objects.filter(sent=False, source__newsletter=self)

    @property
    def num_unsent_entries(self):
        return Entry.objects.filter(source__newsletter=self, sent=False).count()

    def send(self):
        entries = self.get_unsent_entries()
        count = entries.count()

        if not count:
            return

        authors = list(entries.values_list("author", flat=True).distinct())[:10]
        authors = ", ".join(authors)

        html = render_to_string("email.html", {
            "number": count,
            "entries": entries,
        })

        send_mail(
            "%s Letters from %s" % (count, authors),
            html,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html,
            fail_silently=False,
        )

        entries.update(sent=True)
        self.last_sent = datetime.datetime.now(pytz.utc)
        self.save()


class Source(models.Model):
    newsletter = models.ForeignKey(Newsletter, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    url = models.URLField()
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name', )
        unique_together = ('newsletter', 'url')

    def __str__(self):
        return self.name or "Source"

    @property
    def num_unsent_entries(self):
        return Entry.objects.filter(source=self, sent=False).count()

    def update(self, mark_read=False):
        # Brad Frost's feed starts with a newline,
        # throwing off feedparser.
        try:
            content = requests.get(self.url).content.strip()
        except requests.exceptions.ConnectionError:
            logger.error('Could not sync %s' % self.url)
            return

        data = feedparser.parse(content)
        
        for entry in data["entries"][:25]:
            obj, created = Entry.objects.get_or_create(
                source=self,
                url=entry["link"],
                defaults={
                    "title": entry["title"],
                    "author": (entry.get("author") or 
                               data["feed"].get("author") or
                               self.name),
                    "summary": entry["summary"],
                    "sent": mark_read,
                })
        self.last_updated = datetime.datetime.now(pytz.utc)
        self.save()

    def save(self, *args, **kwargs):
        is_new = not self.pk
        result = super(Source, self).save(*args, **kwargs)
        if is_new:
            self.update(mark_read=True)
        return result


class Entry(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    downloaded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=255)
    summary = models.TextField(default="")
    sent = models.BooleanField(default=False)
    url = models.URLField(max_length=2083)

    class Meta:
        verbose_name_plural = "Entries"

    def __str__(self):
        return "%s: %s" % (self.author, self.title)
