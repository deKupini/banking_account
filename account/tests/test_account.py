from unittest.mock import patch
import datetime

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_404_NOT_FOUND, HTTP_200_OK

from account.models import Account, AccountHistory

ACCOUNT_URL = reverse('account-list')


def test_block_get_account_list(db, user_account, user_client):
    response = user_client.get(ACCOUNT_URL)

    assert response.status_code == HTTP_404_NOT_FOUND


def test_block_get_account(db, user_account, user_client):
    response = user_client.get(ACCOUNT_URL + f'/{user_account.id}/')

    assert response.status_code == HTTP_404_NOT_FOUND


def test_block_patch_account(db, user_account, user_client):
    data = {'account_name': 'New name'}
    response = user_client.patch(ACCOUNT_URL + f'/{user_account.id}/', data)

    assert response.status_code == HTTP_404_NOT_FOUND
    user_account = Account.objects.get(id=user_account.id)
    assert user_account.account_name != data['account_name']


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

    assert response.status_code == HTTP_204_NO_CONTENT
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

    assert response.status_code == HTTP_204_NO_CONTENT
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

    assert response.status_code == HTTP_204_NO_CONTENT
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

    assert response.status_code == HTTP_403_FORBIDDEN
    user_account_after_transaction_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transaction_try == user_account
    assert not AccountHistory.objects.count()


def test_income_for_not_existing_account(db, user_client):
    url = reverse('account-transfer-to-account')
    data = {'account_number': 123, 'amount': 20.54, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_404_NOT_FOUND
    assert not AccountHistory.objects.count()


def test_income_for_negative_amount(db, user_2_client, user_account):
    url = reverse('account-transfer-to-account')
    data = {'account_number': user_account.account_number, 'amount': -20.54, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')

    assert response.status_code == HTTP_400_BAD_REQUEST
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert not AccountHistory.objects.count()


def test_outgoing_transfer_with_zero_balance(db, user_account, user_client):
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 19.45, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_400_BAD_REQUEST
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert not AccountHistory.objects.count()


def test_outgoing_transfer_with_negative_balance(db, user_account, user_client):
    user_account.balance = -100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=-100.00,
        description='First outgoing transfer',
        type='O'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 19.45, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_400_BAD_REQUEST
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert AccountHistory.objects.count() == 1


def test_outgoing_transfer_with_amount_greater_than_balance(db, user_account, user_client):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 191.45, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_400_BAD_REQUEST
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert AccountHistory.objects.count() == 1


def test_outgoing_transfer_with_amount_equal_to_balance(db, user_account, user_client):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 100.00, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_204_NO_CONTENT
    user_account = Account.objects.get(id=user_account.id)
    assert not user_account.balance
    assert AccountHistory.objects.count() == 2
    account_history_record = AccountHistory.objects.get(type='O')
    assert account_history_record.account == user_account
    assert account_history_record.amount == data['amount']
    assert not account_history_record.balance_after_transfer
    assert account_history_record.description == data['description']


def test_outgoing_transfer_with_amount_lesser_than_balance(db, user_account, user_client):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 80.00, 'description': 'Transfer description'}
    new_balance = user_account.balance - data['amount']
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_204_NO_CONTENT
    user_account = Account.objects.get(id=user_account.id)
    assert user_account.balance == new_balance
    assert AccountHistory.objects.count() == 2
    account_history_record = AccountHistory.objects.get(type='O')
    assert account_history_record.account == user_account
    assert account_history_record.amount == data['amount']
    assert account_history_record.balance_after_transfer == new_balance
    assert account_history_record.description == data['description']


def test_outgoing_transfer_with_negative_amount(db, user_account, user_client):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': -50.00, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_400_BAD_REQUEST
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert AccountHistory.objects.count() == 1


def test_outgoing_transfer_by_not_owner(db, user_2_client, user_account):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 80.00, 'description': 'Transfer description'}
    response = user_2_client.patch(url, data, format='json')

    assert response.status_code == HTTP_404_NOT_FOUND
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert AccountHistory.objects.count() == 1


def test_outgoing_transfer_without_authorization(anonymous_client, db, user_account):
    user_account.balance = 100.00
    user_account.save()
    AccountHistory.objects.create(
        account=user_account,
        amount=100.00,
        balance_after_transfer=100.00,
        description='First income',
        type='I'
    )
    url = reverse('account-transfer-from-account', args=[user_account.id])
    data = {'amount': 80.00, 'description': 'Transfer description'}
    response = anonymous_client.patch(url, data, format='json')

    assert response.status_code == HTTP_403_FORBIDDEN
    user_account_after_transfer_try = Account.objects.get(id=user_account.id)
    assert user_account_after_transfer_try == user_account
    assert AccountHistory.objects.count() == 1


