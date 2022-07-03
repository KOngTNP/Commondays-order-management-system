from re import A
from traceback import print_tb
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from apscheduler.schedulers.background import BackgroundScheduler

from mysite.models import Product, Statement, Account, Order, Stock
from .forms import CreateStatementForm, CreateProductForm
from taggit.models import Tag

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import numpy as np

def tagged(request, slug):
    tag = get_object_or_404(Tag, name=slug)
    statement = Statement.objects.filter(tags=tag)
    data = [1500,1000,3000,5000,12000,2000]
    context={'data':data, 'statement':statement}
    return render(request,'table.html',context)
@login_required
def dashboard(request):
    return render(request,'dashboard.html')
@login_required
def product(request):
    product = Product.objects.all()
    context = {'product':product}
    return render(request,'product/product.html',context)
@login_required
def createProduct(request):
    user = request.user
    if request.method == "POST":
        form = CreateProductForm(request.POST)
        if form.is_valid():
            form = form.save()
            return redirect("/product/")
    else:
        form = CreateProductForm(initial={'user': user})
    return render(request,'product/create_product.html', {'form': form})
@login_required
def productDetail(request,product_id):
    stock = Stock.objects.filter(product = product_id)
    order = Order.objects.filter(stock__in = stock)
    product = Product.objects.get(id = product_id)
    
    context = {'stock':stock, 'order':order, 'product':product}
    return render(request,'product/detail_product.html',context)
@login_required
def createStock(request,product_id):
    user = request.user
    if request.method == "POST":
        form = CreateProductForm(request.POST)
        if form.is_valid():
            form = form.save()
            return redirect("/product/")
    else:
        form = CreateProductForm(initial={'user': user})
    return render(request,'product/create_product.html', {'form': form})

    return render(request,'product/detail_product.html',context)
@login_required
def table(request):
    account = Account.objects.get(name = 'cash-flow')
    sell_list = [23,10,123,1234]
    last_income = Statement.objects.annotate(month=TruncMonth('date')).values('month').annotate(Sum('income_amount')).order_by()
    if len(last_income) >= 6:
        last_income = last_income[-6:]
    last_outcome = Statement.objects.annotate(month=TruncMonth('date')).values('month').annotate(Sum('outcome_amount')).order_by()
    if len(last_outcome) >= 6:
        last_outcome = last_outcome[-6:]


    profit = account.balance
    income = account.all_income
    income_list = []
    outcome = account.all_outcome
    outcome_list = []
    for item in last_income:
        if item['income_amount__sum'] == None:
            income_list.append(0)
        else:
            income_list.append(item['income_amount__sum'])
    for item in last_outcome:
        if item['outcome_amount__sum'] == None:
            outcome_list.append(0)
        else:
            outcome_list.append(item['outcome_amount__sum'])
    array1 = np.array(income_list)
    array2 = np.array(outcome_list)
    subtracted_array = np.subtract(array1, array2)
    profit_list = list(subtracted_array)

    if len(income_list) > 0 and len(outcome_list) > 0 and len(profit_list) > 0:
        if len(income_list) > 1 and income_list[-2] != 0:
            income_percent = float(format(((income_list[-1]-income_list[-2])/income_list[-2])*100,".2f"))
        else:
            income_percent = income_list[-1]
        if len(outcome_list) > 1 and outcome_list[-2] != 0:
            outcome_percent = float(format(((outcome_list[-1]-outcome_list[-2])/outcome_list[-2])*100,".2f"))
        else:
            outcome_percent = outcome_list[-1]
        if len(profit_list) > 1 and profit_list[-2] > 0:
            profit_percent = float(format(((profit_list[-1]-profit_list[-2])/profit_list[-2])*100,".2f"))
        if len(profit_list) > 1 and profit_list[-2] < 0:
            profit_percent = float(format(((profit_list[-1]+profit_list[-2])/profit_list[-2])*100,".2f"))
        else:
            print(profit_list)
            profit_percent = profit_list[-1]
    else:
        income_percent = 0
        outcome_percent = 0
        profit_percent = 0

    statement = Statement.objects.all()
    context={'profit':profit,'income':income,'outcome':outcome,'profit_list':profit_list,'income_list':income_list,'outcome_list':outcome_list,'sell_list':sell_list,'income_percent':income_percent,'outcome_percent':outcome_percent,'profit_percent':profit_percent, 'statement':statement}
    return render(request,'table.html',context)

@login_required
def createStatement(request):
    user = request.user
    if request.method == "POST":
        form = CreateStatementForm(request.POST)
        if form.is_valid():
            form = form.save()
            account = Account.objects.get(name = 'cash-flow')
            get_new_record = Statement.objects.filter(id = form.id)
            if form.option == "income" and form.income_amount != 0:
                get_new_record.update(outcome_amount = None)
                get_balance = account.balance + form.income_amount
                get_income = account.all_income + form.income_amount
                Account.objects.filter(name = 'cash-flow').update(balance = get_balance, all_income = get_income)
            elif form.option == "outcome" and form.outcome_amount != 0:
                get_new_record.update(income_amount = None)
                get_balance = account.balance - form.outcome_amount
                get_outcome = account.all_outcome + form.outcome_amount
                Account.objects.filter(name = 'cash-flow').update(balance = get_balance, all_outcome = get_outcome)
            else:
                error = "The value should more than 0"
                form = CreateStatementForm(initial={'user': user})
                return render(request,'statement/create_statement.html', {'form': form,'error':error})
            get_new_record.update(last_balance = account.balance)
            return redirect("/table/")
    else:
        form = CreateStatementForm(initial={'user': user})
    return render(request,'statement/create_statement.html', {'form': form})

@login_required
def deleteStatement(request,statement_id):
    get_statement_id = Statement.objects.get(id=statement_id)
    account = Account.objects.get(name = 'cash-flow')
    if get_statement_id.income_amount != None and get_statement_id.outcome_amount == None:
        get_balance = account.balance - get_statement_id.income_amount
        get_income = account.all_income - get_statement_id.income_amount
        Account.objects.filter(name = 'cash-flow').update(balance = get_balance, all_income = get_income)
    elif get_statement_id.outcome_amount != None and get_statement_id.income_amount == None:
        get_balance = account.balance + get_statement_id.outcome_amount
        get_outcome = account.all_outcome - get_statement_id.outcome_amount
        Account.objects.filter(name = 'cash-flow').update(balance = get_balance, all_outcome = get_outcome)
    else:
        error = "The value should more than 0"
        return redirect("/table/")
    get_statement_id.delete()
    return redirect("/table/")
