from django import forms
from django.forms import RadioSelect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from student_portal_app.models import(
    Notes,
    Homework,
    Todo
)

class DashboardForm(forms.Form):
    text = forms.CharField(max_length = 100, label = 'Enter your search ')

class DateInput(forms.DateInput):
    input_type = 'date'

class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'description']

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = '__all__'

        widget = {'due': DateInput()}

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help_text for each field
        for field in self.fields.values():
            field.help_text = None

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'is_finished']

class ConversationForm(forms.Form):
    CHOICES = [('length','Length'), ('mass', 'Mass')]
    measurement = forms.ChoiceField(choices=CHOICES, widget=RadioSelect)

class ConversationLengthForm(forms.Form):
    CHOICES = [('yard', 'Yard'), ('foot', 'Foot')]
    input = forms.CharField(required=False, label=False, widget=forms.TextInput(attrs={'type':'number', 'placeholder':'Enter the number'}))
    measure1 = forms.CharField(label='', widget=forms.Select(choices=CHOICES))
    measure2 = forms.CharField(label='', widget=forms.Select(choices=CHOICES))

class ConversationMassForm(forms.Form):
    CHOICES = [('pound', 'Pound'), ('kilogram', 'Kilogram')]
    input = forms.CharField(required=False, label=False, widget=forms.TextInput(attrs={'type':'number', 'placeholder':'Enter the number'}))
    measure1 = forms.CharField(label='', widget=forms.Select(choices=CHOICES))
    measure2 = forms.CharField(label='', widget=forms.Select(choices=CHOICES))