from django import forms

from .models import Source

class SourceForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        # You can't delete things that aren't
        # yet saved.
        if not self.instance.id:
            self.fields["delete"].widget = forms.HiddenInput()

    def clean_url(self):
        """
        Unique together isn't being enforced
        at the form level. Force it.
        """
        url = self.cleaned_data['url']
        if Source.objects.filter(url=url).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("You already have this feed!")
        return url

    class Meta:
        model = Source
        fields = ('name', 'url', 'delete', )
