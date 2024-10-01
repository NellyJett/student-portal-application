from django.urls import path
from student_portal_app.views import(
    register
)

urlpatterns = [
    path('', register, name='home')
]