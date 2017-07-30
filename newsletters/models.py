# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import feedparser
import datetime
import premailer

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail


class Newsletter(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User)
    last_sent = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Newsletter for %s" % self.email

    def update_sources(self):
        for source in self.source_set.all():
            source.update()

    def get_unsent_entries(self):
        return Entry.objects.filter(sent=False, source__newsletter=self)

    def send(self):
        entries = self.get_unsent_entries()
        count = entries.count()
        authors = list(entries.values_list("author", flat=True).distinct())[:10]
        subject = "Letters from %s" % (", ".join("authors"))

        if not count:
            return

        html = render_to_string("email.html", {
            "number": count,
            "entries": entries,
        })

        html = premailer.Premailer(html).transform()

        send_mail(
            "Your Letters collection is here (%s)!" % count,
            html,
            'portfolios@scruffylogic.com',
            [self.email],
            html_message=html,
            fail_silently=False,
        )

        entries.update(sent=True)


class Source(models.Model):
    newsletter = models.ForeignKey(Newsletter, null=True)
    name = models.CharField(max_length=255)
    url = models.URLField()
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Source"

    def save(self, *args, **kwargs):
        # Mark read the first time to avoid
        # collecting everything, ever.
        if not self.pk:
            self.update(mark_read=True)
        super(Source, self).save(*args, **kwargs)

    def update(self, mark_read=False):
        data = feedparser.parse(self.url)
        for entry in data["entries"]:
            obj, created = Entry.objects.get_or_create(
                source=self,
                url=entry["link"],
                defaults={
                    "title": entry["title"],
                    "author": entry["author"],
                    "summary": entry["summary"],
                    "sent": mark_read,
                })
        self.last_updated = datetime.datetime.now()
        self.save()


class Entry(models.Model):
    source = models.ForeignKey(Source)
    downloaded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=255)
    summary = models.TextField(default="")
    sent = models.BooleanField(default=False)
    url = models.URLField()

    def __str__(self):
        return "%s: %s" % (self.author, self.title)

