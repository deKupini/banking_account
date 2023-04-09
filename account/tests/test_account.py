from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED

from account.models import Account, AccountHistory

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


def test_income_with_zero_balance(db, user_2_client, user_account):
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': 20.54, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')
    assert response.status_code == 204
    new_balance = user_account.balance + data['amount']
    user_account = Account.objects.get(id=user_account.id)
    assert new_balance == user_account.balance
    assert AccountHistory.objects.count() == 1
    account_history_record = AccountHistory.objects.all().first()
    assert account_history_record.account == user_account
    assert account_history_record.amount == data['amount']
    assert account_history_record.balance_after_transfer == new_balance
    assert account_history_record.description == data['description']
    assert account_history_record.type == 'I'


def test_income_with_positive_balance(db, user_2_client, user_account):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': 20.54, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')
    assert response.status_code == 204
    new_balance = user_account.balance + data['amount']
    user_account = Account.objects.get(id=user_account.id)
    assert new_balance == user_account.balance
    assert AccountHistory.objects.count() == 2
    account_history_record = AccountHistory.objects.get(amount=data['amount'])
    assert account_history_record.balance_after_transfer == new_balance
    assert account_history_record.type == 'I'


def test_income_with_negative_balance(db, user_2_client, user_account):
    user_account.balance = -100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=-100.00,
        description='First outgoing transfer',
        type='O'
    )
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': 20.54, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')
    assert response.status_code == 204
    new_balance = user_account.balance + data['amount']
    user_account = Account.objects.get(id=user_account.id)
    assert new_balance == user_account.balance
    assert AccountHistory.objects.count() == 2
    account_history_record = AccountHistory.objects.get(amount=data['amount'])
    assert account_history_record.balance_after_transfer == new_balance
    assert account_history_record.type == 'I'


def test_income_without_authorization(anonymous_client, db, user_account):
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': 20.54, 'description': 'Transfer description'}
    response = anonymous_client.patch(url, data, format='json')
    assert response.status_code == 403
    user_account_after_transaction_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transaction_try == user_account
    assert not AccountHistory.objects.count()


def test_income_for_not_existing_account(db, user_client):
    url = reverse('account-transfer-to-account')
    data = {'account_number': 123, 'amount': 20.54, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')
    assert response.status_code == 404
    assert not AccountHistory.objects.count()


def test_income_for_negative_amount(db, user_2_client, user_account):
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': -20.54, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')
    assert response.status_code == 404
    assert not AccountHistory.objects.count()
