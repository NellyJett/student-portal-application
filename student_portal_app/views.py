from django.shortcuts import render, get_object_or_404, redirect
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
from youtubesearchpython import VideosSearch
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from student_portal_app.forms import(
    DashboardForm,
    UserRegistrationForm,
    NotesForm,
    TodoForm,
    ConversationForm,
    ConversationLengthForm,
    ConversationMassForm
)
from student_portal_app.models import(
    Homework,
    Todo,
    Notes
)

def home(request):
    return render(request, 'dashboard/home.html')

def register(request):
    if request.method == "POST":
        u_form = UserRegistrationForm(request.POST)
        if u_form.is_valid():
            u_form.save()
            username = u_form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  
    else:
        u_form = UserRegistrationForm()

    return render(request, 'dashboard/register.html', {'form': u_form})


@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            note = Notes(
                user=request.user,
                title=request.POST['title'],  
                description=request.POST['description']
            )
            note.save()
            messages.success(request, f'Notes Added from {request.user.username}')
            return redirect('notes')  
    else:
        form = NotesForm()
    
    notes = Notes.objects.filter(user=request.user)

    context = {
        'form': form,
        'notes': notes
    }
    return render(request, 'dashboard/notes.html', context)


@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished = False, user= request.user)
    todos = Todo.objects.filter(is_finished = False, user= request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done == False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False

        context = {
            'homeworks':zip(homeworks, range(1, len(homeworks)+1)),
            'todos':zip(todos, range(1, len(todos)+1)),
            'homeworks_done':homeworks_done,
            'todos_done':todos_done
        }
        return render(request, 'dashboard/profile.html', context)


def wiki(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                # Retrieve the Wikipedia page based on the search term
                search = wikipedia.page(text)

                context = {
                    'form': form,
                    'title': search.title,
                    'link': search.url, 
                    'details': search.summary
                }

            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation error (multiple results found)
                context = {
                    'form': form,
                    'error': f"Multiple results found for '{text}': {e.options}"
                }

            except wikipedia.exceptions.PageError:
                # Handle error if the page doesn't exist
                context = {
                    'form': form,
                    'error': f"No results found for '{text}'"
                }

            return render(request, 'dashboard/wiki.html', context)

    else:
        form = DashboardForm()

    return render(request, 'dashboard/wiki.html', {'form': form}) 

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                # Perform YouTube search
                video = VideosSearch(text, limit=6)
                video_results = video.result()['result']

                result_list = []
                for i in video_results:
                    result_dict = {
                        'input': text,
                        'title': i.get('title', 'No title'),
                        'duration': i.get('duration', 'Unknown duration'),
                        'thumbnail': i['thumbnails'][0]['url'] if i.get('thumbnails') else '',
                        'channel': i['channel']['name'] if 'channel' in i else 'Unknown channel',
                        'link': i.get('link', '#'),
                        'views': i.get('viewCount', {}).get('short', 'Unknown views'),
                        'published': i.get('publishedTime', 'Unknown time'),
                        'description': ''
                    }

                    # Process description snippet if available
                    desc = ''
                    if 'descriptionSnippet' in i:
                        for j in i['descriptionSnippet']:
                            desc += j.get('text', '')
                        result_dict['description'] = desc

                    result_list.append(result_dict)

                return render(request, 'dashboard/youtube.html', {'form': form, 'results': result_list})

            except Exception as e:
                # Handle exceptions such as API errors
                error_message = f"An error occurred while fetching YouTube videos: {str(e)}"
                return render(request, 'dashboard/youtube.html', {'form': form, 'error': error_message})

    else:
        form = DashboardForm()

    return render(request, 'dashboard/youtube.html', {'form': form})


def dictionary(request):
    context = {}
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']

            url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"  
            r = requests.get(url)
            
            if r.status_code == 200:
                answer = r.json()

                try:
                    phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'N/A')
                    audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
                    definition = answer[0]['meanings'][0]['definitions'][0].get('definition', 'N/A')
                    example = answer[0]['meanings'][0]['definitions'][0].get('example', 'N/A')
                    synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])

                    context = {
                        'form': form,
                        'input': text,
                        'audio': audio,
                        'phonetics': phonetics,
                        'definition': definition,
                        'example': example,
                        'synonyms': synonyms
                    }

                except (IndexError, KeyError):
                    context = {
                        'form': form,
                        'input': text,
                        'error': "Word not found or missing information."
                    }

            else:
                context = {
                    'form': form,
                    'input': text,
                    'error': "Error fetching data from dictionary API."
                }
        else:
            context = {
                'form': form,
                'error': "Invalid form input."
            }
    else:
        form = DashboardForm()
        context = {'form': form}

    return render(request, 'dashboard/dictionary.html', context)


