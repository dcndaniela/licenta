from django import forms
from accounts.models import CustomUser as User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator


class RegisterForm(forms.Form):
    # folosesc widgets pt stilizare fields
    cnp = forms.CharField(label='CNP', max_length=13, min_length=13,
                               widget=forms.TextInput(attrs={'class':'form-control'}),
                               validators=[MinLengthValidator(13, message ="CNP should have 13 digits!"),
                                           MaxLengthValidator(13, message = "CNP should have 13 digits!"),
                                           RegexValidator(r'^[0-9]+$', 'Enter a valid CNP!')])
    phone= forms.CharField(label='Phone', max_length=10, min_length=10,
                            widget=forms.TextInput(attrs={'class':'form-control'}),
                            validators=[MinLengthValidator(10, message ="Phone number should have 10 digits!"),
                                        MaxLengthValidator(10, message = "Phone number should have 10 digits!"),
                                        RegexValidator(r'^07[0-9]+$', 'Enter a valid Phone number!')])
    password1 = forms.CharField(label = 'Password', max_length = 100, min_length=10,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}),
                                validators = [MinLengthValidator(10, message = "Password must have at least 10 characters!"),
                                              RegexValidator(r'^[a-z]+[A-Z][0-9][_!+-?*]+$',
                                                             message='Password must contain at least one Upper case,'
                                                                     ' one digit and one _!+-?* symbol!')]
                                )
    password2 = forms.CharField(label = 'Confirm Password', max_length = 100, min_length=10,
                                widget=forms.PasswordInput(attrs={'class':'form-control'}),
                                validators = [MinLengthValidator(10, message = "Password must have at least 10 characters!"),
                                              RegexValidator(r'^[a-z][A-Z][0-9][_!+-?*]+$',
                                                             message='Password must contain at least one Upper case,'
                                                                     ' one digit and one _!+-?* symbol!')]
                                )

# format:   clean_ + nume_field

    def clean_cnp(self):
        cnp=self.cleaned_data['cnp']
        qs = User.objects.filter(cnp = cnp)
        if qs.exists():
            raise ValidationError('CNP is already registered!')
        return cnp

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        qs = User.objects.filter(phone = phone)
        if qs.exists():
            raise ValidationError('Phone number is already registered!')
        return phone

    def clean_password2(self):
        p1 = self.cleaned_data['password1']
        p2 = self.cleaned_data['password2']
        if p1 != p2:
            raise ValidationError('Passwords do not match!')
        return p2

    #
    # def clean(self): #clean pe form (asa trebuie sa fac at cand am 2 fields interdependente)
    #     cleaned_data=super().clean()
    #     p1=cleaned_data.get('password1') #get cauta key=password1 in cleaned_data; intoarce None daca nu exista
    #     p2 = cleaned_data.get('password2')
    #     if p1 and p2:#daca exista ( adica nu sunt None)
    #         if p1!=p2:
    #             raise forms.ValidationError('Passwords Do Not Match')
    #             # raise forms.ValidationError( #NON_FIELD_ERRORS
    #             #     _('Passwords do not match !'),#fiind clean pe form, mesajul va aparea deasupra TUTUROR fields
    #             #     code = 'err2',
    #                #  )
    #             #raise ValidationError('Eroare parole')
    #
