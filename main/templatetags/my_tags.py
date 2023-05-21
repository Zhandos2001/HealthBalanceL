import json
from django import template
from main.models import MyToDo, MyToDoDone

register = template.Library()

@register.filter
def json_encode(value):
    return json.dumps(value)


@register.simple_tag()
def is_todo_checked(todo_id, user):
    try:
        my_todo = MyToDo.objects.get(user=user)
        if my_todo.todo.filter(id=todo_id).exists():
            return 'checked'
    except MyToDo.DoesNotExist:
        pass
    return ''
from datetime import datetime
@register.simple_tag()
def is_my_todo_done_checked(todo_id, user):
    today = datetime.today().date()
    try:
        my_todo = MyToDoDone.objects.get(user=user, date=today)
        if my_todo.my_todo.filter(id=todo_id).exists():
            return 'checked'
    except MyToDoDone.DoesNotExist:
        pass
    return ''
