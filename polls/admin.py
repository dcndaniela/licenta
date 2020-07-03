from django.contrib import admin
from .models import Election,Choice, ValidVote, Vote,  Trustee
from django.contrib.auth.models import Group
from accounts.models import CustomUser

admin.site.unregister(Group)
admin.site.register(CustomUser) #ca sa fie vizibile pt Admin
admin.site.register(ValidVote)
admin.site.register(Vote)
admin.site.register(Choice)
admin.site.register(Trustee)

admin.site.site_header='Admin Dashboard'

class InLineChoices(admin.TabularInline):
    model= Choice
    extra= 2 # nr minim de choices by default (Admin poate adauga mai multe )
    max_num= 7 # nr maxim de choices

class ElectionAdmin(admin.ModelAdmin): # admin.ModelAdmin = clasa din care mosteneste electionAdmin
    inlines = [InLineChoices] #contine lista claselor care mostenesc din clasa InLine
    list_display = ('election_title','start_date','end_date')
    list_filter = ('isActive',)
    list_editable=('start_date','end_date')
    search_fields = ('election_title',)
    date_hierarchy = 'start_date' #filtru
    fields= (
        'owner',
        'election_title',
        'election_content',
        'start_date',
        'end_date',
        'isActive',
        'public_key',
        'secret_key',
        'p',
        'q',
        'g',
        )

admin.site.register(Election, ElectionAdmin)
