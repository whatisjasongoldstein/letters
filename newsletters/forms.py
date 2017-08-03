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

    class Meta:
        model = Source
        fields = ('name', 'url', 'delete', )
