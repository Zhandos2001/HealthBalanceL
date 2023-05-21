from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='media', default='assets/img/smile1.png')

class EmotionsResonate(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class DailyEmotion(models.Model):
    date = models.DateField(auto_now_add=True)
    mood = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    emotions_resonate = models.ManyToManyField('EmotionsResonate')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.mood

class ToDo(models.Model):
    title = models.CharField(max_length=200)
    def __str__(self):
        return self.title

class MyToDo(models.Model):
    todo = models.ManyToManyField('ToDo')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

from datetime import date
class MyToDoDone(models.Model):
    date = models.DateField(default=date.today)
    my_todo = models.ManyToManyField('ToDo')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Diary(models.Model):
    STATUS_CHOICES = (
        (1, 'Positive'),
        (2, 'Negative'),
        (3, 'Sleep'),
        (4, 'Date')
    )
    title = models.CharField(max_length=200)
    text = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

class Question(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='diaries', null=True, blank=True)



