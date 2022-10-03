import traceback

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.mixins import IsSubscribedMixin

from users.models import User

from .models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                     ShoppingCart, Tag, TagsRecipe)


class AuthorSerializer(serializers.ModelSerializer, IsSubscribedMixin):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'slug'


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientsRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(max_value=32767, min_value=1)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_status_func(self, data, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        if self.context.get('request').user:
            user = self.context.get('request').user
        else:
            user = self.context.get('user')
        init_queryset = model.objects.filter(recipe=data, user=user)
        if init_queryset.exists():
            return True
        return False

    def get_is_favorited(self, data):
        return self.get_status_func(data, model=Favorite)

    def get_is_in_shopping_cart(self, data):
        return self.get_status_func(data, model=ShoppingCart)

    def create(self, validated_data):
        context = self.context['request']
        ingredients = validated_data.pop('recipe_ingredients')
        if Recipe.objects.create(**validated_data,
                                 author=self.context.get('request').user):
            recipe = Recipe.objects.create(
                **validated_data,
                author=self.context.get('request').user
            )
        else:
            pass
        tags_set = context.data['tags']
        for tag in tags_set:
            TagsRecipe.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=tag)
            )
        ingredients_set = context.data['ingredients']
        for ingredient in ingredients_set:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            IngredientsRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        context = self.context['request']
        ingredients = validated_data.pop('recipe_ingredients')
        tags_set = context.data['tags']
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        instance.tags.set(tags_set)
        IngredientsRecipe.objects.filter(recipe=instance).delete()
        ingredients_req = context.data['ingredients']
        for ingredient in ingredients_req:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            IngredientsRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient['amount'],
            )
        return instance

    def to_representation(self, instance):
        response = super(RecipeSerializer, self).to_representation(instance)
        if instance.image:
            response['image'] = instance.image.url
        return response


class FavoritedSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True, source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True, source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True, source='recipe.name',
    )

    def create(self, validated_data):
        favorite = Favorite.objects.create(**validated_data)
        favorite.save()
        return favorite

    class Meta:
        model = Favorite
        fields = ('id', 'cooking_time', 'name', 'image', 'user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'cooking_time', 'name', 'image', 'user', 'recipe')
