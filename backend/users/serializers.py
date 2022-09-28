from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework import serializers, validators

from recipes.models import Follow, Recipe
from recipes.serializers import RecipeSerializer
from users.mixins import IsSubscribedMixin

from .models import User


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class UserSerializer(serializers.ModelSerializer, IsSubscribedMixin):
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )
        model = User


class UserSubscribeSerializer(serializers.ModelSerializer, IsSubscribedMixin):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        )

    def validate(self, data):
        author = data['followed']
        user = data['follower']
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        if (Follow.objects.filter(author=author, user=user).exists()):
            raise serializers.ValidationError('Вы уже подписаны на этого автора!')
        return data

    def create(self, validated_data):
        subscribe = Follow.objects.create(**validated_data)
        subscribe.save()
        return subscribe

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, data):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            data.recipes.all()[:int(recipes_limit)]
            if recipes_limit else data.recipes
        )
        serializer = serializers.ListSerializer(child=RecipeSerializer())
        return serializer.to_representation(recipes)
