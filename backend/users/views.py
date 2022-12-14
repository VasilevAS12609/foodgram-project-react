from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

from recipes.models import Follow

from .models import User
from .serializers import UserSerializer, UserSubscribeSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        followed = get_object_or_404(User, id=id)
        follower = request.user

        if request.method == 'POST':
            subscribed = (Follow.objects.filter(
                author=followed, user=follower).exists()
            )
            if subscribed is True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.get_or_create(
                user=follower,
                author=followed
            )
            serializer = UserSubscribeSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=followed),
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            Follow.objects.filter(
                user=follower, author=followed
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        current_user = request.user
        followed_list = User.objects.filter(followed__user=current_user)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        authors = paginator.paginate_queryset(
            followed_list,
            request=request
        )
        serializer = ListSerializer(
            child=UserSubscribeSerializer(),
            context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(
            serializer.to_representation(authors)
        )
