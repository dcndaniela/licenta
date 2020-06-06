from django.contrib import admin
from .models import Election,Choice, AuditedBallot, CastVote
from django.contrib.auth.models import Group, User
from accounts.models import CustomUser

#admin.site.register(Election)  #ca sa fie vizibile pt Admin
#admin.site.register(Choice)#ca sa fie vizibile pt Admin
admin.site.unregister(Group)
admin.site.register(CustomUser)
admin.site.register(AuditedBallot)
admin.site.register(CastVote)
#admin.site.register(Choice)

admin.site.site_header='Admin Dashboard'
#admin.site.unregister(User)

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
        'pub_date',
        'start_date',
        'end_date',
        'isActive',
        )

#admin.site.register(User, electionAdmin)

admin.site.register(Election, ElectionAdmin)
