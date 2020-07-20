from django.urls import path
from splitter import views

app_name = 'splitter'

urlpatterns = [
    path('signup/',views.signup,name="signup"),
    path('login/',views.user_login,name="login"),
    path('logout/',views.user_logout,name="logout"),
    path('create_room/',views.add_room,name="add_room"),
    path('rooms_list/',views.room_list,name="room_list"),
    path('rooms_detail/<int:pk>',views.room_details,name="room_detail"),
    path('rooms_detail/<int:pk>/create_transaction',views.create_transaction,name="create_transaction"),
    path('my_debts/',views.my_debts,name="my_debts"),
    path('settle_debt/<int:pk>',views.delete_debt,name="delete_debt"),
    path('final_settlements/',views.final_settlements,name="final_settlements"),
    path('members_list/<int:pk>/',views.list_members,name="list_members"),
    path('add_members/<int:pk>/add/<int:id>/',views.add_member,name="add_member"),
    path('personal_budget/',views.personal_budget,name="personal_budget"),
    path('add_personal_budget/',views.add_personal_budget,name="add_personal_budget"),
    path('delete_personal_income/<int:pk>/',views.delete_personal_income,name="delete_personal_income"),
    path('delete_personal_expense/<int:pk>/',views.delete_personal_expense,name="delete_personal_expense"),
    path('<int:pk>/update_transaction/<int:id>/',views.update_transaction,name="update_transaction"),
    path('transaction_details/<int:pk>/',views.transaction_details,name="transaction_details"),
    path('join_us/',views.joinus,name="joinus"),
]