def books(request):
    form = DashboardForm()
    result_list = []

    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()  

        # Check if there are items in the response
        if 'items' in answer:
            for i in range(min(10, len(answer['items']))):  
                result_dict = {
                    'title': answer['items'][i]['volumeInfo']['title'],
                    'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                    'description': answer['items'][i]['volumeInfo'].get('description'),
                    'count': answer['items'][i]['volumeInfo'].get('pageCount'),  # Correct spelling to 'pageCount'
                    'categories': answer['items'][i]['volumeInfo'].get('categories'),
                    'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                    'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),  # Avoid KeyError
                    'preview': answer['items'][i]['volumeInfo'].get('previewLink')
                }
                result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,
        }
        return render(request, 'dashboard/books.html', context)

    return render(request, 'dashboard/books.html', {'form': form})

def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            finished = request.POST.get('is_finished') == 'on'
            todo_instance = form.save(commit=False)
            todo_instance.user = request.user
            todo_instance.is_finished = finished
            todo_instance.save()
            messages.success(request, f'Todo Added from {request.user.username}')
            return redirect('todo')
    else:
        form = TodoForm()
    
    todos = Todo.objects.filter(user=request.user)
    todos_done = not todos.exists()
    
    context = {
        'form': form,
        'todos': zip(todos, range(1, len(todos) + 1)),
        'todos_done': todos_done,
    }
    return render(request, 'dashboard/todo.html', context)



class NotesDetailView(generic.DetailView):
    template_name = 'dashboard/notes_detail.html'
    model = Notes


def delete_note(request, pk=None):
    Notes.objects.get(id = pk).delete()
    return redirect('notes')


def update_todo(request, pk=None):
    todo = Todo.objects.get(id = pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
        todo.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


def delete_todo(request, pk = None):
    Todo.objects.get(id = pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')

def homework(request, pk=None):
    Homework.objects.get(id = pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('homework')

def update_homework(request, pk=None):
    todo = Homework.objects.get(id = pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
        todo.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


def conversation(request):
    answer = ''
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        input_value = request.POST.get('input', '')
        
        if request.POST.get('measurement') == 'length':
            measurement_form = ConversationLengthForm()
            if input_value.isdigit() and int(input_value) >= 0:
                first = request.POST.get('measure1')
                second = request.POST.get('measure2')
                input_value = int(input_value)

                if first == 'yard' and second == 'foot':
                    answer = f'{input_value} yard(s) = {input_value * 3} foot/feet'
                elif first == 'foot' and second == 'yard':
                    answer = f'{input_value} foot/feet = {input_value / 3} yard(s)'

        elif request.POST.get('measurement') == 'mass':
            measurement_form = ConversationMassForm()
            if input_value.isdigit() and int(input_value) >= 0:
                first = request.POST.get('measure1')
                second = request.POST.get('measure2')
                input_value = int(input_value)

                if first == 'pound' and second == 'kilogram':
                    answer = f'{input_value} pound(s) ≈ {input_value * 0.453592:.2f} kilogram(s)'
                elif first == 'kilogram' and second == 'pound':
                    answer = f'{input_value} kilogram(s) ≈ {input_value / 0.453592:.2f} pound(s)'

        context = {
            'form': form,
            'm_form': measurement_form,
            'input': True,
            'answer': answer
        }

    else:
        form = ConversationForm()
        context = {
            'form': form,
            'input': False
        }

    return render(request, 'dashboard/conversation.html', context)


@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user=request.user, subject=request.POST['subject'], title=request.POST['title'], description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            homeworks.save()
            messages.success(
                request, f'Homework Added from {request.user.username}!')
    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    homeworks = zip(homeworks, range(1, len(homeworks)+1))
    context = {'form': form, 'homeworks': homeworks,
               'homeworks_done': homeworks_done}
    return render(request, 'dashboard/homework.html', context)