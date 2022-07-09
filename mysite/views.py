from re import A
from traceback import print_tb
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from apscheduler.schedulers.background import BackgroundScheduler

from mysite.models import Product, Statement, Account, Order, Stock, Customer, Item
from .forms import CreateStatementForm, UpdateStatementForm, CreateProductForm, UpdateProductForm, CreateStockForm, UpdateStockForm, CreateOrderForm, UpdateOrderForm, CreateCustomerForm, CreateItemForm, UpdateItemForm
from taggit.models import Tag
from django.template.loader import render_to_string
from django.http import JsonResponse

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
    posted_by = request.user
    if request.method == "POST":
        form = CreateProductForm(request.POST)
        if form.is_valid():
            form = form.save()
            return redirect("/product/")
    else:
        form = CreateProductForm(initial={'posted_by': posted_by})
    return render(request,'product/create_product.html', {'form': form})
@login_required
def editProduct(request,product_id):
    get_product = Product.objects.get(id=product_id)
    return render(request, 'product/edit_product.html',{'get_product':get_product})
@login_required
def updateProduct(request,product_id):
    get_product = Product.objects.get(id=product_id)
    form = UpdateProductForm(request.POST, instance=get_product)
    if form.is_valid():
        form.save()
        return redirect("/product/")
    return render(request, 'product/edit_product.html',{'get_product':get_product, 'form':form})
@login_required
def deleteProduct(request,product_id):
    get_product = Product.objects.get(id=product_id)
    if request.user.is_superuser:
        get_product.delete()
    return redirect("/product/")

@login_required
def productDetail(request,product_id):
    stock = Stock.objects.filter(product = product_id)
    items = Item.objects.filter(stock__in = stock)


    product = Product.objects.get(id = product_id)
    
    context = {'stock':stock,  'product':product, 'items':items}
    return render(request,'product/detail_product.html',context)


@login_required
def createStock(request,product_id):
    posted_by = request.user
    product = Product.objects.get(id = product_id)
    if request.method == "POST":
        form = CreateStockForm(request.POST)
        if form.is_valid():
            form = form.save()
            return redirect(f"/product/detail/{product_id}")
    else:
        form = CreateStockForm(initial={'posted_by': posted_by, 'product':product})

    return render(request,'stock/create_stock.html',{'form': form,'product':product})

@login_required
def editStock(request,product_id,stock_id):
    posted_by = request.user
    get_stock = Stock.objects.get(id=stock_id)
    product = Product.objects.get(id = product_id)
    return render(request, 'stock/edit_stock.html',{'get_stock':get_stock, 'product':product, 'posted_by':posted_by})

@login_required
def updateStock(request,product_id,stock_id):
    posted_by = request.user
    get_stock = Stock.objects.get(id=stock_id)
    product = Product.objects.get(id = product_id)
    form = UpdateStockForm(request.POST, instance=get_stock)
    if form.is_valid():
        form.save()
        return redirect(f"/product/detail/{product.id}")
    return render(request, 'stock/edit_stock.html',{'get_stock':get_stock, 'form':form, 'product':product, 'posted_by':posted_by})
@login_required
def order(request):
    get_order = Order.objects.all()

    return render(request,'order/order.html', {'get_order':get_order})
@login_required
def createOrder(request):
    posted_by = request.user
    get_customer = Customer.objects.all()
    get_account = Account.objects.all()
    if request.method == "POST":
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            if form.platform == "Other":
                form.sum_price = None
            form.save()
            # create statement
            get_last_balance = Account.objects.get(id = form.account.id)
            new_statement = Statement.objects.create(date = form.date, item=(f'Form {form.customer.name}'), option="income", income_amount=form.sum_price, account=form.account, last_balance=get_last_balance.balance, posted_by=form.posted_by, order=form)
            new_statement.tags.add("Sell")
            # update balance
            if form.sum_price != None:
                get_balance = get_last_balance.balance + form.sum_price
                get_income = get_last_balance.all_income + form.sum_price
                new_balance = Account.objects.filter(id = form.account.id)
                new_balance.update(balance = get_balance, all_income = get_income)
                new_statement = Statement.objects.filter(order = form)
                new_statement.update(last_balance=get_balance)
            # ---------------- 
            return redirect(f"/order/{form.id}/item")
    else:
        form = CreateOrderForm(initial={'posted_by': posted_by,})

    return render(request,'order/create_order.html',{'form': form,'get_customer':get_customer, 'get_account':get_account,})

