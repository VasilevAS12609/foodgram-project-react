from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.permissions import AuthorOrReadOnly

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (FavoritedSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)

    @action(
        detail=True,
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite_and_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            favorite_recipe, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created is True:
                serializer = FavoritedSerializer()
                return Response(
                    serializer.to_representation(instance=favorite_recipe),
                    status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE':
            Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            recipe, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created is True:
                serializer = ShoppingCartSerializer()
                return Response(
                    serializer.to_representation(instance=recipe),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже в корзине покупок'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_shopping_list(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user).all()
        shopping_list = {}
        for item in shopping_cart:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                name = recipe_ingredient.ingredient.name
                measuring_unit = recipe_ingredient.ingredient.measurement_unit
                amount = recipe_ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        'name': name,
                        'measurement_unit': measuring_unit,
                        'amount': amount
                    }
                else:
                    shopping_list[name]['amount'] += amount
        content = (
            [f'{item["name"]} ({item["measurement_unit"]}) '
             f'- {item["amount"]}\n'
             for item in shopping_list.values()]
        )
        response = HttpResponse(
            content,
            content_type='text/plain; charset=WINDOWS-1251')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        try:
            return self.get_shopping_list(request)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
