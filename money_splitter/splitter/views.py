from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect,HttpResponse
from splitter.forms import UserForm,RoomForm
from splitter.models import User,room,room_members,transaction,debt,final_transactions,Personal_income,Personal_expense
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib import messages
# Create your views here.

def joinus(request):
    return render(request,'splitter/joinus.html',{})


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if(User.objects.filter(username=username).exists()):
            messages.error(request, "Username already exists, try to signin or choose different username")
            return redirect('splitter:joinus')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            messages.error(request,'Account successfully created! Try logging now')
            return HttpResponseRedirect(reverse('home'))


## Logout view
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

## Login view
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

            else:
                return HttpResponse("Account not active")
        else:
            messages.error(request, "Invalid Details")
            return redirect("splitter:joinus")


"""
Room creation view.
When user creates new room. A new object is created in room model with user as creater.
Also User is automatically added in the group so another object is to be created for room_members model.
"""
def add_room(request):
    if request.method == "POST":
        room_name = request.POST.get('room_name')
        new_room = room(creater=request.user,name=room_name)
        new_room.save()
        member = room_members(room=new_room,member=request.user)
        member.save()
        return HttpResponseRedirect(reverse('splitter:room_list'))
    return render(request,'splitter/room_list.html',{'form':form})


"""
Display all the rooms in which user is a member.
Filter objects from room_members model.
"""
def room_list(request):
    rooms = room_members.objects.filter(member=request.user)
    rooms_list = [x.room for x in rooms]
    length = False
    if(len(rooms_list) == 0):
        length = True
    print(len(rooms_list))
    return render(request,'splitter/room_list.html',{'rooms_list':rooms_list,'length':length})



"""
Display all the details of the room.
Room name, Creator, number of members, All the transaction made in the room.
"""
def room_details(request,pk):
    rooms = get_object_or_404(room,pk=pk)
    creator = False
    if request.user == rooms.creater:
        creator = True
    members = room_members.objects.filter(room=rooms)
    members_list = [x.member for x in members]
    members_count = len(members_list)
    transactions = transaction.objects.filter(room=rooms)
    return render(request,'splitter/room_detail.html',{'rooms':rooms,
                                                        'members_list':members_list,
                                                        'transactions':transactions,
                                                        'members_count':members_count,
                                                        'creator':creator})

## Add members in the room.
def add_member(request,pk,id):
    in_room = get_object_or_404(room,pk=pk)
    member = get_object_or_404(User,id=id)
    room_member = room_members(room=in_room,member=member)
    room_member.save()
    return HttpResponseRedirect(reverse('splitter:list_members',kwargs={'pk':pk}))

## List of all users
def list_members(request,pk):
    rooms = get_object_or_404(room,pk=pk)
    query = request.GET.get("q", None)
    members = room_members.objects.filter(room=rooms)
    members_list = [x.member for x in members]
    qs = User.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(username__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in members_list:
            pass
        else:
            qs_one.append(x)

    context = {
        "members_list": qs_one,
        "rooms":rooms
    }
    template = "splitter/members_list.html"
    return render(request, template, context)




"""
transaction details view.
amount,reason,splitters and all details of transaction.
"""
def transaction_details(request,pk):
    transactions = get_object_or_404(transaction,pk=pk)
    members = room_members.objects.filter(room=transactions.room)
    all_room_members = [x.member for x in members]
    transaction_splitters = transactions.splitters.all()
    transaction_splitters_username = [x.username for x in transaction_splitters]
    return render(request,'splitter/transaction_details.html',{'transaction':transactions,'transaction_splitters_username':transaction_splitters_username,'all_room_members':all_room_members,'transaction_splitters':transaction_splitters})

# Create transaction View
# Take all the data of transaction and create transaction object. Payer will be the current user.
# Take the list of splitters and make debt object for each of them.
# For all the splitters, filter the objects in final_transactions model with user and another person.
# If there is no object created then create one else update it.
# Show the create transaction form as a pop-up form in room detail page.
def create_transaction(request,pk):
    rooms = get_object_or_404(room,pk=pk)
    if request.method == "POST":
        try:
            reason = request.POST.get('reason')
            amount = request.POST.get('amount')
            transaction_members = request.POST.getlist('splitter')
            splitters = User.objects.filter(username__in = transaction_members)
            obj = transaction(room = rooms,amount=amount,reason=reason,payer=request.user)
            obj.save()
            obj.splitters.add(*splitters)
            for x in splitters:
                if x == request.user:
                    pass
                else:
                    debt_obj = debt(room = rooms,transaction=obj,sender=x,receiver=request.user,amount=int(amount)/len(splitters))
                    debt_obj.save()
                    if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=x)
                    if_user_receiver = final_transactions.objects.filter(sender=x,receiver=request.user)
                    if len(if_user_receiver) == 0 and len(if_user_sender) == 0:
                        final_obj = final_transactions(sender=x,receiver=request.user,final_amount=int(amount)/len(splitters))
                        final_obj.save()
                    else:
                        if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
                            final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                            final_objs.final_amount += int(amount)/len(splitters)
                            final_objs.save()
                        else:
                            final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                            final_objs.final_amount -= int(amount)/len(splitters)
                            final_objs.save()
            return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))
        except:
            messages.error(request, "Details do not match the specified data type. (Hint: amount should be integer)")
            return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))
    # return render(request,'splitter/create_transaction.html',{'members':members,'rooms':rooms})