def test_outgoing_transfer_from_not_existing_account(db, user_client):
    url = reverse('account-transfer-from-account', args=[1])
    data = {'amount': 80.00, 'description': 'Transfer description'}
    response = user_client.patch(url, data, format='json')

    assert response.status_code == HTTP_404_NOT_FOUND
    assert not AccountHistory.objects.count()


def test_check_balance_without_authorization(anonymous_client, db, user_account):
    url = reverse('account-check-balance', args=[user_account.id])
    response = anonymous_client.get(url)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_check_balance_as_not_owner(db, user_2_client, user_account):
    url = reverse('account-check-balance', args=[user_account.id])
    response = user_2_client.get(url)

    assert response.status_code == HTTP_404_NOT_FOUND


def test_check_zero_balance(db, user_account, user_client):
    url = reverse('account-check-balance', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response == {
        'balance': user_account.balance
    }


def test_check_positive_balance(db, user_account, user_client):
    user_account.balance = 100.00
    user_account.save()
    url = reverse('account-check-balance', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response == {
        'balance': user_account.balance
    }


def test_check_negative_balance(db, user_account, user_client):
    user_account.balance = -100.00
    user_account.save()
    url = reverse('account-check-balance', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response == {
        'balance': user_account.balance
    }


def test_check_empty_account_history(db, user_account, user_client):
    url = reverse('account-check-history', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response['results'] == []


def test_check_single_income_record_account_history(account_history_record_income, db, user_account, user_client):
    url = reverse('account-check-history', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response['results'] == [
        {
            'amount': account_history_record_income.amount,
            'balance_after_transfer': account_history_record_income.balance_after_transfer,
            'description': account_history_record_income.description,
            'id': account_history_record_income.id,
            'transaction_date': account_history_record_income.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'type': account_history_record_income.type,
        }
    ]


def test_check_single_expense_record_account_history(account_history_record_expense, db, user_account, user_client):
    url = reverse('account-check-history', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response['results'] == [
        {
            'amount': account_history_record_expense.amount,
            'balance_after_transfer': account_history_record_expense.balance_after_transfer,
            'description': account_history_record_expense.description,
            'id': account_history_record_expense.id,
            'transaction_date': account_history_record_expense.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'type': account_history_record_expense.type,
        }
    ]


def test_check_order_of_account_history(account_history_factory, db, user_account, user_client):
    transaction_date = datetime.datetime(2023, 4, 5, 15, 0, 20)
    with patch('django.utils.timezone.now', return_value=transaction_date):
        transfer_1 = account_history_factory(amount=20.50)

    transaction_date = datetime.datetime(2023, 4, 5, 14, 58, 1)
    with patch('django.utils.timezone.now', return_value=transaction_date):
        transfer_2 = account_history_factory(amount=30.45, transfer_type='O')

    transaction_date = datetime.datetime(2023, 4, 5, 16, 4, 50)
    with patch('django.utils.timezone.now', return_value=transaction_date):
        transfer_3 = account_history_factory(amount=100.00)

    transaction_date = datetime.datetime(2023, 4, 5, 15, 0, 14)
    with patch('django.utils.timezone.now', return_value=transaction_date):
        transfer_4 = account_history_factory(amount=12.01, transfer_type='O')

    order: list[AccountHistory] = [transfer_3, transfer_1, transfer_4, transfer_2]

    url = reverse('account-check-history', args=[user_account.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    response = response.json()
    assert response['count'] == 4
    for i in range(4):
        assert response['results'][i]['id'] == order[i].id


def test_check_excluding_account_history_from_another_accounts(
        account_history_record_income,
        db,
        user_account,
        user_account_2,
        user_client,
):
    url = reverse('account-check-history', args=[user_account_2.id])
    response = user_client.get(url)

    assert response.status_code == HTTP_200_OK
    assert not response.json()['count']


def test_check_account_history_as_not_owner(
        account_history_record_income,
        db,
        user_2_client,
        user_account,
):
    url = reverse('account-check-history', args=[user_account.id])
    response = user_2_client.get(url)

    assert response.status_code == HTTP_404_NOT_FOUND


def test_check_account_history_of_not_existing_account(db, user_client):
    url = reverse('account-check-history', args=[1])
    response = user_client.get(url)

    assert response.status_code == HTTP_404_NOT_FOUND


def test_check_account_history_without_authorization(anonymous_client, db, user_account):
    url = reverse('account-check-history', args=[1])
    response = anonymous_client.get(url)

    assert response.status_code == HTTP_403_FORBIDDEN
