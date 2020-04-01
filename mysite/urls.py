
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^polls/', include('polls.urls', namespace="pols")), #daca ruta incepe cu 'polls' => merge la polls/urls.py
    url(r'^admin/', admin.site.urls),
]