"""
Updating transaction view.
Abstract the list  of all the members of room to add them in the form for updating from room_member model.
Get the previous transaction details which is going to be updated.
Make the new transaction from data given by user in updating transaction form.
Update all the final_transactions objects between previous transaction splitters and user to delete all the debts created by that transaction.
Again update final_transactions objects according to the new data i.e. between new splitters and user with new amount(depending on the data given).
create the debt objects for Updated transaction.
Delete previous transaction.
"""
def update_transaction(request,pk,id):
    rooms = get_object_or_404(room,pk=pk)
    members_list = room_members.objects.filter(room=rooms)
    members = [x.member for x in members_list]
    prev_transaction = get_object_or_404(transaction,id=id)
    prev_amount = prev_transaction.amount
    prev_reason = prev_transaction.reason
    prev_splitters = prev_transaction.splitters.all()
    prev_splitters_usernames = [x.username for x in prev_splitters]
    if request.method == "POST":
        new_reason = request.POST.get('reason')
        new_amount = request.POST.get('amount')
        new_transaction_members = request.POST.getlist('splitter')
        new_splitters = User.objects.filter(username__in = new_transaction_members)
        obj = transaction(room = rooms,amount=new_amount,reason=new_reason,payer=request.user)
        obj.save()
        obj.splitters.add(*new_splitters)
        for x in prev_splitters:
            if x == request.user:
                pass
            else:
                if_user_sender_prev = final_transactions.objects.filter(sender=request.user,receiver=x)
                if_user_receiver_prev = final_transactions.objects.filter(sender=x,receiver=request.user)
                if len(if_user_receiver_prev) == 1 and len(if_user_sender_prev) == 0:
                    final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                    final_objs.final_amount -= int(prev_amount)/len(prev_splitters)
                    final_objs.save()
                else:
                    final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                    final_objs.final_amount += int(prev_amount)/len(prev_splitters)
                    final_objs.save()
        for x in new_splitters:
            if x == request.user:
                pass
            else:
                debt_obj = debt(room = rooms,transaction=obj,sender=x,receiver=request.user,amount=int(new_amount)/len(new_splitters))
                debt_obj.save()
                if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=x)
                if_user_receiver = final_transactions.objects.filter(sender=x,receiver=request.user)
                if len(if_user_receiver) == 0 and len(if_user_sender) == 0:
                    final_obj = final_transactions(sender=x,receiver=request.user,final_amount=int(new_amount)/len(new_splitters))
                    final_obj.save()
                else:
                    if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
                        final_objs = final_transactions.objects.get(sender=x,receiver=request.user)
                        final_objs.final_amount += int(new_amount)/len(new_splitters)
                        final_objs.save()
                    else:
                        final_objs = final_transactions.objects.get(sender=request.user,receiver=x)
                        final_objs.final_amount -= int(new_amount)/len(new_splitters)
                        final_objs.save()
        prev_transaction.delete()
        return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))
    return HttpResponseRedirect(reverse('splitter:room_detail',kwargs={'pk':pk}))


## list of all debts for user.
def my_debts(request):
    income = debt.objects.filter(receiver=request.user)
    expense = debt.objects.filter(sender=request.user)
    query = request.GET.get("q", None)
    if query is not None:
        income = income.filter(
                Q(sender__username__icontains=query) |
                Q(transaction__reason__icontains=query) |
                Q(room__name__icontains=query)
                )
        expense = expense.filter(
                Q(receiver__username__icontains=query) |
                Q(transaction__reason__icontains=query) |
                Q(room__name__icontains=query)
                )
    return render(request,'splitter/my_debts.html',{'incomes':income,'expenses':expense})

