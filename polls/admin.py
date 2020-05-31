from django.contrib import admin
from .models import Question,Choice
from django.contrib.auth.models import Group, User

#admin.site.register(Question)  #ca sa fie vizibile pt Admin
#admin.site.register(Choice)#ca sa fie vizibile pt Admin
admin.site.unregister(Group)

admin.site.site_header='Admin Dashboard'
#admin.site.unregister(User)

class InLineChoices(admin.TabularInline):
    model= Choice
    extra= 2 # nr minim de choices by default (Admin poate adauga mai multe )
    max_num= 7 # nr maxim de choices

class QuestionAdmin(admin.ModelAdmin): # admin.ModelAdmin = clasa din care mosteneste QuestionAdmin
    inlines = [InLineChoices] #contine lista claselor care mostenesc din clasa InLine
    list_display = ('question_title','start_date','end_date')
    list_filter = ('isActive',)
    list_editable=('start_date','end_date')
    search_fields = ('question_title',)
    date_hierarchy = 'start_date' #filtru
    fields= (
        'question_title',
        'question_content',
        'pub_date',
        'start_date',
        'end_date',
        'isActive',
        )

#admin.site.register(User, QuestionAdmin)

admin.site.register(Question,QuestionAdmin)
