from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet

from account.models import Account, AccountHistory
from account.serializers import AccountSerializer


class AccountViewSet(ModelViewSet):
    http_method_names = ('patch', 'post')
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=False, methods=['patch'])
    def transfer_to_account(self, request):
        account = get_object_or_404(Account, account_number=request.data['account_number'])
        if request.data['amount'] < 0:
            return Response({'message': 'Negative amount is not allowed'}, status=HTTP_404_NOT_FOUND)
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
