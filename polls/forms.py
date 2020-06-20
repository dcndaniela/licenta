from django import forms
from polls.models import Election, Choice
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator


class DateInput(forms.DateTimeField):
    input_type = 'date'

class ElectionForm(forms.ModelForm): #acest form il import in views.py
#pentru ca folosesc ModelForm, pot declara extra fields (choices):
    choice1 = forms.CharField(label = 'Choice1', max_length = 100, min_length = 5,
                               widget = forms.TextInput(attrs = {'class': 'form-control'}),
                               validators =[MinLengthValidator(5, message ="Choice text should have at least 5 characters!" ),
                                           RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid valid choice text!') ] )

    choice2 = forms.CharField(label = 'Choice2', max_length = 100, min_length = 5,
                              widget = forms.TextInput(attrs = {'class': 'form-control'}),
                              validators = [
                                  MinLengthValidator(5, message = "Choice text should have at least 5 characters!"),
                                  RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid valid choice text!')]
                              )
    #start_date=forms.CharField(widget=forms.Textarea)
    class Meta: #pt a defini datele actuale ale clasei
        model= Election
        fields=['election_title','election_content','start_date','end_date','isActive']
        #model.start_date=forms.DateField(widget = DateInput) #ca sa selectez data din calendar
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets= {
            'election_title':forms.Textarea(attrs = {"class":"form-control", "rows":1,"cols":10}),
            'election_content': forms.Textarea(attrs = {"class":"form-control", "rows":1,"cols":10}),
            # 'start_date': forms.DateTimeField(),
            # 'end_date': forms.DateTimeField(),
            'isActive':forms.CheckboxInput()
                }
    #
    # def clean_start_date(self):
    #     start_date = self.cleaned_data['start_date']
    #     if (start_date<timezone.now()):
    #         raise ValidationError("Start date can not be in the past!")
    #     return start_date
    #
    #     def clean_end_date(self):
    #         start_date = self.cleaned_data['start_date']
    #         end_date = self.cleaned_data['end_date']
    #         if (end_date <= start_date):
    #             raise ValidationError("End date must be after start date!")
    #         return end_date



class EditElectionForm(forms.ModelForm):
    class Meta:  # pt a defini datele actuale ale clasei
        model = Election
        model.election_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        fields = ['election_title', 'election_content', 'start_date', 'end_date', 'isActive']
        # model.start_date=forms.DateField(widget = DateInput) #ca sa selectez data din calendar
        model.start_date = forms.DateTimeField()
        model.end_date = forms.DateTimeField()
        widgets = {
            'election_title': forms.Textarea(attrs = {"class": "form-control", "rows": 1, "cols": 10}),
            'election_content': forms.Textarea(attrs = {"class": "form-control", "rows": 1, "cols": 10}),
            # 'start_date':DateInput(),
            'isActive': forms.CheckboxInput()
            }

    # def clean_start_date(self):
    #     start_date = self.cleaned_data['start_date']
    #     if (start_date<timezone.now()):
    #         raise ValidationError("Start date can not be in the past!")
    #     return start_date
    #
    # def clean_end_date(self):
    #     start_dat = self.cleaned_data['start_date']
    #     end_dat = self.cleaned_data['end_date']
    #     if (end_dat <= start_dat):
    #         raise ValidationError("End date must be after start date!")
    #     return end_dat


class ChoiceForm(forms.ModelForm):
    class Meta:
        model=Choice
        fields=['choice_text']

