from . import views

from django.urls import path


app_name = 'linksapp'
urlpatterns = [
    path('', views.addemail, name='addemail'),
    path('token-auth/<uuid:rtoken>', views.token_auth, name='token_auth'),
    path('tokens', views.tokenslist, name='tokenslist'),
]
