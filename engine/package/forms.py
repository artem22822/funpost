from django import forms
from engine import models


class RequestForm(forms.ModelForm):
    class Meta:
        model = models.Request
        fields = [
            'uuid', 'model', 'agency', 'package',
            'comment'
        ]
