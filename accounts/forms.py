from django import forms
from accounts.models import CustomUser as User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
#from accounts.models import CustomUser
#format:   clean_ + nume_field


class RegisterForm(forms.Form):
    # folosesc widgets pt stilizare fields
    cnp = forms.CharField(label='CNP', max_length=13, min_length=13,
                               widget=forms.TextInput(attrs={'class':'form-control'}),
                               validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid CNP.')])
    phone= forms.CharField(label='Phone', max_length=10, min_length=10,
                            widget=forms.TextInput(attrs={'class':'form-control'}),
                            validators=[RegexValidator(r'^07[0-9]+$', 'Enter a valid Phone number.')])
    password1 = forms.CharField(label = 'Password', max_length = 100, min_length=8,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label = 'Confirm Password', max_length = 100, min_length=8,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}))


    def clean(self): #clean pe form (asa trebuie sa fac at cand am 2 fields interdependente)
        cleaned_data=super().clean()
        p1=cleaned_data.get('password1') #get cauta key=password1 in cleaned_data; intoarce None daca nu exista
        p2 = cleaned_data.get('password2')

        if p1 and p2:#daca exista
            if p1!=p2:
                raise forms.ValidationError( #NON_FIELD_ERRORS
                    _('Passwords do not match !'),#fiind clean pe form, mesajul va aparea deasupra TUTUROR fields
                    code = 'err2',
                     )
                #raise ValidationError('Eroare parole')

