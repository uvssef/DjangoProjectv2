from django.urls import path, include

urlpatterns = [
    path('', include('stat_app.urls')),
]
