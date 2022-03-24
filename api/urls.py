from django.urls import path
from .views import *

urlpatterns = [
    path('moneyEntry/create', MoneyEntryCreate.as_view()),
    path('moneyEntry/update/<int:id>', MoneyEntryUpdate.as_view()),
    path('moneyEntry/list', MoneyEntryList.as_view()),
    path('moneyEntry/reports', MoneyEntryReport.as_view()),
    path('moneyEntry/expenseReport', ExpenseReport.as_view()),
    path('categories/list', CategoryList.as_view()),
    path('users/create', UserCreate.as_view()),
    path('users/update/<int:id>', UserUpdate.as_view()),
    path('users/get', UserProfile.as_view()),
    path('users/auth', UserLogin.as_view()),
    path('users/updateBudget/<int:id>', UserUpdateBudget.as_view())
]