import pytest

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from account.models import Account


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
def user_client(db, user) -> APIClient:
    user_client = APIClient()
    user_client.force_authenticate(user)
    return user_client


@pytest.fixture
def user_2_client(db, user_2) -> APIClient:
    user_client = APIClient()
    user_client.force_authenticate(user_2)
    return user_client
