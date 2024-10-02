from django.shortcuts import render, redirect
import requests
import wikipedia
from youtubesearchpython import VideosSearch
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from student_portal_app.forms import(
    DashboardForm,
    UserRegistrationForm,
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
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        url = "https://googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pagecount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }

            result_list.append(result_dict)
            context = {
                'form':form,
                'results':result_list,
            }
            return render(request, 'dashboard/books.html', context)
        else:
            form = DashboardForm()
            return render(request, 'dashboard/books.html', {'form':form})



