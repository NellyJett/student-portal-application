from django.urls import path
from student_portal_app.views import(
    home,
    notes,
    conversation,
    todo,
    # homework,
    wiki,
    dictionary,
    youtube,
    register,
    books,
    NotesDetailView,
    delete_note,
    delete_todo,
    profile,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('notes/', notes, name='notes'),
    path('conversation/', conversation, name='conversation'),
    path('todo/', todo, name='todo'),
    # path('homework', homework, name='homework'),
    path('wiki/', wiki, name='wiki'),
    path('dictionary/', dictionary, name='dictionary'),
    path('books', books, name='books'),
    path('youtube', youtube, name='youtube'),
    path('profile/', profile, name='profile'),
    path('note_detail/<int:pk>/', NotesDetailView.as_view(), name='note_detail'),
    path('delete_note/<int:pk>/', delete_note, name='delete-note'),
    path('delete_todo/<int:pk>/', delete_todo, name='delete-todo'),
]