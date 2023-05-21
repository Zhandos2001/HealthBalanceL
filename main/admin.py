from django.contrib import admin
from .models import DailyEmotion, EmotionsResonate, ToDo, MyToDo, MyToDoDone, Diary, Question, Answer, Profile

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'user', 'diary')
    list_filter = ('question', 'user', 'diary')
    search_fields = ('text',)
    ordering = ('id',)

admin.site.register(Answer, AnswerAdmin)

class DiaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'date')
    list_filter = ('user', 'status', 'date')
    search_fields = ('title', 'text',)
    ordering = ('-date',)

admin.site.register(Diary, DiaryAdmin)

class DailyEmotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user', 'mood')
    list_filter = ('user', 'date')
    search_fields = ('mood', 'reason',)
    ordering = ('-date',)
    
admin.site.register(DailyEmotion, DailyEmotionAdmin)


admin.site.register(EmotionsResonate)
admin.site.register(ToDo)
admin.site.register(MyToDo)
admin.site.register(MyToDoDone)
admin.site.register(Question)
admin.site.register(Profile)
