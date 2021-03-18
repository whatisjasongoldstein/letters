# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Newsletter, Source, Entry


class SourceInline(admin.StackedInline):
    model = Source
    extra = 0
    readonly_fields = ["last_updated", "num_unsent_entries"]


def sync(modeladmin, request, queryset):
    for obj in queryset:
        obj.update_sources()
sync.short_description = "Sync Sources Now"


def send(modeladmin, request, queryset):
    for obj in queryset:
        obj.send()
send.short_description = "Send Newsletter Now"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ["email", "last_sent", "num_unsent_entries"]
    inlines = [SourceInline, ]
    readonly_fields = ["last_sent", "num_unsent_entries"]
    actions = [sync, send, ]


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "source", "sent", "downloaded"]
    list_filter = ["source", "author"]
    search_fields = ["title", "author", ]
    ordering = ["-downloaded", ]

