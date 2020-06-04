from django import forms
from polls.models import Election, Choice
from django.contrib.admin import widgets
from django.contrib.admin.widgets import AdminSplitDateTime


class DateInput(forms.DateTimeField):
    input_type = 'date'

class ElectionForm(forms.ModelForm): #acest form il import in views.py
#pentru ca folosesc ModelForm, pot declara extra fields (choices):
    choice1 = forms.CharField(label = 'Choice1', max_length = 100, min_length = 3,
                               widget = forms.TextInput(attrs = {'class': 'form-control'}))

    choice2 = forms.CharField(label = 'Choice2', max_length = 100, min_length = 3,
                               widget = forms.TextInput(attrs = {'class': 'form-control'}))

    class Meta: #pt a defini datele actuale ale clasei
        model= Election
        fields=['election_title','election_content','start_date','end_date','isActive']
        #model.start_date=forms.DateField(widget = DateInput) #ca sa selectez data din calendar
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets= {
            'election_title':forms.Textarea(attrs = {"class":"form-control", "rows":3,"cols":20}),
           # 'start_date':DateInput(),
            'isActive':forms.CheckboxInput()
            }


class EditElectionForm(forms.ModelForm):
    class Meta:  # pt a defini datele actuale ale clasei
        model = Election
        fields = ['election_title', 'election_content', 'start_date', 'end_date', 'isActive']
        # model.start_date=forms.DateField(widget = DateInput) #ca sa selectez data din calendar
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets = {
            'election_title': forms.Textarea(attrs = {"class": "form-control", "rows": 3, "cols": 20}),
            # 'start_date':DateInput(),
            'isActive': forms.CheckboxInput()
            }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model=Choice
        fields=['choice_text']
