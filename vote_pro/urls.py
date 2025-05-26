from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView  # <-- ajoute cette ligne

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vote_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
]

