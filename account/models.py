import random
import string

from django.db import models


class Account(models.Model):
    account_number = models.CharField(max_length=26, unique=True)
    account_name = models.CharField(max_length=64)
    balance = models.FloatField(default=0)
    creation_date = models.DateField(auto_now=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    @staticmethod
    def _generate_account_number():
        account_numbers = Account.objects.all().values_list('account_number', flat=True)
        while True:
            account_number = ''.join(random.choices(string.digits, k=26))
            if account_number not in account_numbers:
                return account_number

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self._generate_account_number()
        super().save(*args, **kwargs)


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
