from datetime import datetime, timedelta
import re
import json
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AddressForm, ProductForm, OrderAddressForm, QuestionForm
from engine.models import Product, Order, Address, OrderProduct, Visit, Support
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from telegram import Telegram


def profile_redirect(request):
    username = request.user.username
    return redirect(reverse('profile', kwargs={'username': username}))


class Index(View):
    def get(self, request):
        form = QuestionForm()
        return render(request, 'index.html', dict(form=form))

    def post(self, request):
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.save()
            messages.add_message(request, messages.SUCCESS, "Thank you for the question")
            return redirect('index')

        return redirect('index')


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('/')


class Login(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, "User  does not exist")
                return redirect('login')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if next_url:
                return HttpResponseRedirect(next_url)
            return redirect(reverse('profile', kwargs={'username': user.username}))
        else:
            messages.add_message(request, messages.ERROR, "Invalid Email or Password")
            if next_url:
                login_url = f"{reverse('login')}?{urlencode({'next': next_url})}"
                return redirect(login_url)
            else:
                return redirect('login')

    def get(self, request):
        return render(request, 'registration/login.html')


class Register(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        next_url = request.POST.get('next', '')

        if form.is_valid():
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            try:
                Telegram.new_registration(email)
            except Exception as e:
                print(f"Error - {e}")

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if next_url:
                login_url = f"{reverse('login')}?{urlencode({'next': next_url})}"
                return redirect(login_url)
            else:
                return redirect('login')
        else:
            return render(request, 'registration/register.html', dict(form=form, next=next_url))


class RedirectToProfile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        next_url = request.GET.get('next', '')
        if next_url:
            login_url = f"{reverse('login')}?{urlencode({'next': next_url})}"
            return redirect(login_url)
        return redirect(reverse('profile', kwargs={'username': username}))


class Fans(View):
    def get(self, request):
        return render(request, '')


class Agency(View):
    def get(self, request):
        return render(request, '')


class Profile(View):
    def get(self, request, username, *args, **kwargs):
        cookie_value = request.COOKIES.get('confirmed_age', 'false')
        try:
            user = User.objects.get(username=username)
            address, created = Address.objects.get_or_create(user=user)
            products = Product.objects.filter(user=user)

            context = dict(username=username, products=products, cookie_value=cookie_value)
            response = render(request, 'profile.html', context)

            if not address.confirmed_age:
                if request.COOKIES.get('confirmed_age') == 'true':
                    address.confirmed_age = True
                    address.save()
                elif cookie_value == 'false':
                    response = render(request, 'profile.html', context)
            else:
                context['cookie_value'] = 'true'
                response = render(request, 'profile.html', context)
                response.set_cookie('confirmed_age', 'true')

            return response

        except:
            return profile_redirect(request)


class AddProducts(LoginRequiredMixin, View):
    def get(self, request):
        form = ProductForm
        return render(request, 'add_product.html', dict(form=form))

    def post(self, request):
        form = ProductForm(request.POST, request.FILES, user_id=request.user.id)
        # Max Size File
        max_file_size = 50 * 1024 * 1024  # 50 MB
        file_errors = []

        for file_key in form.files:
            file = request.FILES.get(file_key)
            if file and file.size > max_file_size:
                file_errors.append((file_key, file.name))

        if file_errors:
            for file_key, file_name in file_errors:
                messages.add_message(
                    request, messages.ERROR, f'File "{file_name}" should not exceed 50 MB.'
                )
            return render(request, 'add_product.html', {'form': form})

        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return profile_redirect(request)

        return render(request, 'add_product.html', {'form': form})


class DeleteProduct(LoginRequiredMixin, View):
    def get(self, request, product_id):
        Product.objects.get(id=product_id).delete()
        messages.add_message(request, messages.SUCCESS, "Delete Success")
        return redirect('profile', request.user.username)


class EditProduct(LoginRequiredMixin, View):
    def get(self, request, product_uuid):
        product = Product.objects.get(uuid=product_uuid)
        form = ProductForm(instance=product, user_id=request.user.id)
        return render(request, 'edit_product.html', dict(form=form, product=product))

    def post(self, request, product_uuid):
        product = Product.objects.get(uuid=product_uuid)
        form = ProductForm(request.POST, instance=product, user_id=request.user.id)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Updated success')
            return redirect('profile', request.user.username)


class ProfileSettings(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'profile/page.html')


class ProfileAccount(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'profile/account.html')


class ProfileAddress(View):
    def get(self, request):
        user = request.user
        try:
            address = Address.objects.get(user=user)
            initial_data = {
                'location': address.location,
                'first_name': address.first_name,
                'last_name': address.last_name,
                'address_line_1': address.address_line_1,
                'address_line_2': address.address_line_2,
                'country': address.country,
                'city': address.city,
                'state': address.state,
                'zipcode': address.zipcode,
                'phone_number': address.phone_number,
                'description': address.description,
            }
            form = AddressForm(initial=initial_data)
        except Address.DoesNotExist:
            form = AddressForm()
        return render(request, 'profile/address.html', dict(form=form))

    def post(self, request):
        user = request.user
        form = AddressForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            addess, created = Address.objects.get_or_create(user=user, defaults={
                'location': data.get('location'),
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'address_line_1': data.get('address_line_1'),
                'address_line_2': data.get('address_line_2'),
                'country': data.get('country'),
                'city': data.get('city'),
                'state': data.get('state'),
                'zipcode': data.get('zipcode'),
                'phone_number': data.get('phone_number'),
                'description': data.get('description'),
            })

            if not created:
                addess.location = data.get('location')
                addess.first_name = data.get('first_name')
                addess.last_name = data.get('last_name')
                addess.address_line_1 = data.get('address_line_1')
                addess.address_line_2 = data.get('address_line_2')
                addess.country = data.get('country')
                addess.city = data.get('city')
                addess.state = data.get('state')
                addess.zipcode = data.get('zipcode')
                addess.phone_number = data.get('phone_number')
                addess.description = data.get('description')
                addess.save()
            messages.add_message(request, messages.SUCCESS, "Address successfully updated")
            return render(request, 'profile/address.html', {'form': form})
        else:
            return render(request, 'profile/address.html', {'form': form})


class ProfileWithdraw(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'profile/withdraw.html')


# *** CART *** #
@method_decorator(csrf_exempt, name='dispatch')
class AddToCart(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        user = request.user
        order = Order.objects.filter(user=user, status=Order.CREATED).last()
        if not order:
            order = Order.objects.create(user=user, status=Order.CREATED)

        product = Product.objects.get(id=product_id)
        order_prod, created = OrderProduct.objects.get_or_create(order=order, product=product)
        message = ''
        if not created:
            order_prod.count += 1
            order_prod.save()
            message = 'product_count'
        if created:
            message = 'new_product'
        order.update_costs()
        order.save()

        try:
            Telegram.add_to_cart(product)
        except Exception as e:
            print(f"Error - {e}")

        return JsonResponse({'message': message, 'order_uuid': order.uuid, 'available_product': product.count})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFromCart(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        user = request.user
        product = Product.objects.get(id=product_id)
        order = Order.objects.filter(user=user).last()
        order.update_costs()
        order.products.remove(product)
        return JsonResponse({'success': True})


class ProductCart(LoginRequiredMixin, View):
    def get(self, request):
        order = Order.objects.filter(user=request.user, status=Order.CREATED).last()
        if order:
            serialized = [q.serialize(order=order) for q in order.products.all()]
        else:
            serialized = []
        response = json.dumps(serialized)

        return HttpResponse(response, content_type='application/json')


@method_decorator(csrf_exempt, name='dispatch')
class UpdateProductCart(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        product_id = data.get('product_id')
        count = data.get('count')
        try:
            product = Product.objects.get(id=product_id)
            order, created = Order.objects.get_or_create(user=user, status=Order.CREATED)
            order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)
            order_product.count = count
            order_product.save()
            order.update_costs()
            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)


def get_ip(request):
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        ip = x_real_ip
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
    return ip


class PageProduct(View):
    def get(self, request, username, product_uuid):
        try:
            product = Product.objects.get(uuid=product_uuid)
            user_product = product.user
            Visit.objects.create(product=product, ip=get_ip(request), created_at=timezone.now())
        except Product.DoesNotExist:
            return redirect('login')
        return render(request, 'product.html', dict(product=product, user_product=user_product))


class AllOrders(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return render(request, 'orders.html', dict(orders=orders))


class ProcessOrder(LoginRequiredMixin, View):
    def get(self, request, order_uuid):
        user = request.user
        try:
            order = Order.objects.get(uuid=order_uuid, status=Order.CREATED)
            if order.products.exists():
                # products = order.products.all()
                products = []
                for order_prod in OrderProduct.objects.filter(order=order):
                    product = order_prod.product
                    product.count = order_prod.count
                    products.append(product)
                address, created = Address.objects.get_or_create(user=user)
                initial_data = {}

                if created:
                    form = OrderAddressForm(initial=initial_data)
                else:
                    initial_data = {
                        'location': address.location,
                        'first_name': address.first_name,
                        'last_name': address.last_name,
                        'address_line_1': address.address_line_1,
                        'address_line_2': address.address_line_2,
                        'country': address.country,
                        'city': address.city,
                        'state': address.state,
                        'zipcode': address.zipcode,
                        'phone_number': address.phone_number,
                        'description': address.description,
                    }
                    form = OrderAddressForm(initial=initial_data)
            else:
                return redirect('profile', user.username)
        except:
            return redirect('profile', user.username)
        try:
            Telegram.new_buy(order)
        except Exception as e:
            print(f"Error - {e}")

        return render(request, 'order.html', dict(
            order=order, products=products, form=form))


class CheckoutOrder(LoginRequiredMixin, View):
    def get(self, request, order_uuid):

        try:
            order = Order.objects.get(uuid=order_uuid)
            if order.status != order.PROCESSING:
                return redirect('all-orders')
            return render(request, 'checkout.html', dict(order=order))
        except Order.DoesNotExist:
            return profile_redirect(request)

    def post(self, request, order_uuid):
        try:
            order = Order.objects.filter(uuid=order_uuid).exclude(status=Order.PAID).first()
            form = OrderAddressForm(request.POST, instance=order)
            address = Address.objects.get(user=request.user)
            form_address = AddressForm(request.POST, instance=address)
            if form.is_valid():
                form.save()
                if not address.location:
                    form_address.save()
                order.status = order.PROCESSING
                order.save()
                try:
                    Telegram.new_checkout(order)
                except Exception as e:
                    print(f"Error - {e}")

                return render(request, 'checkout.html', dict(order=order))
            return messages.add_message(request, messages.ERROR, 'Invalid form')
        except:
            return redirect('profile', request.user.username)


class PaidOrder(LoginRequiredMixin, View):
    def get(self, request, order_uuid):
        try:
            order = Order.objects.get(uuid=order_uuid, status=Order.PROCESSING)
            order_products = OrderProduct.objects.filter(order=order)
            quantity_products = []
            for order_product in order_products:
                if order_product.count > order_product.product.count:
                    quantity_products.append(
                        {'name': order_product.product.name,
                         'required_count': order_product.count,
                         'available_count': order_product.product.count
                         })

            if quantity_products:

                for product in quantity_products:
                    messages.add_message(request, messages.ERROR,
                                         f"Product: {product['name']} - Requested: {product['required_count']}, Available: {product['available_count']}")
                messages.add_message(request, messages.ERROR, 'Insufficient quantity of the following products:')
                return render(request, 'checkout.html', {'order': order})

            for order_product in order_products:
                product = order_product.product
                product.count -= order_product.count
                product.save()

            order.status = Order.PAID
            order.save()
            try:
                Telegram.new_paid(order)
            except Exception as e:
                print(f"Error - {e}")

            messages.add_message(request, messages.SUCCESS, 'Track status in your orders')
            # return redirect('profile', order.user.username)
            return redirect('all-orders')
        except Order.DoesNotExist:
            return profile_redirect(request)


class SearchUsers(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('query', '')
        users = User.objects.filter(username__icontains=query).exclude(is_staff=True)[:10]
        result = [{'username': user.username} for user in users]
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class SupportMessageUser(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        time_now = datetime.now()
        message_content = data.get('message', '')
        if message_content:
            message_entry = {
                'from': user.username,
                'message': message_content,
                'date': time_now.strftime('%d.%m.%Y %H:%M:%S')}

            try:
                support = Support.objects.filter(user=user).last()
                if support:
                    support.message.append(message_entry)
                else:
                    nwe_time = time_now + timedelta(seconds=3)
                    suport_msg = {
                        'from': 'support',
                        'message': 'Thank you for your question. A support agent will respond to you shortly.',
                        'date': nwe_time.strftime('%d.%m.%Y %H:%M:%S')
                    }

                    support = Support(user=user, message=[message_entry, suport_msg])
                support.save()
                try:
                    Telegram.support(message_entry)
                except Exception as e:
                    print(f"Error - {e}")

                return JsonResponse({'success': True})
            except Support.DoesNotExist:
                return JsonResponse({'success': False})

        return JsonResponse({'success': False})


class SupportMessageAdmin(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        support = Support.objects.filter(user=user).last()
        if support:
            if support.message:
                sorted_messages = sorted(
                    support.message, key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y %H:%M:%S')
                )
            else:
                sorted_messages = []
        else:
            sorted_messages = []
        return JsonResponse({'message': sorted_messages})


@method_decorator(csrf_exempt, name='dispatch')
class SendTelegramShare(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        product_id = data.get('product_id', 0)
        if product_id:
            product = Product.objects.get(id=product_id)
            try:
                Telegram.new_share(product)
                return JsonResponse({'success': True})
            except Exception as e:
                print(f"Error - {e}")
                return JsonResponse({'success': False})

        return JsonResponse({'success': False})
