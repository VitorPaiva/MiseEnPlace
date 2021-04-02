from django.contrib import admin

from .models import Unit, UnitRate, Currency, CurrencyRate, Ingredient, Recipe, RecipeIngredient

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'label']
    list_editable = ['label']

@admin.register(UnitRate)
class UnitRateAdmin(admin.ModelAdmin):
    list_display = ['unit', 'parent', 'rate']
    list_editable = ['rate']

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'symbol']
    list_editable = ['label', 'symbol']

@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ['original_currency', 'rating_currency', 'rate']
    list_editable = ['rate']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_number', 'price', 'currency', 'quantity', 'unit']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'currency', 'quantity', 'unit']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image', 'created_by', 'created_date', 'updated_date']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['name']
    list_display_links = None

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'quantity', 'unit']
    list_editable = ['quantity', 'unit']

