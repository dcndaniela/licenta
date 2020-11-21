from django import forms
from polls.models import Election, Choice
from django.core.validators import RegexValidator, MinLengthValidator


class DateInput(forms.DateTimeField):
    input_type = 'date'

class ElectionForm(forms.ModelForm): #acest form il import in views.py
#pentru ca folosesc ModelForm, pot declara extra fields (choices):
    choice1 = forms.CharField(label = 'Choice1', max_length = 100, min_length = 5,
                               widget = forms.TextInput(attrs = {'class': 'form-control'}),
                               validators =[MinLengthValidator(5, message ="Choice text should have at least 5 characters!" ),
                                           RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Invalid format! You can use only letters and didgits') ] )

    choice2 = forms.CharField(label = 'Choice2', max_length = 100, min_length = 5,
                              widget = forms.TextInput(attrs = {'class': 'form-control'}),
                              validators = [
                                  MinLengthValidator(5, message = "Choice text should have at least 5 characters!"),
                                  RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid valid choice text!')]
                              )

    class Meta: #pt a defini datele actuale ale clasei
        model= Election
        fields=['election_title','election_content','start_date','end_date','isActive']
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets= {
            'election_title':forms.Textarea(attrs = {"class":"form-control", "rows":1,"cols":10}),
            'election_content': forms.Textarea(attrs = {"class":"form-control", "rows":1,"cols":10}),
            'isActive':forms.CheckboxInput()
                }

class EditElectionForm(forms.ModelForm):
    class Meta:  # pt a defini datele actuale ale clasei
        model = Election
        model.election_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        fields = ['election_title', 'election_content', 'start_date', 'end_date', 'isActive']
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets = {
            'election_title': forms.Textarea(attrs = {"class": "form-control", "rows": 1, "cols": 10}),
            'election_content': forms.Textarea(attrs = {"class": "form-control", "rows": 1, "cols": 10}),
            # 'start_date':DateInput(),
            'isActive': forms.CheckboxInput()
            }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model=Choice
        fields=['choice_text']


