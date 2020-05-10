
from django.contrib import admin
from django.conf.urls import url, include


urlpatterns = [
    url(r'^polls/', include('polls.urls', namespace="polls")), #daca ruta incepe cu 'polls' => merge la polls/urls.py
    url(r'^admin/', admin.site.urls),
    url(r'^home/', include('menu.urls', namespace="menu")),
]