@login_required
def editOrder(request,order_id):
    posted_by = request.user
    get_order = Order.objects.get(id = order_id)
    get_customer = Customer.objects.all()
    get_account = Account.objects.all()
    return render(request,'order/edit_order.html',{'get_order': get_order,'get_customer':get_customer, 'get_account':get_account,'posted_by':posted_by})

@login_required
def updateOrder(request, order_id):
    posted_by = request.user
    get_order = Order.objects.get(id = order_id)
    print(f"123123asdasdasd {get_order.sum_price}")
    get_customer = Customer.objects.all()
    get_account = Account.objects.all()
    form = UpdateOrderForm(request.POST, instance=get_order)
    if form.is_valid():
        form = form.save(commit=False)
        get_item = Item.objects.filter(order = get_order)
        if form.platform == "Other":
            sum_price = 0
            for item in get_item:
                if item.price == None:
                    Item.objects.filter(id = item.id).update(price = item.stock.price)
                new_item = Item.objects.get(id = item.id)
                sum_price += new_item.quantity * new_item.price
            form.sum_price = sum_price
        else:
            sum_price = form.sum_price
            for item in get_item:
                Item.objects.filter(id = item.id).update(price = None)

        get_order = Order.objects.get(id = order_id)
        form.save()
        # update statement
        Statement.objects.filter(order = form.id).update(income_amount = sum_price)
        # update balance
        get_last_balance = Account.objects.get(id = form.account.id)
        if form.sum_price != None:
            get_balance = (get_last_balance.balance + form.sum_price) - get_order.sum_price
            get_income = (get_last_balance.all_income + form.sum_price) - get_order.sum_price
            new_balance = Account.objects.filter(id = form.account.id)
            new_balance.update(balance = get_balance, all_income = get_income)
            new_statement = Statement.objects.filter(order = form)
            new_statement.update(last_balance=get_balance)
        else:
            get_balance = get_last_balance.balance - get_order.sum_price
            get_income = get_last_balance.all_income - get_order.sum_price
            new_balance = Account.objects.filter(id = form.account.id)
            new_balance.update(balance = get_balance, all_income = get_income)
            new_statement = Statement.objects.filter(order = form)
            new_statement.update(last_balance=get_balance)
        # ----------------
        return redirect(f"/order/{form.id}/item")

    return render(request,'order/edit_order.html',{'get_order': get_order,'get_customer':get_customer, 'get_account':get_account,'form':form, 'posted_by':posted_by})

@login_required
def createItem(request, order_id):
    posted_by = request.user
    order = Order.objects.get(id = order_id)
    get_item = Item.objects.filter(order = order)
    item_list = []
    for filter_item in get_item:
        item_list.append(filter_item.stock.id)
    get_stock = Stock.objects.filter(~Q(quantity=0), ~Q(id__in=item_list))
    sum_price = 0
    if order.platform != "Other":
        sum_price = order.sum_price
    else:
        for item in get_item:
            sum_price += item.quantity * item.price

    if request.method == "POST":
        form = CreateItemForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            if order.platform != "Other":
                form.price = None
            else:
                form.price = form.stock.price
                sum_price = sum_price+(form.price*form.quantity)
                new_order = Order.objects.filter(id = form.order.id).update(sum_price=sum_price)
                # update balance
                get_last_balance = Account.objects.get(id = form.order.account.id)
                if form.price != None:
                    get_balance = (get_last_balance.balance + form.price*form.quantity)
                    get_income = (get_last_balance.all_income + form.price*form.quantity)
                    new_balance = Account.objects.filter(id = form.order.account.id)
                    new_balance.update(balance = get_balance, all_income = get_income)
                    new_statement = Statement.objects.filter(order = form.order)
                    new_statement.update(last_balance=get_balance)
                #------------
            # update stock
            get_update_stock = Stock.objects.get(id = form.stock.id)
            Stock.objects.filter(id = form.stock.id).update(quantity = get_update_stock.quantity-form.quantity)
            #------------

            # update statement
            Statement.objects.filter(order = form.order.id).update(income_amount = sum_price)
            # ----------------

            form.save()
            return redirect(f"/order/{order_id}/item")
    else:
        form = CreateItemForm(initial={'posted_by': posted_by,'order':order})

    return render(request,'item/item_list.html',{'form': form,'get_item':get_item,'get_stock':get_stock, 'order':order, 'sum_price':sum_price})

