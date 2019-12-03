from rest_framework import serializers
from rental.models import Friend, Belonging, Borrowed
from dynamic_rest.serializers import DynamicModelSerializer
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class FriendSerializer(DynamicModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Friend
        fields = ('id', 'name', 'email', 'owner', 'has_overdue')
        deferred_fields = ('has_overdue',)


class BelongingSerializer(DynamicModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Belonging
        fields = ('id', 'name', 'owner')


class BorrowedSerializer(DynamicModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item = serializers.ReadOnlyField(source='what.name')
    friend = serializers.ReadOnlyField(source='to_who.name')
    expandable_fields = {
        'item': serializers.ReadOnlyField(source='what.name'),
        'friend': serializers.ReadOnlyField(source='to_who.name'),
        'what': (BelongingSerializer, {'source': 'what'}),
        'to_who': (FriendSerializer, {'source': 'to_who'})
    }
    
    class Meta:
        model = Borrowed
        fields = ('id', 'what', 'item', 'to_who', 'friend', 'when', 'returned', 'owner')


class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
