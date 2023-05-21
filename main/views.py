from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import DailyEmotion, EmotionsResonate, MyToDo, ToDo, MyToDoDone, Diary, Profile
from .forms import DiaryForm, TestForm, RegistrationForm, ProfileForm
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.views.generic import UpdateView

class RegistrationView(CreateView):
    template_name = 'registration/registration.html'

    def get(self, request, *args, **kwargs):
        registration_form = RegistrationForm()
        return self.render_to_response(
            {'registration_form': registration_form})

    def post(self, request, *args, **kwargs):
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            new_user=registration_form.save(commit=False)
            new_user.set_password(
                registration_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            authenticate_user = authenticate(
                username=registration_form.cleaned_data['username'],
                password=registration_form.cleaned_data['password']
            )
            login(request, authenticate_user)
            return redirect('main:index')
        return self.render_to_response(
            {'registration_form': registration_form})

class IndexView(TemplateResponseMixin, View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        daily_emotions = DailyEmotion.objects.filter(user=request.user).order_by('-id')[:5]
        return self.render_to_response({
            'daily_emotions': daily_emotions
            })

class DailyEmotionMoodChooseView(TemplateResponseMixin, View):
    template_name = 'daily_emotion_choose.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            })

class DailyEmotionResonateChooseView(TemplateResponseMixin, View):
    template_name = 'daily_emotion_resonate_choose.html'

    def get(self, request, *args, **kwargs):
        mood = self.kwargs.get('mood')
        emotions_resonate = EmotionsResonate.objects.all()
        return self.render_to_response({
            'mood': mood, 'emotions_resonate': emotions_resonate
        })

class DailyEmotionReasonChooseView(TemplateResponseMixin, View):
    template_name = 'daily_emotion_reason.html'

    def get(self, request, *args, **kwargs):
        mood = request.GET.get('mood')
        emotions_resonate = EmotionsResonate.objects.all()
        selected_emotions = request.GET.getlist('emotions[]')
        print(selected_emotions)
        return self.render_to_response({
            'mood': mood, 'emotions_resonate': emotions_resonate,
            'selected_emotions': selected_emotions
        })

import json

class DailyEmotionSaveView(View):
    def post(self, request, *args, **kwargs):
        mood = request.POST.get('mood')
        reason = request.POST.get('reason')
        emotions_resonate = request.POST.get('emotions_resonate')
        user = request.user
        daily_emotion = DailyEmotion.objects.create(mood=mood, reason=reason, user=user)
        try:
            emotions_resonate_list = json.loads(emotions_resonate)
            emotions_resonate_ids = [int(id_str) for id_str in emotions_resonate_list]
            daily_emotion.emotions_resonate.add(*emotions_resonate_ids)
        except json.JSONDecodeError:
            # Handle the error here (e.g. return an error message to the user)
            pass
        return redirect('main:daily_emotion_done')


class DailyEmotionDone(TemplateResponseMixin, View):
    template_name = 'done.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

class MyToDoListView(TemplateResponseMixin, View):
    template_name = 'my_todo.html'

    def get(self, request, *args, **kwargs):
        try:
            my_todo = MyToDo.objects.get(user=request.user)
            return self.render_to_response({'my_todo': my_todo})
        except MyToDo.DoesNotExist:
            return self.render_to_response({})

class MyToDoAddView(TemplateResponseMixin, View):
    template_name = 'my_todo_add.html'

    def get(self, request, *args, **kwargs):
        try:
            todo_list = ToDo.objects.all()
            return self.render_to_response({'todo_list': todo_list})
        except ToDo.DoesNotExist:
            return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        try:
            my_todo = MyToDo.objects.get(user=request.user)
        except MyToDo.DoesNotExist:
            my_todo = MyToDo.objects.create(user=request.user)

        new_todo_list = request.POST.getlist('todo_list[]')
        new_todo_ids = [int(id_str) for id_str in new_todo_list]
        old_todo_ids = my_todo.todo.values_list('id', flat=True)

        # Remove to-do items that are no longer selected
        for todo_id in old_todo_ids:
            if todo_id not in new_todo_ids:
                my_todo.todo.remove(todo_id)

        # Add new to-do items that are selected
        for todo_id in new_todo_ids:
            if todo_id not in old_todo_ids:
                my_todo.todo.add(todo_id)

        return redirect('main:my_todo')
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Count

class MyToDoDoneView(TemplateResponseMixin, View):
    template_name = 'calendar.html'

    def get(self, request, *args, **kwargs):
        try:
            todo_done_list = MyToDoDone.objects.filter(user=request.user).order_by('-id')[:5]

            seven_days_ago = datetime.now() - timedelta(days=7)

            # Define the moods dictionary with point values
            moods = {"awful": 1, "sad": 2, "ok": 3, "pretty good": 4, "happy": 5}

            # Create a dictionary to store mood counts and total points for each day of the week
            mood_counts = defaultdict(lambda: defaultdict(int))
            mood_points = defaultdict(lambda: defaultdict(int))

            # Get the mood counts for the last 7 days
            daily_emotions = DailyEmotion.objects.filter(date__gte=seven_days_ago, user=request.user)
            for emotion in daily_emotions:
                day_of_week = emotion.date.weekday()
                mood = emotion.mood.lower()
                mood_counts[day_of_week][mood] += 1
                mood_points[day_of_week][mood] += moods[mood]

            # Calculate the average mood for each day of the week
            days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            average_moods = []
            max_mood = max(moods.values())  # Get the maximum mood value
            for day in range(7):
                total_count = sum(mood_counts[day][mood] for mood in moods)
                total_points = sum(mood_points[day][mood] for mood in moods)
                if total_count > 0:
                    average_mood = total_points / total_count
                else:
                    average_mood = 0
                average_moods.append(round(average_mood, 1))

            # Adjust the average moods to fit the range of 1 to max_mood
            adjusted_moods = [max(1, min(mood, max_mood)) for mood in average_moods]

            # Calculate the scale values for the histogram
            scale_values = list(range(1, max_mood + 1))[::-1]  # Reverse the range and convert to a list

            happy_count = DailyEmotion.objects.filter(mood='happy', date__gte=seven_days_ago, user=request.user).count()
            ok_count = DailyEmotion.objects.filter(mood='Ok', date__gte=seven_days_ago, user=request.user).count()
            sad_count = DailyEmotion.objects.filter(mood='Sad', date__gte=seven_days_ago, user=request.user).count()
            pretty_good_count = DailyEmotion.objects.filter(mood='Pretty Good', date__gte=seven_days_ago,
                                                            user=request.user).count()
            awful_count = DailyEmotion.objects.filter(mood='Awful', date__gte=seven_days_ago, user=request.user).count()

            return self.render_to_response({
                'todo_done_list': todo_done_list,
                'average_moods': adjusted_moods,
                'days_of_week': days_of_week,
                'scale_values': scale_values,
                'happy_count': happy_count,
                'ok_count': ok_count,
                'sad_count': sad_count,
                'pretty_good_count': pretty_good_count,
                'awful_count': awful_count
            })
        except MyToDoDone.DoesNotExist:
            return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        today = datetime.today().date()
        try:
            todo = MyToDoDone.objects.get(user=request.user, date=today)
        except ObjectDoesNotExist:
            todo = MyToDoDone.objects.create(user=request.user)

        new_todo_list = request.POST.getlist('todo_list[]')
        todo_done_list = json.loads(json.dumps(new_todo_list))
        new_todo_done_list_ids = [int(id_str) for id_str in todo_done_list]
        old_todo_done_list_ids = todo.my_todo.values_list('id', flat=True)


        # Remove to-do items that are no longer selected
        for todo_id in old_todo_done_list_ids:
            if todo_id not in new_todo_done_list_ids:
                todo.my_todo.remove(todo_id)

        # Add new to-do items that are selected
        for todo_id in new_todo_done_list_ids:
            if todo_id not in old_todo_done_list_ids:
                todo.my_todo.add(todo_id)

        return redirect('main:my_todo_done')

class DiarySaveView(TemplateResponseMixin, View):
    template_name = 'diary_create.html'

    def get(self, request, *args, **kwargs):
        form = DiaryForm()
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = DiaryForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.user = request.user
            form_obj.save()
            return redirect('main:my_diary')
        return self.render_to_response({'form': form})

class MyDiaryView(TemplateResponseMixin, View):
    template_name = 'my_diary.html'

    def get(self, request, *args, **kwargs):
        my_diaries = Diary.objects.filter(user=request.user).order_by('-id')[:5]#[:5]
        return self.render_to_response({'my_diaries': my_diaries})

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse



class ProfileView(TemplateResponseMixin, View):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        return self.render_to_response({'profile': profile})

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'user_update.html'
    success_url = reverse_lazy('main:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['profile_form'] = ProfileForm()
        return context

    def form_valid(self, form):
        profile_form = ProfileForm(self.request.POST, self.request.FILES, instance=self.request.user.profile)
        if profile_form.is_valid():
            profile_form_obj = profile_form.save(commit=False)
            profile_form_obj.user = self.request.user
            profile_form_obj.save()
        return super().form_valid(form)


from django.contrib.auth.views import PasswordChangeView

class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('main:password_change_done')

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Question, Answer

class StartTestView(View):
    def get(self, request, *args, **kwargs):
        # create a session and set the initial question index to 1
        request.session['diary_pk'] = self.kwargs.get('pk')
        diary = Diary.objects.get(pk=self.kwargs.get('pk'))
        context = {'diary': diary}
        request.session['question_index'] = 1
        return render(request, 'test.html', context)

    def post(self, request, *args, **kwargs):
        # create a session and set the initial question index to 1
        request.session['question_index'] = 1
        return redirect('main:get_question')


class GetQuestionView(View):
    def get(self, request, *args, **kwargs):
        # get the current question index from the session
        question_index = request.session.get('question_index', 1)
        diary_pk_ = request.session.get('diary_pk', 1)
        print('Current question index:', question_index)

        try:
            # retrieve the current question from the database
            question = Question.objects.get(pk=question_index)
            print('Current question:', question)

            # get the latest diary entry for the user
            diary = Diary.objects.get(pk=diary_pk_)

            # check if the user has already answered this question for the latest diary entry
            answer = Answer.objects.filter(question=question, user=request.user, diary=diary).first()
            print('Current answer:', answer)

            return render(request, 'question.html', {'question': question, 'answer': answer})

        except ObjectDoesNotExist:
            # handle the case where the question does not exist
            return render(request, 'test_completed.html', {'test_completed': True})


class SubmitAnswerView(View):
    def post(self, request, *args, **kwargs):
        diary_pk_ = request.session.get('diary_pk', 1)
        # get the current question index from the session
        question_index = request.session.get('question_index', 1)

        # retrieve the current question from the database
        question = get_object_or_404(Question, pk=question_index)

        # get the latest diary entry for the user
        diary = Diary.objects.get(pk=diary_pk_)

        # create or update the user's answer for this question and the latest diary entry
        answer_text = request.POST.get('answer', '')
        answer, _ = Answer.objects.update_or_create(question=question, user=request.user, diary=diary,
                                                    defaults={'text': answer_text})

        # increment the question index in the session
        request.session['question_index'] = question_index + 1

        return redirect('main:get_question')


class IsTestCompletedView(View):
    def get(self, request, *args, **kwargs):
        # get the latest diary entry for the user
        diary_pk_ = request.session.get('diary_pk', 1)
        diary = Diary.objects.filter(pk=diary_pk_)

        # count the total number of questions in the database
        total_questions = Question.objects.count()

        # get the number of questions answered by the user for the latest diary entry
        answered_questions = Answer.objects.filter(user=request.user, diary=diary).count()

        # check if the user has completed the test
        test_completed = answered_questions >= total_questions

        return render(request, 'test_completed.html', {'test_completed': test_completed})
    
class DleteUserView(View):

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = User.objects.get(pk=pk)
        user.delete()
        return redirect('login')