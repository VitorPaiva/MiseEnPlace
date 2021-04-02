from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout as logoutUser
from django.db.models import Q
from .models import *
from .utils import *
from .forms import *


#Home View
def home(request):
    return render(request, 'manager/home.html')

#Log Out View
def logout(request):
    logoutUser(request)
    return redirect(reverse('manager:home'))

#Login Class
class Login(LoginView):
    template_name = 'manager/login.html'
    success_url = 'home'

    def post(self, request, *args, **kargs):
        post = super().post(request, *args, **kargs)
        
        if(post.status_code == 302):
            return post
        else:
            return render(request, 
                     self.template_name, 
                      {'username': request.POST.get('username')})

#Ingredient List View
def ingredients(request):
    search_query = request.GET.get('search', False)
    ingredients = Ingredient.objects.all().order_by('name').filter(Q(name__icontains=search_query or '') | 
                                                                   Q(article_number__icontains=search_query or ''))
    for ingredient in ingredients:
        ingredient = currency_rate(request, ingredient)
    
    return render(request, 'manager/ingredient/index.html', {'ingredients': ingredients, 'anim': not search_query, "currencies": Currency.objects.all()})


class CreateIngredient(CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'manager/ingredient/create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('manager:ingredients')

class UpdateIngredient(UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = 'manager/ingredient/update.html'

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        currency_rate(request, self.get_object())
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('manager:ingredients')

# Recipe List View
def recipes(request):
    search_query = request.GET.get('search', False)
    ingredients = RecipeIngredient.objects.filter(Q(recipe__name__icontains=search_query or '') | Q(ingredient__name__icontains=search_query or ''))
    recipes = {}
    for ingredient in ingredients:
        if(ingredient.recipe in recipes):
            recipes[ingredient.recipe].append(ingredient)
        else:
            recipes[ingredient.recipe] = [ingredient]

    for recipe in recipes:
        recipe.ingredients=recipes[recipe]
        recipe.price, recipe.currency = get_recipe_price(request, recipe.ingredients)

    return render(request, 'manager/recipe/index.html', {'recipes': recipes, 'anim': not search_query, "currencies": Currency.objects.all()})


class CreateRecipe(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'manager/recipe/create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kargs):
        return super().get(request, *args, **kargs)

    def post(self, request, *args, **kargs):
        name = request.POST.get('name')
        recipe_post = super().post(request, *args, **kargs)
        if(recipe_post.status_code == 302):
            recipe = Recipe.objects.filter(name=name).order_by('-created_date')[0]
            self.addIngredientsToRecipe(request, recipe)
        return recipe_post

    def addIngredientsToRecipe(self, request, recipe):
        ingredients = request.POST.get('ingredients').split(';')

        for ingredient in ingredients[:len(ingredients)-1]:
            data = ingredient.split(',')
            ingredient = Ingredient.objects.get(name=data[0])
            quantity = data[1]
            unit = Unit.objects.get(label=data[2])
            recipe_ingredient = RecipeIngredient(recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit)
            recipe_ingredient.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = load_units_and_ingredients(context)
        return context

    def get_success_url(self):
        return reverse('manager:recipes')


class UpdateRecipe(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'manager/recipe/update.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=self.get_object()).order_by('recipe')
        context["recipe_ingredients"] = recipe_ingredients
        context = load_units_and_ingredients(context)
        return context

    def post(self, request, *args, **kargs):
        recipe_post = super().post(request, *args, **kargs)
        self.addIngredientsToRecipe(request, self.get_object())
        return recipe_post

    def addIngredientsToRecipe(self, request, recipe):
        ingredients = request.POST.get('ingredients').split(';')
        ingredients = ingredients[:len(ingredients)-1]
        print(self.get_object())
        RecipeIngredient.objects.filter(recipe=self.get_object()).delete()
         
        for ingredient in ingredients:
            data = ingredient.split(',')
            ingredient = Ingredient.objects.get(name=data[0])
            quantity = data[1]
            unit = Unit.objects.get(label=data[2])
            recipe_ingredient = RecipeIngredient(recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit)
            recipe_ingredient.save()
                
    def get_success_url(self):
        return reverse('manager:recipes')

def recipe_details(request, slug):
    recipe = Recipe.objects.get(slug=slug)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe).order_by('id')
    price, currency = get_recipe_price(request, ingredients)

    recipes = Recipe.objects.filter(~Q(slug=slug))
    ingredients_as_set = set(ingredients.values_list('ingredient', flat=True))
    reps = []
    for re in recipes:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=re).order_by('id').values_list('ingredient', flat=True)
        reps.append((len(list(ingredients_as_set.intersection(recipe_ingredients))), re))

    reps.sort(reverse=True, key=lambda rep: rep[0])
    recipes = [recipe[1] for recipe in reps[0:3] if recipe[0] > 0]

    for re in recipes:
        re.ingredients = RecipeIngredient.objects.filter(recipe = re)
        re.price, re.currency = get_recipe_price(request, re.ingredients)
            

    print(recipes)

    return render(request, 'manager/recipe/details.html', {'recipe': recipe, 'recipes': recipes, 'ingredients': ingredients, 'price': price, 'currency': currency.currency, 'currencies': Currency.objects.all()})