@login_required
def editItem(request, order_id, item_id):
    posted_by = request.user
    order = Order.objects.get(id = order_id)
    get_item = Item.objects.filter(order = order)
    get_item_edit = Item.objects.get(id = item_id)
    item_list = []
    for filter_item in get_item:
        item_list.append(filter_item.stock.id)
    get_stock = Stock.objects.filter(~Q(quantity=0), ~Q(id__in=item_list))
    sum_price = 0
    if order.platform != "Other":
        sum_price = order.sum_price
    else:
        for item in get_item:
            sum_price += item.quantity * item.price

    if request.method == "POST":
        form = UpdateItemForm(request.POST, instance=get_item_edit)
        if form.is_valid():
            get_item_edit = Item.objects.get(id = item_id)
            form = form.save(commit=False)
            if order.platform != "Other":
                form.price = None
                form.save()
            else:
                get_last_item = Item.objects.get(id = form.id)
                form.save()
                sum_price = 0
                get_item = Item.objects.filter(order = order)
                for item in get_item:
                    sum_price += item.quantity * item.price
                Order.objects.filter(id = form.order.id).update(sum_price=sum_price)
                # update balance
                get_last_balance = Account.objects.get(id = form.order.account.id)
                if form.price != None:
                    get_balance = (get_last_balance.balance + form.price*form.quantity)-(get_last_item.price*get_last_item.quantity)
                    get_income = (get_last_balance.all_income + form.price*form.quantity)-(get_last_item.price*get_last_item.quantity)
                    new_balance = Account.objects.filter(id = form.order.account.id)
                    new_balance.update(balance = get_balance, all_income = get_income)
                    new_statement = Statement.objects.filter(order = form.order)
                    new_statement.update(last_balance=get_balance)
                #------------
            # update stock
            get_update_stock = Stock.objects.get(id = form.stock.id)
            new_stock = Stock.objects.filter(id = form.stock.id)
            new_stock.update(quantity = (get_update_stock.quantity+get_item_edit.quantity)-form.quantity)
            #------------

            # update statement
            Statement.objects.filter(order = form.order.id).update(income_amount = sum_price)
            # ----------------
            return redirect(f"/order/{order_id}/item")
    else:
        form = UpdateItemForm(initial={'order':order,'posted_by':posted_by})
    return render(request,'item/edit_item.html',{'form':form, 'order':order, 'get_item':get_item,'get_item_edit':get_item_edit, 'get_stock':get_stock, 'sum_price':sum_price})

