from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class room(models.Model):
    creater = models.ForeignKey(User,on_delete=models.CASCADE,related_name="creater")
    name = models.CharField(max_length=250)
    members = models.ManyToManyField(User,through="room_members")

    def __str__(self):
        return self.name

class room_members(models.Model):
    room = models.ForeignKey(room, on_delete = models.CASCADE, related_name = "room_name")
    member = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "room_member")

    def __str__(self):
        return self.member.username + ' in group ' + self.room.name

    class Meta:
        unique_together = ('room','member')

class transaction(models.Model):
    room = models.ForeignKey(room, on_delete = models.CASCADE, related_name = 'room_transaction')
    amount = models.IntegerField()
    reason = models.CharField(max_length = 250)
    created_at = models.DateTimeField(auto_now=True)
    payer = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'transaction_payer')
    splitters = models.ManyToManyField(User, related_name = "transaction_members")

    def __str__(self):
        return self.reason + ' in group ' + self.room.name


class debt(models.Model):
    room = models.ForeignKey(room,on_delete = models.CASCADE, related_name = 'room_debts')
    transaction = models.ForeignKey(transaction, on_delete = models.CASCADE, related_name = 'transactions_debt')
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'transaction_sender')
    receiver = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'transaction_receiver')
    amount = models.IntegerField()

    def __str__(self):
        return self.sender.username + ' pay to ' + self.receiver.username + ' in room ' + self.room.name

class final_transactions(models.Model):
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'final_transaction_sender')
    receiver = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'final_transaction_receiver')
    final_amount = models.IntegerField()

    def __str__(self):
        return self.sender.username + ' gives amount ' + str(self.final_amount) + ' to ' +self.receiver.username

class Personal_income(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    description = models.CharField(max_length = 250)
    amount = models.IntegerField()

    def __str__(self):
        return self.description

class Personal_expense(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    description = models.CharField(max_length = 250)
    amount = models.IntegerField()

    def __str__(self):
        return self.description
