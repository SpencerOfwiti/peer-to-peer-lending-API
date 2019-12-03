from rest_framework import viewsets, status
from rental import models, serializers, permissions, custom_filter, authentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework_extensions.mixins import NestedViewSetMixin
from dynamic_rest.viewsets import DynamicModelViewSet
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.contrib.auth.models import User

# Create your views here.


class FriendViewSet(NestedViewSetMixin, DynamicModelViewSet):
    queryset = models.Friend.objects.with_overdue()
    serializer_class = serializers.FriendSerializer
    permission_classes = [permissions.IsOwner, IsAuthenticatedOrReadOnly]


class BelongingViewSet(NestedViewSetMixin, DynamicModelViewSet):
    queryset = models.Belonging.objects.all()
    serializer_class = serializers.BelongingSerializer
    permission_classes = [permissions.IsOwner, IsAuthenticatedOrReadOnly]


class BorrowedViewSet(NestedViewSetMixin, DynamicModelViewSet):
    queryset = models.Borrowed.objects.all().select_related('to_who', 'what')
    permit_list_expands = ['what', 'to-who']
    serializer_class = serializers.BorrowedSerializer
    permission_classes = [permissions.IsOwner, IsAuthenticatedOrReadOnly]
    filterset_class = custom_filter.BorrowedFilterSet

    @action(detail=True, url_path='remind', methods=['post'])
    def remind_single(self, request, *args, **kwargs):
        obj = self.get_object()
        send_mail(
            subject=f'Please return my belonging: {obj.what.name}',
            message=f'You forgot to return my belonging: "{obj.what.name}" that you borrowed on {obj.when}. Please return it.',
            from_email='maxspencer56@gmail.com',
            recipient_list=[obj.to_who.email],
            fail_silently=False
        )
        return Response(f'Email sent to {obj.to_who.name}')


@api_view(['POST'])
@permission_classes((AllowAny,))
def signin(request):
    signin_serializer = serializers.UserSigninSerializer(data=request.data)
    if not signin_serializer.is_valid():
        return Response(signin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(
        username = signin_serializer.data['username'],
        password = signin_serializer.data['password']
    )
    if not user:
        return Response({'detail': 'Invalid Credentials or activate account'}, status=status.HTTP_404_NOT_FOUND)

    # retrieve users token
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate a new one
    is_expired, token = authentication.token_expire_handler(token)
    if is_expired:
        token.delete()
        token = Token.objects.create(user=user)
    user_serialized = serializers.UserSerializer(user)

    return Response({
        'user': user_serialized.data,
        'expires_in': authentication.expires_in(token),
        'token': token.key,
        'is_expired': is_expired
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_info(request):
    is_expired, token = authentication.token_expire_handler(request.auth)
    return Response({
        'user': request.user.username,
        'password': request.user.password,
        'expires_in': authentication.expires_in(request.auth),
        'is_expired': is_expired
    }, status=status.HTTP_200_OK)


@permission_classes((AllowAny,))
class UserCreate(APIView):
    """
    Creates the user
    """
    def post(self, request, format='json'):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
