from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#format:   clean_ + nume_field


class RegisterForm(forms.Form):
    # folosesc widgets pt stilizare fields
    username = forms.CharField(label='Username', max_length=100, min_length=5,
                               widget=forms.TextInput(attrs={'class':'form-control'}))
    email= forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label = 'Password', max_length = 100, min_length=8,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label = 'Confirm Password', max_length = 100, min_length=8,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean_email(self):#clean pe field-ul email
        emailUser= self.cleaned_data['email']
        qs= User.objects.filter(email=emailUser) #qs=query set;ma asiur ca email ul e unic
        if qs.exists():
            raise ValidationError(
                _('Email already used!'),#fiind clean pe field, mesajul apare deasupra fieldului
                code = 'err1',
                params = {'value': '42'},
                )
        return(emailUser)

    #def clean_password2(self): #arunca eroare daca folseam password1(referentia password2 care se crea dupa validarea lui password1)
      #  p1=self.cleaned_data['password1']
      #  p2=self.cleaned_data['password2']
      #  if p1 != p2:
      #      raise ValidationError('Password2 does not match password1!')
      #  return p2


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

