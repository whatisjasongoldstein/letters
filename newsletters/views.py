# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower

from .models import Newsletter, Source, Entry
from .forms import SourceForm


def form_complete(request, msg, path="/"):
    messages.add_message(request, messages.SUCCESS, msg)
    return redirect(path)


@login_required
def dashboard(request):
    newsletter, _ = Newsletter.objects.get_or_create(user=request.user,
        defaults={
            "email": request.user.email,
        })

    # Set forms on existing sources
    sources = newsletter.source_set.all().order_by(Lower('name'))
    for source in sources:
        source.form = SourceForm(request.POST or None,
            instance=source,
            prefix="source-%s" % source.id)

        # Handle updates
        is_updating = False
        try:
            is_updating = (int(request.GET.get("update", None)) == source.id)
        except (ValueError, TypeError):
            pass

        if request.POST and is_updating and source.form.is_valid():

            # Handle deletes
            if source.form.cleaned_data["delete"]:
                source.delete()
                return form_complete(request, "Removed %s!" % source.name)

            source.form.save()
            source.refresh_from_db()
            return form_complete(request, "Updated %s!" % source.name)

    # Set up new source form
    add_form = SourceForm(request.POST or None, prefix="new-source",
        initial={"newsletter": newsletter})
    if add_form.is_valid():
        obj = add_form.save(commit=False)
        obj.newsletter = newsletter
        obj.save()
        return form_complete(request, "Added %s!" % obj.name)

    return render(request, "dashboard.html", {
        "newsletter": newsletter,
        "add_form": add_form,
        "sources": sources,
    })


@login_required
def preview(request):
    entries = Entry.objects.all()[:10]

    return render(request, "email.html", {
        "number": entries.count(),
        "entries": entries,
    })