from cmath import log
from os import stat
from typing import List
from unicodedata import category
from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime
from calendar import monthrange
from collections import defaultdict
from django.db.models.expressions import Value
from django.db.models.fields import CharField
from django.db.models.functions import Concat
from django.db.models import Sum
import operator

from .errres import errres
from .models import Category, User, MoneyEntry
from .serializers import *


# Create your views here.
class UserCreate(generics.CreateAPIView):
    set = User.objects.all()
    serializer_class = UserCreateSerializer

class UserLogin(generics.CreateAPIView):
    set = User.objects.all()
    serializer_class = UserLoginSerializer

class UserProfile(generics.CreateAPIView):
    serializer_class = UserSerializer
    pagination_class = None

    def get(self, req, *args, **kwargs):
        serializer = UserSerializer([req.login_user], many=True)

        return Response(serializer.data[0])

class UserUpdate(generics.CreateAPIView):
    serializer_class = UpdateUserSerializer
    set = User.objects.all()
    lookup_field = 'id'

    def put(self, req, *args, **kwargs):
        id = self.kwargs['id']
        serializer = UpdateUserSerializer()
        serializer.validate(req.data)

        user = User.objects.filter(id=id).first()

        if user is None:
            return errres("User doesn't exist", status.HTTP_400_BAD_REQUEST)

        user.name = req.data['name']
        user.email = req.data['email']
        user.save(update_fields=['name', 'email'])

        updatedUser = user.getObject()
        updatedUser['id'] = id

        return Response(updatedUser)

class UserUpdateBudget(generics.CreateAPIView):
    serializer_class = UserUpdateBudgetSerializer
    set = User.objects.all()
    lookup_field = 'id'

    def put(self, req, *args, **kwargs):
        id = self.kwargs['id']
        serializer = UserUpdateBudgetSerializer()
        serializer.validate(req.data)
        user = User.objects.filter(id=id).first()

        if user is None:
            return errres("User doesn't exist", status.HTTP_400_BAD_REQUEST)

        user.budget = int(req.data['budget'])
        # user.id = id
        user.save(update_fields=['budget'])

        myRes = user.getObject()
        myRes['id'] = id

        return Response(myRes)

class MoneyEntryCreate(generics.CreateAPIView):
    set = MoneyEntry.objects.all()
    serializer_class = MoneyEntrySerializer

    def post(self, req, *args, **kwargs):
        # ,"name": "OneChanged", "email": "onechanged@lmao.com"
        loginUser = json.loads(req.headers["Authorization"])
        ser = MoneyEntrySerializer()
        catId = int(req.data['category'])
        cat = Category.objects.get(id=catId)

        if cat is None:
            return errres('Category not found', status.HTTP_400_BAD_REQUEST)
        
        req.data._mutable = True
        req.data['user'] = loginUser['id']
        req.data['userId'] = loginUser['id']
        req.data['category'] = cat.id

        return self.create(req, *args, **kwargs)

class MoneyEntryUpdate(generics.CreateAPIView):
    serializer_class = MoneyEntrySerializer
    set = MoneyEntry.objects.all()
    lookup_field = 'id'

    def put(self, req, *args, **kwargs):
        loginUser = json.loads(req.headers["Authorization"])
        id = self.kwargs['id']
        serializer = MoneyEntrySerializer()
        serializer.validate(req.data)

        moneyEntry = MoneyEntry.objects.filter(id=id).first()

        if moneyEntry is None:
            return errres("Entry not found.", status.HTTP_400_BAD_REQUEST)

        catId = int(req.data['category'])
        cat = Category.objects.get(id=catId)

        if cat is None:
            return errres('Category not found.', status.HTTP_400_BAD_REQUEST)
        
        req.data['user']     = loginUser['id'], 
        req.data['category'] = cat.id
        moneyEntry.amount    = req.data['amount']
        moneyEntry.entryType = req.data['entryType']
        moneyEntry.name      = req.data['name']
        moneyEntry.category  = req.data['category']
        moneyEntry.date      = req.data['date']
        moneyEntry.save(update_fields=['amount', 'entryType', 'name', 'category', 'date'])

        return Response(req.data)

