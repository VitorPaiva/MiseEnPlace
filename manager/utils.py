
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import *
import random
import string


'''

    Parameters: 
        request - GET request with the «currency» value 
        obj - Ingredient that will be converted

    Returns:
     Ingredient object with the price converted

    Converts the price of a ingredient for the desired currency, in the request

'''
def currency_rate(request, obj):

    currency_filter = request.GET.get('currency', '')
    
    try:
        currency = Currency.objects.get(label = currency_filter)
    except ObjectDoesNotExist:
        currency = False

    if currency and currency.label != obj.currency.label:
        currency_rate = CurrencyRate.objects.all().filter(Q(original_currency = obj.currency) & Q(rating_currency = currency))
        if not currency_rate:
            currency_rate = CurrencyRate.objects.all().filter(Q(original_currency = currency) & Q(rating_currency = obj.currency))
        obj.price = round(obj.price * currency_rate[0].rate, 2)
        obj.currency = currency
        
    return obj


'''

    Parameters: 
        context - View context

    Returns:
        context

    Loads list of units and ingredients into context

'''
def load_units_and_ingredients(context):
    ingredients = get_ingredients_by_name()
    units = Unit.objects.all()
    context["ingredients"] = ingredients
    context["units"] = units
    return context

'''

    Parameters: 
        order - either an empty string for «ascending» of '-' for «descending»

    Returns:
        Ingredient list ordered by name

    Gets the Ingredient list ordered by name ignoring the case.

'''
def get_ingredients_by_name(order = ''):
    ingredient_list = Ingredient.objects.all().extra(select={'lower_name':'lower(name)'})
    if order == '-':
        return ingredient_list.order_by('-lower_name')
    return ingredient_list.order_by('lower_name')


'''

    Parameters: 
        request - request to wit the GET fields
        ingredient_list - list of RecipeIngredient 

    Returns:
        total recipe price

    Return the total recipe price, formated with only 2 decimal places.
    This method will also convert all the Ingredients currencies for the one in the request.

'''
def get_recipe_price(request, ingredient_list):
    price = 0

    for ingredient in ingredient_list:
        dummy = Ingredient(name='dummy', price=ingredient.get_rate_price(), currency=ingredient.ingredient.currency)
        currency = currency_rate(request, dummy)
        price = price + currency.price
    return "{:.2f}".format(round(price,2)), currency
