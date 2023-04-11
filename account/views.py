from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet

from account.models import Account, AccountHistory
from account.serializers import AccountSerializer


class AccountViewSet(ModelViewSet):
    http_method_names = ('get', 'patch', 'post')
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=False, methods=['patch'])
    def transfer_to_account(self, request):
        account = get_object_or_404(Account, account_number=request.data['account_number'])
        if request.data['amount'] < 0:
            return Response({'message': 'Negative amount is not allowed'}, status=HTTP_400_BAD_REQUEST)
        account.balance += request.data['amount']
        account.save()
        AccountHistory.objects.create(
            account=account,
            amount=request.data['amount'],
            balance_after_transfer=account.balance,
            description=request.data['description'],
            type='I'
        )
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def transfer_from_account(self, request, pk=None):
        account = get_object_or_404(Account, id=pk)
        if account.owner != request.user:
            return Response(status=HTTP_404_NOT_FOUND)
        if account.balance <= 0 or request.data['amount'] > account.balance:
            return Response({'message': 'You do not have enough funds in your account'}, status=HTTP_400_BAD_REQUEST)
        if request.data['amount'] < 0:
            return Response({'message': 'Negative amount is not allowed'}, status=HTTP_400_BAD_REQUEST)
        account.balance -= request.data['amount']
        account.save()
        AccountHistory.objects.create(
            account=account,
            amount=request.data['amount'],
            balance_after_transfer=account.balance,
            description=request.data['description'],
            type='O'
        )
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def check_balance(self, request, pk=None):
        account = get_object_or_404(Account, id=pk)
        if account.owner != request.user:
            return Response(status=HTTP_404_NOT_FOUND)
        return Response({'balance': account.balance})
