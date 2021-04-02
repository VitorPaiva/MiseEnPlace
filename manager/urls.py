from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('recipes/', views.recipes, name='recipes'),
    path('recipes/create', login_required(views.CreateRecipe.as_view()), name='create_recipe'),
    path('recipes/<slug:slug>', login_required(views.UpdateRecipe.as_view()), name='recipe_update'),
    path('recipes/<slug:slug>/details', views.recipe_details, name='recipe_details'),
    path('ingredients/', views.ingredients, name='ingredients'),
    path('ingredients/create', login_required(views.CreateIngredient.as_view()), name='create_ingredient'),
    path('ingredients/<slug:slug>', login_required(views.UpdateIngredient.as_view()), name='ingredient_update'),
]
