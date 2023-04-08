from rest_framework import serializers

from account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    account_number = serializers.IntegerField(read_only=True)
    balance = serializers.FloatField(read_only=True)
    creation_date = serializers.DateField(read_only=True)
    owner = serializers.CharField(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        account = Account.objects.create(owner=self.context['request'].user, **validated_data)
        return account
