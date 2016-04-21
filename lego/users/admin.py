from django.contrib import admin
from django.contrib.auth.models import Group
from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask, TaskState, WorkerState
from mptt.admin import MPTTModelAdmin

from .models import AbakusGroup, Membership, User

admin.site.unregister(Group)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(WorkerState)
admin.site.unregister(TaskState)

admin.site.register(User)
admin.site.register(AbakusGroup, MPTTModelAdmin)
admin.site.register(Membership)
