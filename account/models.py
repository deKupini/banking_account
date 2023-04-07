from django.db import models


class Account(models.Model):
    account_number = models.PositiveIntegerField(unique=True)
    account_name = models.CharField(max_length=64)
    balance = models.IntegerField(default=0)
    creation_date = models.DateField(auto_now=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class AccountHistory(models.Model):
    TYPE = (
        ('C', 'charge'),
        ('I', 'income'),
    )

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    description = models.CharField(blank=True, max_length=128, null=True)
    transaction_date = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=1, choices=TYPE)