@login_required
def deleteItem(request,order_id,item_id):
    order = Order.objects.get(id = order_id)
    get_delete_item = Item.objects.get(id = item_id)

    # update balance
    get_last_balance = Account.objects.get(id = get_delete_item.order.account.id)
    if get_delete_item.price != None:
        get_balance = (get_last_balance.balance-(get_delete_item.price*get_delete_item.quantity))
        get_income = (get_last_balance.all_income-(get_delete_item.price*get_delete_item.quantity))
        new_balance = Account.objects.filter(id = get_delete_item.order.account.id)
        new_balance.update(balance = get_balance, all_income = get_income)
        new_statement = Statement.objects.filter(order = get_delete_item.order)
        new_statement.update(last_balance=get_balance)
    #------------
    # update stock
    get_stock = Stock.objects.get(id = get_delete_item.stock.id)
    Stock.objects.filter(id = get_delete_item.stock.id).update(quantity = get_stock.quantity+get_delete_item.quantity)
    #------------

    get_delete_item.delete()
    sum_price = 0
    get_item = Item.objects.filter(order = order)
    if order.platform == "Other":
        for item in get_item:
            sum_price += item.quantity * item.price
            Order.objects.filter(id = order_id).update(sum_price=sum_price)
    return redirect(f"/order/{order_id}/item")

@login_required 
def get_table(requset):
    account = Account.objects.all().first()
    return redirect(f"/table/{account.id}/")
@login_required
def table(request,account_id):
    get_all_account = Account.objects.all()
    account = Account.objects.get(id = account_id)

    last_sell = Item.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(Sum('quantity')).order_by()
    if len(last_sell) >= 6:
        last_sell = last_sell[-6:]
    last_income = Statement.objects.filter(account=account).annotate(month=TruncMonth('date')).values('month').annotate(Sum('income_amount')).order_by()
    if len(last_income) >= 6:
        last_income = last_income[-6:]
    last_outcome = Statement.objects.filter(account=account).annotate(month=TruncMonth('date')).values('month').annotate(Sum('outcome_amount')).order_by()
    if len(last_outcome) >= 6:
        last_outcome = last_outcome[-6:]

    sell = Item.objects.aggregate(Sum('quantity'))
    sell = list(sell.values())[0]
    sell_list = []
    profit = account.balance
    profit = ("%.2f" % profit)
    income = account.all_income
    income = ("%.2f" % income)
    income_list = []
    outcome = account.all_outcome
    outcome = ("%.2f" % outcome)
    outcome_list = []
    for item in last_sell:
        if item['quantity__sum'] == None:
            sell_list.append(0)
        else:
            sell_list.append(item['quantity__sum'])
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
        elif len(profit_list) > 1 and profit_list[-2] < 0:
            profit_percent = float(format(((profit_list[-1]-profit_list[-2])/(-profit_list[-2]))*100,".2f"))
        else:
            profit_percent = profit_list[-1]
    else:
        income_percent = 0
        outcome_percent = 0
        profit_percent = 0

    statement = Statement.objects.filter(account=account)
    context={'profit':profit,'income':income,'outcome':outcome,'profit_list':profit_list,'income_list':income_list,'outcome_list':outcome_list,'sell_list':sell_list,'income_percent':income_percent,'outcome_percent':outcome_percent,'profit_percent':profit_percent, 'statement':statement, 'sell':sell, 'get_all_account':get_all_account, 'account':account,'account_id':account_id}
    return render(request,'table.html',context)

@login_required
def createStatement(request,account_id):
    posted_by = request.user
    if request.method == "POST":
        form = CreateStatementForm(request.POST)
        if form.is_valid():
            form = form.save()
            account = Account.objects.get(id = account_id)
            get_new_record = Statement.objects.filter(id = form.id)
            if form.option == "income" and form.income_amount != 0:
                get_new_record.update(outcome_amount = None)
                get_balance = account.balance + form.income_amount
                get_income = account.all_income + form.income_amount
                Account.objects.filter(id = account_id).update(balance = get_balance, all_income = get_income)
            elif form.option == "outcome" and form.outcome_amount != 0:
                get_new_record.update(income_amount = None)
                get_balance = account.balance - form.outcome_amount
                get_outcome = account.all_outcome + form.outcome_amount
                Account.objects.filter(id = account_id).update(balance = get_balance, all_outcome = get_outcome)
            else:
                error = "The value should more than 0"
                form = CreateStatementForm(initial={'posted_by': posted_by})
                return render(request,'statement/create_statement.html', {'form': form,'error':error})
            get_new_record.update(last_balance = account.balance)
            return redirect(f"/table/{account_id}/")
    else:
        form = CreateStatementForm(initial={'posted_by': posted_by,})
    return render(request,'statement/create_statement.html', {'form': form,'account_id':account_id})

