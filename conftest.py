from datetime import datetime

import pytest

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from account.models import Account, AccountHistory


@pytest.fixture
def account_history_factory(user_account):
    def factory(
            account: Account = user_account,
            amount: float = 100.20,
            description: str = None,
            transfer_type: str = 'I'
    ) -> AccountHistory:
        if transfer_type == 'I':
            account.balance += amount
        else:
            account.balance -= amount
        account.save()

        account_history_record = AccountHistory.objects.create(
            account=account,
            amount=amount,
            balance_after_transfer=account.balance,
            description=description,
            type=transfer_type
        )

        return account_history_record

    return factory


@pytest.fixture
def account_history_record_income(user_account) -> AccountHistory:
    account_history_record = AccountHistory.objects.create(
        account=user_account,
        amount=100.20,
        balance_after_transfer=user_account.balance + 100.20,
        description='Transfer description',
        type='I'
    )
    user_account.balance += account_history_record.amount
    user_account.save()
    return account_history_record


@pytest.fixture
def account_history_record_expense(user_account) -> AccountHistory:
    account_history_record = AccountHistory.objects.create(
        account=user_account,
        amount=100.20,
        balance_after_transfer=user_account.balance - 100.20,
        description='Transfer description',
        type='O'
    )
    user_account.balance -= account_history_record.amount
    user_account.save()
    return account_history_record


@pytest.fixture
def anonymous_client() -> APIClient:
    client = APIClient()
    return client


@pytest.fixture
def user(db) -> User:
    user = User.objects.create_user('user')
    return user


@pytest.fixture
def user_2(db) -> User:
    user = User.objects.create_user('user_2')
    return user


@pytest.fixture
def user_account(db, user) -> Account:
    user_account = Account.objects.create(account_name='Account name', owner=user)
    return user_account


@pytest.fixture
def user_account_2(db, user) -> Account:
    user_account = Account.objects.create(account_name='Account name 2', owner=user)
    return user_account


@pytest.fixture
def user_client(db, user) -> APIClient:
    user_client = APIClient()
    user_client.force_authenticate(user)
    return user_client


@pytest.fixture
def user_2_client(db, user_2) -> APIClient:
    user_client = APIClient()
    user_client.force_authenticate(user_2)
    return user_client
