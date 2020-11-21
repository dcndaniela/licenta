
from django.contrib import admin
from django.conf.urls import url, include


urlpatterns = [
    url(r'^voote5/', include('polls.urls', namespace="polls")), #daca ruta incepe cu 'polls' => merge la polls/urls.py
    url(r'^admin/', admin.site.urls, name="adm"),
    url(r'^accounts/', include('accounts.urls', namespace = "accounts")),  # pun namespace => pun app_name in accounts.urls

]