class MoneyEntryList(generics.ListAPIView):
    serializer_class = ListMoneyEntrySerializer

    def get(self, request, *args, **kwargs):
        loginUser = json.loads(request.headers["Authorization"])

        self.queryset = MoneyEntry.objects.order_by('-date').filter(userId = loginUser['id'])
        return self.list(request, *args, **kwargs)

class MoneyEntryReport(generics.ListAPIView):
    serializer_class = ListMoneyEntrySerializer

    def get(self, request, *args, **kwargs):
        loginUser = json.loads(request.headers["Authorization"])
        print(loginUser)
        current_date = datetime.today()
        current_year = current_date.year

        past_date = (current_date - relativedelta(months=3)).date()

        start_date = datetime(past_date.year, past_date.month, 1).date()
        end_date = datetime(current_year, current_date.month, monthrange(current_year, current_date.month)[-1]).date()

        transactions = MoneyEntry.objects.filter(
            userId = loginUser['id'], 
            date__gte=start_date,
            date__lte=end_date
        ).values("date__month", "date__year", 'entryType').annotate(
            total_amount=Sum('amount'), 
            date=Concat('date__month', Value('/'), 'date__year', 
            output_field=CharField())).order_by('date')

        # Groupby date transaction within expense and income
        list_result = [entry for entry in transactions] 
        groups = defaultdict(list)
        for obj in list_result:
            groups[obj['date']].append(obj)
        
        # Make sure that list result is consistently 4 arrays
        new_list = list(groups.values())
        result = [] 
        for i in range(4):
            if(i < len(new_list)):
                result.append(new_list[i])
            else:
                result.insert(0, [
                    { "date": "N/A", "type": "expense", "total_amount": 0 },
                    { "date": "N/A", "type": "income", "total_amount": 0 }
                ])

        return Response(result)

class ExpenseReport(generics.ListAPIView):
    serializer_class = ListMoneyEntrySerializer

    def get(self, request, *args, **kwargs):
        loginUser = json.loads(request.headers["Authorization"])
        current_date = datetime.today()
        current_year = current_date.year

        past_date = (current_date - relativedelta(months=3)).date()
        
        start_date = datetime(past_date.year, past_date.month, 1).date()
        end_date = datetime(current_year, current_date.month, monthrange(current_year, current_date.month)[-1]).date()

        transactions = MoneyEntry.objects.filter(
            userId=loginUser['id'], 
            entryType=True, 
            date__gte=start_date,
            date__lte=end_date
        ).values('category_id').annotate(total_amount=Sum('amount'))
        
        total_expense = sum(map(operator.itemgetter('total_amount'),transactions))

        for transaction in transactions:
            category = Category.objects.filter(id=transaction['category_id']).get()
            transaction['category_name'] = category.name
            transaction['total_amount_percent'] = transaction['total_amount'] * 100 / total_expense
            
        return Response({
            'data': transactions, 
            'total_expense': total_expense, 
            'budget': loginUser['budget'],
            'reminder': loginUser['budget'] - total_expense,
            })









class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None

# class MoneyEntryDelete(generics.CreateAPIView):
#     serializer_class = MoneyEntrySerializer
#     set = MoneyEntry.objects.all()
#     lookup_field = 'id'

#     def delete(self, req, *args, **kwargs):
#         id = self.kwargs['id']

#         moneyEntry = MoneyEntry.objects.filter

# class TransactionDelete(CustomLoginRequiredMixin, generics.DestroyAPIView):
#     serializer_class = TransactionSerializer
#     queryset = Transaction.objects.all()
#     lookup_field = 'id'

#     def delete(self, request, *args, **kwargs):
#         # Get URL Param
#         id = self.kwargs['id']

#         transaction = Transaction.objects.filter(user_id=request.login_user.id, id=id).first()

#         if transaction is None:
#             return error_response('Transaction not found.', status.HTTP_400_BAD_REQUEST)

#         self.destroy(request, *args, **kwargs)
        
#         return Response({'message': "Success."})
