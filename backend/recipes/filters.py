from django_filters import rest_framework as filters

from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.CharFilter(lookup_expr='exact')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='shopping_cart_filter'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='favorited_filter'
    )

    def shopping_cart_filter(self, queryset, name, value):
        queryset = queryset.filter(
            shopping_cart__user=self.request.user
        )
        return queryset

    def favorited_filter(self, queryset, name, value):
        queryset = queryset.filter(
            favorite_recipes__user=self.request.user
        )
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
