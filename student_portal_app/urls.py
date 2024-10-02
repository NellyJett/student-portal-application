from django.urls import path
from student_portal_app.views import(
    home,
    # notes,
    # conversation,
    # todo,
    # homework,
    wiki,
    dictionary,
    youtube,
    register,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    # path('notes/', notes, name='notes'),
    # path('conversation/', conversation, name='convasation'),
    # path('todo/', todo, name='todo'),
    # path('homework', homework, name='homework'),
    path('wiki/', wiki, name='wiki'),
    path('dictionary/', dictionary, name='dictionary'),
    # path('notes', notes, name='notes'),
    path('youtube', youtube, name='youtube'),
]