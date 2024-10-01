from django.shortcuts import render, redirect
import requests
import wikipedia
from youtubesearchpython import VideoSearch
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
    if request.method == 'POST':
        u_form = UserRegistrationForm(request.POST)
        if u_form.is_valid():
            u_form.save()
            username = u_form.clean_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
        else:
            u_form = UserRegistrationForm()
        return render(request, )
    

def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)

        context = {
            'form':form,
            'title':search.title,
            'link':search.link,
            'details':search.summary
        }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm
        return render(request, 'dashboard/wiki.html', {'form':form})
    

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            video = VideoSearch(text, limit=5)

            result_list = []
            for i in video.result()['result']:  
                result_dict = {
                    'input': text,
                    'title': i.get('title'),
                    'duration': i.get('duration'),
                    'thumbnail': i['thumbnails'][0]['url'] if i.get('thumbnails') else '',
                    'channel': i['channel']['name'],
                    'link': i['link'],
                    'views': i.get('viewCount', {}).get('short'),
                    'published': i.get('publishedTime'),
                    'description': ''
                }

                # Process description snippet if available
                desc = ''
                if 'descriptionSnippet' in i:
                    for j in i['descriptionSnippet']:
                        desc += j['text']
                    result_dict['description'] = desc

                result_list.append(result_dict)

            return render(request, 'dashboard/youtube.html', {'form': form, 'results': result_list})

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



