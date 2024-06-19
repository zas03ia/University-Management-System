from django.urls import path, include

urlpatterns = [
    path('', include('weapi.rest.urls.advising')),
    path('', include('weapi.rest.urls.department')),
]
