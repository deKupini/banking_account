from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED

from account.models import Account


ACCOUNT_URL = reverse('account-list')


def test_create_account_without_other_accounts(db, user, user_client):
    data = {
        'account_name': 'Some name'
    }
    response = user_client.post(ACCOUNT_URL, data)
    assert response.status_code == HTTP_201_CREATED
    assert Account.objects.count() == 1
    banking_account = Account.objects.all().first()
    assert banking_account.account_name == data['account_name']
    assert len(banking_account.account_number) == 26
    assert not banking_account.balance
    assert banking_account.owner == user


def test_create_account_with_other_account(db, user_account, user_client):
    data = {
        'account_name': 'Some name'
    }
    response = user_client.post(ACCOUNT_URL, data)
    assert response.status_code == HTTP_201_CREATED
    assert Account.objects.count() == 2
    new_account = Account.objects.get(account_name=data['account_name'])
    assert new_account.account_number != user_account.account_number
