from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from . import models


class UploadCSVLeitores(forms.Form):
    file = forms.FileField()
    
  
        
class ExemplarAdminForm(forms.ModelForm):
    quantidade = forms.IntegerField(
        label="Quantidade de Exemplares",
        required=False,
        min_value=1,
        help_text="Informe a quantidade de exemplares para cadastrar em lote.",
    )

    class Meta:
        model = models.Exemplar
        fields = "__all__"
