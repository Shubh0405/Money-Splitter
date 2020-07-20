from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,room,room_members,transaction,debt,final_transactions,Personal_income,Personal_expense
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(room)
admin.site.register(room_members)
admin.site.register(transaction)
admin.site.register(debt)
admin.site.register(final_transactions)
admin.site.register(Personal_income)
admin.site.register(Personal_expense)
