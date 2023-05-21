from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

app_name = 'main'


urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('daily/emotion/choose/', views.DailyEmotionMoodChooseView.as_view(),
         name='daily_emotion_mood_choose'),
    path('daily/emotion/resonate/<mood>', views.DailyEmotionResonateChooseView.as_view(),
         name='daily_emotion_resonate_choose'),
    path('daily/emotion/reason/', views.DailyEmotionReasonChooseView.as_view(),
         name='daily_emotion_reason'),
    path('daily/emotion/done/', views.DailyEmotionDone.as_view(),
         name='daily_emotion_done'),
    path('daily/emotion/save/', views.DailyEmotionSaveView.as_view(),
         name='daily_emotion_save'),
    path('my/to/do', views.MyToDoListView.as_view(),
         name='my_todo'),
    path('my/todo/add', views.MyToDoAddView.as_view(),
         name='my_todo_add'),
    path('my/todo/done', views.MyToDoDoneView.as_view(),
         name='my_todo_done'),
    path('diary/save', views.DiarySaveView.as_view(),
         name='diary_save'),
    path('my/diary', views.MyDiaryView.as_view(),
         name='my_diary'),
    path('register/', views.RegistrationView.as_view(),
         name='register'),
    path('profile/', views.ProfileView.as_view(),
         name='profile'),
    path('user/update/', views.UserUpdateView.as_view(),
         name='user_update'),
    path('password-change/', views.CustomPasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('start-test/<pk>', views.StartTestView.as_view(), name='start_test'),
    path('get-question/', views.GetQuestionView.as_view(), name='get_question'),
    path('submit-answer/', views.SubmitAnswerView.as_view(), name='submit_answer'),
    path('test-completed/', views.IsTestCompletedView.as_view(), name='test_completed'),
    path('delete/user/<pk>', views.DleteUserView.as_view(), name='delete_user'),
    
]