@login_required
def editStatement(request,statement_id, account_id):
    posted_by = request.user
    get_statement = Statement.objects.get(id=statement_id)
    return render(request, 'statement/edit_statement.html',{'get_statement':get_statement, 'account_id':account_id, 'posted_by':posted_by})

@login_required
def updateStatement(request,statement_id, account_id):
    posted_by = request.user
    get_statement = Statement.objects.get(id=statement_id)
    account = Account.objects.get(id = account_id)
    form = UpdateStatementForm(request.POST, instance=get_statement)
    if form.is_valid():
        get_statement = Statement.objects.get(id=statement_id)
        form = form.save()
        get_new_record = Statement.objects.filter(id = form.id)
        if form.option == "income" and form.income_amount != 0:
            get_new_record.update(outcome_amount = None)
            get_balance = account.balance + form.income_amount
            get_income = account.all_income + form.income_amount
            Account.objects.filter(id = account_id).update(balance = get_balance, all_income = get_income)
        elif form.option == "outcome" and form.outcome_amount != 0:
            get_new_record.update(income_amount = None)
            get_balance = account.balance - form.outcome_amount
            get_outcome = account.all_outcome + form.outcome_amount
            Account.objects.filter(id = account_id).update(balance = get_balance, all_outcome = get_outcome)
        get_new_record.update(last_balance = account.balance)

        account = Account.objects.get(id = account_id)
        if get_statement.income_amount != None and get_statement.outcome_amount == None:
            get_balance = account.balance - get_statement.income_amount
            get_income = account.all_income - get_statement.income_amount
            Account.objects.filter(id = account_id).update(balance = get_balance, all_income = get_income)
        elif get_statement.outcome_amount != None and get_statement.income_amount == None:
            get_balance = account.balance + get_statement.outcome_amount
            get_outcome = account.all_outcome - get_statement.outcome_amount
            Account.objects.filter(id = account_id).update(balance = get_balance, all_outcome = get_outcome) 
        return redirect(f"/table/{account_id}/")

    return render(request, 'statement/edit_statement.html',{'get_statement':get_statement, 'form':form, 'account_id':account_id,'posted_by':posted_by})

@login_required
def deleteStatement(request,statement_id, account_id):
    get_statement_id = Statement.objects.get(id=statement_id)
    account = Account.objects.get(id = account_id)
    if get_statement_id.income_amount != None and get_statement_id.outcome_amount == None:
        get_balance = account.balance - get_statement_id.income_amount
        get_income = account.all_income - get_statement_id.income_amount
        Account.objects.filter(id = account_id).update(balance = get_balance, all_income = get_income)
    elif get_statement_id.outcome_amount != None and get_statement_id.income_amount == None:
        get_balance = account.balance + get_statement_id.outcome_amount
        get_outcome = account.all_outcome - get_statement_id.outcome_amount
        Account.objects.filter(id = account_id).update(balance = get_balance, all_outcome = get_outcome)
    else:
        error = "The value should more than 0"
        return redirect(f"/table/{account_id}/")
    get_statement_id.delete()
    return redirect(f"/table/{account_id}/")


#=======================================Ajax===============================================
@login_required
def create_customer(request):
    data = dict()
    posted_by = request.user
    if request.method == 'POST':
        form = CreateCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            get_customer = Customer.objects.all()
            get_last_add = Customer.objects.first()
            data['customer_list'] = render_to_string('order/update_customer_list.html',{'get_customer':get_customer, 'get_last_add':get_last_add})
        else:
            data['form_is_valid'] = False
    else:
        form = CreateCustomerForm(initial={'posted_by':posted_by})
    context = {
        'form':form
    }
    data['html_form'] = render_to_string('customer/create_customer.html',context, request=request)
    return JsonResponse(data)

def custom_page_not_found_view(request, exception):
    return render(request, "errors/404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})