import json
import os
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View

from .models import Products, CartOrder, CartOrderItems, Customer, Order, StatisticsProducts, Invoice, Supplier, \
    CATEGORY_TYPE, product_directory_path


# Add to cart
def add_to_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        product_check = Products.objects.get(pid=prod_id)
        # print(product_check)
        product_id_default = product_check.id
        # print(product_id_default)
        if product_check:
            if CartOrder.objects.filter(user=request.user.id, product=product_id_default):
                return JsonResponse({'success': False, 'message': 'Product already in cart'})
            else:
                # Cart.objects.create(user=request.user, product=prod_id, quantity=1)
                cart_item = CartOrder(user=request.user, product=product_check, quantity=1)
                cart_item.save()
                return JsonResponse({'success': True, 'message': 'Product added to cart'})
        else:
            return JsonResponse({'success': False})


def update_cart_item(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        quantity = request.POST.get('quantity')
        try:
            cart_item = CartOrder.objects.get(cid=id)
            product = cart_item.product
            stock_count = product.stock_count
            if stock_count is not None and int(quantity) > int(stock_count):
                return JsonResponse({'error': 'Not enough stock.'})
            cart_item.quantity = quantity
            cart_item.save()
            total_price = cart_item.get_price()
            subtotal = sum(item.get_price() for item in CartOrder.objects.filter(user=request.user.id))
            tax_rate = Decimal('0.05')  # 5% tax rate
            discount = 0  # example discount value
            tax = subtotal * tax_rate
            total = subtotal + tax - discount

            try:
                cart_order_item = CartOrderItems.objects.get(user=request.user.id)
                cart_order_item.grand_total = subtotal
                cart_order_item.tax = tax
                cart_order_item.total_price = total
                cart_order_item.save()
            except CartOrderItems.DoesNotExist:
                print('CartOrderItems.DoesNotExist')
                # ValueError: Cannot assign "1": "CartOrderItems.user" must be a "User" instance.
                CartOrderItems.objects.create(user=request.user, grand_total=subtotal, tax=tax, total_price=total)
            return JsonResponse({'success': 'Cart item updated.',
                                 'total_price': total_price,
                                 'subtotal': str(subtotal),
                                 'discount': str(discount),
                                 'tax': str(tax),
                                 'total': str(total)})
        except CartOrder.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'})


class DeleteCartItemView(LoginRequiredMixin, View):
    def post(self, request):
        cid = request.POST.get('cid')
        cart_item = get_object_or_404(CartOrder, cid=cid, user=request.user)
        print(cart_item)
        cart_item.delete()
        return redirect('car-cart')


# class CheckOutCartItemView(LoginRequiredMixin, View):
#     def get(self, request):
#         cart_order_item = CartOrderItems.objects.get(user=request.user.id)
#         context = {
#             'heading': "Checkout",
#             'pageview': "Car Management",
#             'cart_order_item': cart_order_item
#         }
#         return render(request, 'car/car-checkout.html', context)


class ProductsView(LoginRequiredMixin, View):
    def get(self, request):
        # Get all products ordered by title
        products = Products.objects.order_by('-title')
        # Get all suppliers ordered by name
        suppliers = Supplier.objects.order_by('-name')
        # Get the category from the request's GET parameters
        category = request.GET.get('category')
        if category:
            products = products.filter(category=category)  # Filter products by category if category is provided
        supplier_id = request.GET.get('supplier')
        if supplier_id:
            products = products.filter(supplier=supplier_id)  # Filter products by supplier if supplier is provided

        search_query = request.GET.get('search')
        # SEARCH by title
        if search_query:
            products = products.filter(
                title__icontains=search_query)  # Filter products by title if search query is provided
        # Create a Paginator object with 6 items per page
        paginator = Paginator(products, 9)
        # Get the current page number from the request's GET parameters
        page_number = request.GET.get('page')
        # Get the Page object for the current page
        try:
            paginated_products = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        context = {
            'suppliers': suppliers,
            'products': paginated_products,
            'heading': "Products",
            'pageview': "Car Management"}

        return render(request, 'car/car-products.html', context)


class ProductDetailView(LoginRequiredMixin, View):
    def get(self, request, pid):
        product = Products.objects.get(pid=pid)
        # products = Products.objects.filter(category=product.category).exclude(pid=pid)
        greeting = {}
        greeting['heading'] = "Product Detail"
        greeting['pageview'] = "Car Management"
        greeting['product'] = product
        return render(request, 'car/car-productdetail.html', greeting)
        context = {
            'product': product,
            'heading': "Product Detail",
            'pageview': "Car Management"
        }
        return render(request, 'car/car-productdetail.html', context)


class OrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.order_by('-id')
        context = {
            'heading': "Orders",
            'pageview': "Car Management",
            'orders': orders

        }

        return render(request, 'car/car-orders.html', context)


#
#
# class CustomersView(LoginRequiredMixin, View):
#     def get(self, request):
#         form = CustomersForm()
#         customers_record = Customer.objects.all()
#         p = Paginator(customers_record, 8)
#         page = request.GET.get('page')
#         if p == None:
#             page = int(1)
#         page_obj = p.get_page(page)
#         greeting = {}
#         greeting['heading'] = "Customers"
#         greeting['pageview'] = "Ecommerce"
#         greeting['page_obj'] = page_obj
#         greeting['form'] = form
#         greeting['form1'] = EditCustomersForm()
#         return render(request, 'car/car-customers.html', greeting)
#
#     def post(self, request):
#         if request.method == "POST":
#             if "addcustomer" in request.POST:
#                 form = CustomersForm(request.POST)
#                 form.save()
#                 page_number = request.POST['page_number']
#                 return redirect("/car/customers" + "?page=" + str(page_number))
#             if "editcustomer" in request.POST:
#                 id = request.POST['id']
#                 username = request.POST['username']
#                 email = request.POST['email']
#                 phone = request.POST['phone']
#                 rating = request.POST['rating']
#                 wallet_balance = request.POST['wallet_balance']
#                 address = request.POST['address']
#                 page_number = request.POST['page_number']
#
#                 user = Customers.objects.filter(id=id).update(username=username, email=email, phone=phone,
#                                                               rating=rating, wallet_balance=wallet_balance,
#                                                               address=address)
#                 return redirect("/car/customers" + "?page=" + str(page_number))
#             if "deleteCustomer" in request.POST:
#                 id = request.POST['id']
#                 obj = Customers.objects.filter(id=id).first()
#                 obj.delete()
#                 return HttpResponse()
#
#
# Edit Customer
class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartOrder.objects.filter(user=request.user.id)
        subtotal = sum(item.get_price() for item in cart_items)
        tax_rate = Decimal('0.05')  # 5% tax rate
        discount = 0  # example discount value
        tax = subtotal * tax_rate
        total = subtotal + tax - discount
        context = {
            'heading': "Cart",
            'pageview': "Car Management",
            'cart_items': cart_items,
            'subtotal': subtotal,
            'tax': tax,
            'discount': discount,
            'total': total,
        }
        return render(request, 'car/car-cart.html', context)

    # def post(self, request):
    #     if request.method == "POST":
    #         if "deleteCartItem" in request.POST:
    #             id = request.POST['id']
    #             obj = CartOrder.objects.filter(id=id).first()
    #             obj.delete()
    #             return HttpResponse()


class CheckOutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_order_item = CartOrderItems.objects.get(user=request.user.id)
        cart_item = CartOrder.objects.filter(user=request.user.id)
        # print(cart_order_item.cart_order.all())
        context = {
            'heading': "Checkout",
            'pageview': "Car Management",
            'cart_order_item': cart_order_item,
            'cart_item': cart_item,
            'subtotal': cart_order_item.grand_total,
            'tax': cart_order_item.tax,
            'total': cart_order_item.total_price,
        }
        return render(request, 'car/car-checkout.html', context)

    def post(self, request):
        name = request.POST.get('billing-name')
        email = request.POST.get('billing-email-address')
        contact = request.POST.get('billing-phone')
        address = request.POST.get('billing-address')
        city = request.POST.get('city')
        district = request.POST.get('district')
        ward = request.POST.get('ward')

        cart_items = CartOrder.objects.filter(user=request.user.id)
        for items in cart_items:
            statistics_prod = StatisticsProducts.objects.filter(product=items.product).first()
            if statistics_prod:
                statistics_prod.quantity_sold = statistics_prod.quantity_sold + items.quantity
                statistics_prod.total_revenue = statistics_prod.total_revenue + items.get_price()
                statistics_prod.save()
            else:
                statistics_prod = StatisticsProducts(product=items.product, quantity_sold=items.quantity,
                                                     total_revenue=items.get_price())
                statistics_prod.save()

        cart_order_item = CartOrderItems.objects.get(user=request.user.id)
        customer = Customer.objects.filter(email=email).first()
        if customer is None:
            customer = Customer(email=email, name=name, contact=contact, address=address, city=city,
                                district=district, ward=ward)
            customer.save()
            # customer, created = Customer.objects.get_or_create(email=email, defaults={'name': name, 'contact':
            # contact, 'address': address, 'city': city, 'district': district, 'ward': ward})

        order = Order(user=request.user, customer=customer)
        order.grand_total = cart_order_item.grand_total
        order.tax = cart_order_item.tax
        order.total_price = cart_order_item.total_price
        order.save()
        return redirect('/car/invoice/' + str(order.oid))


class ShopsView(LoginRequiredMixin, View):
    def get(self, request):
        greeting = {}
        greeting['heading'] = "Shops"
        greeting['pageview'] = "Car Management"
        return render(request, 'car/car-shops.html', greeting)


class ProductListView(LoginRequiredMixin, View):
    def get(self, request):
        products = Products.objects.all()
        context = {
            'heading': "Product List",
            'pageview': "Car Management",
            'products': products,
        }
        return render(request, 'car/car-productlist.html', context)


class AddProductView(LoginRequiredMixin, View):
    def get(self, request):
        suppliers = Supplier.objects.all()
        # print(suppliers)

        context = {
            'heading': "Add Product",
            'pageview': "Car Management",
            'suppliers': suppliers,
        }
        return render(request, 'car/car-addproduct.html', context)

    def post(self, request):
        name = request.POST.get('productname')
        supplier = request.POST.get('supplier')
        supplier = Supplier.objects.filter(id=supplier).first()
        image = request.FILES.get('image')
        category = request.POST.get('category')
        cost = request.POST.get('cost')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')

        product = Products(title=name, supplier=supplier, category=category,
                           cost_price=cost, price=price, stock_count=quantity,
                           description=description)
        if image:
            file_path = os.path.join('products', image.name)
            image_name = default_storage.save(file_path, image)
            product.image = image_name
        product.save()

        return redirect('/car/productlist')


class EditProductView(LoginRequiredMixin, View):
    def get(self, request, pid):
        product = Products.objects.filter(pid=pid).first()
        context = {
            'heading': "Edit Product",
            'pageview': "Car Management",
            'product': product,
        }
        return render(request, 'car/car-editproduct.html', context)

    def post(self, request, pid):
        product = Products.objects.filter(pid=pid).first()
        title = request.POST.get('title', product.title)
        category = request.POST.get('category', product.category)
        supplier = request.POST.get('supplier', product.supplier.id)
        cost = request.POST.get('cost', product.cost_price)
        price = request.POST.get('price', product.price)
        quantity = request.POST.get('quantity', product.quantity)
        description = request.POST.get('description', product.description)

        product.title = title
        # product.supplier = supplier
        # product.category = category
        product.cost_price = cost
        product.price = price
        product.quantity = quantity
        product.description = description
        product.save()
        return redirect('/car/productlist')


class InvoiceView(LoginRequiredMixin, View):
    def get(self, request, oid):
        order = Order.objects.filter(oid=oid).first()
        customer = Customer.objects.filter(id=order.customer.id).first()
        cart_item = CartOrder.objects.filter(user=request.user.id)
        cart_order_item = CartOrderItems.objects.get(user=request.user.id)
        context = {
            'heading': "Invoice",
            'pageview': "Car Management",
            'order': order,
            'customer': customer,
            'cart_item': cart_item,
            'cart_order_item': cart_order_item,
        }
        return render(request, 'car/car-invoicedetail.html', context)

    def post(self, request, oid):
        try:
            order = Order.objects.filter(oid=oid).first()
            customer = Customer.objects.filter(id=order.customer.id).first()
            cart_item = CartOrder.objects.filter(user=request.user.id)
            cart_order_item = CartOrderItems.objects.get(user=request.user.id)
            # Decrease product stock count
            for prod in cart_item:
                product = Products.objects.filter(id=prod.product.id).first()
                product.stock_count = int(product.stock_count) - int(prod.quantity)
                product.save()
            # take image of product
            prod_images = [item.product.image.url for item in cart_item]
            # create invoice
            invoice = Invoice(order=order,
                              customer=customer,
                              user=request.user)
            invoice_prod = {
                index + 1: [item.product.title, '', float(item.product.price), item.quantity, int(item.get_price())] for
                index, item in
                enumerate(cart_item)}
            for index, prod_image in enumerate(prod_images):
                if index == len(invoice_prod):
                    break
                # add prod_image to invoice_prod
                invoice_prod[index + 1][1] = prod_image
            invoice.prod = invoice_prod
            invoice.save()
            cart_item.delete()
            cart_order_item.delete()
            return redirect('/car/orders')
        except Exception as e:
            print(f"Error encoding invoice as JSON: {e}")
            return HttpResponseServerError("Could not complete request")


class InvoiceListView(LoginRequiredMixin, View):
    def get(self, request):
        invoices = Invoice.objects.order_by('-id')
        context = {
            'heading': "Invoices",
            'pageview': "Car Management",
            'invoices': invoices,
        }
        return render(request, 'car/car-invoicelist.html', context)