## Final settlements of the users
def final_settlements(request):
    user_sender = final_transactions.objects.filter(sender = request.user)
    user_receiver = final_transactions.objects.filter(receiver = request.user)
    user_sender_positive = []
    user_sender_negative = []
    user_receiver_positive = []
    user_receiver_negative = []
    noincome = False
    noexpense = False
    for obj in user_sender:
        if(obj.final_amount > 0):
            user_sender_positive.append(obj)
        if(obj.final_amount < 0):
            obj.final_amount = abs(obj.final_amount)
            user_sender_negative.append(obj)
    for obj in user_receiver:
        if(obj.final_amount > 0):
            user_receiver_positive.append(obj)
        if(obj.final_amount < 0):
            obj.final_amount = abs(obj.final_amount)
            user_receiver_negative.append(obj)
    if len(user_receiver_positive) == 0 and len(user_sender_negative) == 0:
        noincome = True
    if len(user_sender_positive) == 0 and len(user_receiver_negative) == 0:
        noexpense = True
    return render(request,'splitter/final_settlements.html',{'user_sender_positive':user_sender_positive,
                                                                'user_sender_negative':user_sender_negative,
                                                                'user_receiver_positive':user_receiver_positive,
                                                                'user_receiver_negative':user_receiver_negative,
                                                                'noincome':noincome,
                                                                'noexpense':noexpense})


## delete debt view
def delete_debt(request,pk):
    if request.method == "POST":
        obj = get_object_or_404(debt,pk=pk)
        if_user_sender = final_transactions.objects.filter(sender=request.user,receiver=obj.sender)
        if_user_receiver = final_transactions.objects.filter(sender=obj.sender,receiver=request.user)
        if len(if_user_receiver) == 1 and len(if_user_sender) == 0:
            final_objs = final_transactions.objects.get(sender=obj.sender,receiver=request.user)
            final_objs.final_amount -= obj.amount
            final_objs.save()
        else:
            final_objs = final_transactions.objects.get(sender=request.user,receiver=obj.sender)
            final_objs.final_amount += obj.amount
            final_objs.save()
        obj.delete()
        return HttpResponseRedirect(reverse('splitter:my_debts'))
    return HttpResponseRedirect(reverse('splitter:my_debts'))

## Home Page view
def HomePage(request):
    return render(request,'splitter/index.html',{})

def personal_budget(request):
    qs_inc = Personal_income.objects.filter(user = request.user)
    qs_exp = Personal_expense.objects.filter(user = request.user)

    total_inc = sum([x.amount for x in qs_inc])
    total_exp = sum([x.amount for x in qs_exp])
    total_budget = total_inc - total_exp

    context = {
        'incomes': qs_inc,
        'expenses': qs_exp,
        'total_income': total_inc,
        'total_expenses': total_exp,
        'total_bud': total_budget,
    }

    template = 'splitter/personal_budget.html'
    return render(request, template, context)


def add_personal_budget(request):
    if request.method == 'POST':
        description = request.POST.get("description", None)
        amount = request.POST.get("amount", None)
        type = request.POST.get("type", None)
        user = request.user

        try:
            if (type == 'inc'):
                form = Personal_income(user=user,description=description, amount=int(amount))
            else:
                form = Personal_expense(user=user,description=description, amount=int(amount))
            form.save()
            return HttpResponseRedirect(reverse('splitter:personal_budget'))
        except:
            messages.error(request, "Details do not match the specified data type. (Hint: amount should be integer)")
            return HttpResponseRedirect(reverse('splitter:personal_budget'))

def delete_personal_income(request,pk):
    if request.method == "POST":
        obj = get_object_or_404(Personal_income,pk=pk)
        obj.delete()
        return HttpResponseRedirect(reverse('splitter:personal_budget'))
    return render(request,'splitter/personal_budget.html',{'obj':obj})

def delete_personal_expense(request,pk):
    if request.method == "POST":
        object = get_object_or_404(Personal_expense,pk=pk)
        object.delete()
        return HttpResponseRedirect(reverse('splitter:personal_budget'))
    return render(request,'splitter/personal_budget.html',{'object':object})
