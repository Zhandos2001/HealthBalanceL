from django import forms
from django.contrib.auth.models import User
from .models import Diary, Question, Profile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = Question.objects.all()
        for question in questions:
            choices = [(a.pk, a.text) for a in question.answers.all()]
            self.fields['question_{}'.format(question.pk)] = forms.ChoiceField(label=question.text, choices=choices, widget=forms.RadioSelect, required=True)

class DiaryForm(forms.ModelForm):

    class Meta:
        model = Diary
        fields = ('title', 'text', 'status')
        exclude = ('user',)

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('photo', )
        exclude = ('user', )