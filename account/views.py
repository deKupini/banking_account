from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from account.models import Account
from account.serializers import AccountSerializer


class AccountViewSet(ModelViewSet):
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
