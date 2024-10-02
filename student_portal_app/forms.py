from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from student_portal_app.models import(
    Notes,
    Homework,
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