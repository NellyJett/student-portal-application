from django import forms
from student_portal_app.models import(
    Notes,
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
        model = 'Homework'
        fields = '__all__'

        widget = {'due': DateInput()}