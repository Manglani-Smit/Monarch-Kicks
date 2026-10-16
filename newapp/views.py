from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import requests
import random
import stripe
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

YOUR_DOMAIN = 'http://127.0.0.1:8000'
stripe.api_key = settings.STRIPE_SECRET_KEY
def index(request):
    products = Product.objects.all()
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype == "buyer":
            return render(request, 'index.html',{'products':products})
        else:
            seller = User.objects.get(email=request.session['email'])
            products = Product.objects.filter(seller=seller)
            return render(request, 'seller-index.html',{'products':products})
    except:
        return render(request, 'index.html',{'products':products})

def login(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['fname'] = user.fname
                request.session['profile_picture'] = user.profile_picture.url
                if user.usertype == "buyer":
                    products = Product.objects.all()
                    return render(request, 'index.html',{'products':products})
                else:
                    seller = User.objects.get(email=request.session['email'])
                    products = Product.objects.filter(seller=seller)
                    return render(request, 'seller-index.html', {'products': products})
            else:
                msg = "Incorrect Password"
                return render(request, 'login.html', {'msg': msg})
        except:
            msg = "Email does not exist"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
            msg = "Email already exists"
            return render(request, 'signup.html', {'msg': msg})
        except:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES.get('profile_picture'),
                    usertype=request.POST['usertype'],
                )
                msg = "Signup successful"
                return render(request, 'login.html', {'msg': msg})
            else:
                msg = "Passwords did not match"
                return render(request, 'signup.html', {'msg': msg})
    else:
        return render(request, 'signup.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        msg = "Logout successful"
        return render(request, 'login.html', {'msg': msg})
    except:
        msg = "Logout successful"
        return render(request, 'login.html', {'msg': msg})

def change_password(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        if user.password == request.POST['old_password']:
            if request.POST['new_password'] == request.POST['cnew_password']:
                if user.password != request.POST['new_password']:
                    user.password = request.POST['new_password']
                    user.save()
                    del request.session['email']
                    del request.session['fname']
                    del request.session['profile_picture']
                    msg = "Password changed successful"
                    return render(request, 'login.html', {'msg': msg})
                else:
                    msg = "Password Can't be Old Password"
                    if user.usertype == "buyer":
                        return render(request, 'change-password.html', {'msg': msg})
                    else:
                        return render(request, 'seller-change-password.html', {'msg': msg})
            else:
                msg = "New Password And Confirm Password Doesn't Match"
                if user.usertype == "buyer":
                    return render(request, 'change-password.html', {'msg': msg})
                else:
                    return render(request, 'seller-change-password.html', {'msg': msg})
        else:
            msg = "Old Password Does not Match"
            if user.usertype == "buyer":
                return render(request, 'change-password.html', {'msg': msg})
            else:
                return render(request, 'seller-change-password.html', {'msg': msg})
    else:
        if user.usertype == "buyer":
            return render(request, 'change-password.html')
        else:
            return render(request, "seller-change-password.html")

def profile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.mobile = request.POST['mobile']
        user.address = request.POST['address']
        try:
            user.profile_picture = request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture'] = user.profile_picture.url
        msg = "Profile Updated Successfully"
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'msg': msg, 'user': user})
        else:
            return render(request, 'seller-profile.html', {'msg': msg, 'user': user})
    else:
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'user': user})
        else:
            return render(request, 'seller-profile.html', {'user': user})

def forgot_password(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(mobile=request.POST['mobile'])
            otp = random.randint(1000, 9999)
            mobile = str(user.mobile)
            message = "Hello, Your OTP for Forgot Password is " + str(otp)
            url = "https://www.fast2sms.com/dev/bulkV2"
            querystring = {
                "message": message,
                "route": "q",
                "numbers": mobile,
                "sms_details": "1"
            }
            headers = {
                "accept": "application/json",
                "Authorization": "7Xhtrh9eWXBqVIUWzDs4Pgn6WuRFYJuJjlX1aZi6t9y3xEEPutANp1xHUMkx"
            }
            response = requests.get(url, headers=headers, params=querystring)
            print(response.text)
            request.session['mobile'] = user.mobile
            request.session['otp'] = otp
            return render(request, "otp.html")
        except:
            msg = "Mobile Number Not Registered"
            return render(request, "forgot-password.html", {'msg': msg})
    else:
        return render(request, "forgot-password.html")

def verify_otp(request):
    otp1 = int(request.session['otp'])
    otp2 = int(request.POST['otp'])
    if otp1 == otp2:
        del request.session['otp']
        msg = "Set your new password"
        return render(request, 'new-password.html', {'msg': msg})
    else:
        msg = "Invalid OTP"
        return render(request, 'otp.html', {'msg': msg})

def new_password(request):
    if request.POST['new_password'] == request.POST['cnew_password']:
        user = User.objects.get(mobile=request.session['mobile'])
        user.password = request.POST['new_password']
        user.save()
        del request.session['mobile']
        msg = "Password Updated Successfully"
        return render(request, 'login.html', {'msg': msg})
    else:
        msg = "New Password & Confirm Password not match"
        return render(request, 'new-password.html', {'msg': msg})


def seller_add_product(request):
    if request.method == "POST":
        seller = User.objects.get(email=request.session['email'])
        Product.objects.create(
            seller=seller,
            product_category=request.POST['product_category'],
            product_name=request.POST['product_name'],
            product_price=request.POST['product_price'],
            product_desc=request.POST['product_desc'],
            product_image=request.FILES['product_image'],
        )
        msg="Product Added Successfully"
        return render(request, 'seller-add-product.html',{'msg': msg})
    else:
        return render(request, 'seller-add-product.html')

def seller_view_product(request,cat):
    seller=User.objects.get(email=request.session['email'])
    products=Product()
    if cat=='all':
        products = Product.objects.filter(seller=seller)
    elif cat=='Adidas':
        products = Product.objects.filter(seller=seller,product_category='Adidas')
    elif cat=='Nike':
        products = Product.objects.filter(seller=seller,product_category='Nike')
    elif cat=='Woodland':
        products = Product.objects.filter(seller=seller,product_category='Woodland')
    elif cat=='Clarks Formal':
        products = Product.objects.filter(seller=seller,product_category='Clarks Formal')
    return render(request, 'seller-view-product.html',{'products':products})

def seller_edit_product(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method == "POST":
        product.product_category = request.POST['product_category']
        product.product_name = request.POST['product_name']
        product.product_price = request.POST['product_price']
        product.product_desc = request.POST['product_desc']
        try:
            product.product_image = request.FILES['product_image']
        except:
            pass
        product.save()
        msg="Product Updated Successfully"
        return render(request,'seller-edit-product.html',{'msg': msg,'product':product})
    else:
        return render(request, 'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    msg="Product Deleted Successfully"
    return render(request,'seller-view-product.html',{'products':products,'msg':msg})

def shop(request,cat):
    products = Product()
    if cat == 'all':
        products = Product.objects.all()
    elif cat == 'Adidas':
        products = Product.objects.filter(product_category='Adidas')
    elif cat == 'Nike':
        products = Product.objects.filter(product_category='Nike')
    elif cat == 'Woodland':
        products = Product.objects.filter(product_category='Woodland')
    elif cat == 'Clarks Formal':
        products = Product.objects.filter(product_category='Clarks Formal')
    return render(request, 'shop.html', {'products': products})

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user, product=product)
        cart_flag = True
    except:
        pass
    return render(request,'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,product=product)
    return redirect('wishlist')

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists = Wishlist.objects.filter(user=user)
    return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    wishlists = Wishlist.objects.get(user=user,product=product)
    wishlists.delete()
    return redirect('wishlist')

def add_to_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False,
        )
    return redirect('cart')

def cart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts = Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price = net_price+i.total_price
    return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
    product = Product.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])
    cart = Cart.objects.get(user=user,product=product)
    cart.delete()
    return redirect('cart')

def change_qty(request,pk):
    cart = Cart.objects.get(pk=pk)
    product_qty = int(request.POST['product_qty'])
    cart.total_price=cart.product_price*product_qty
    cart.product_qty=product_qty
    cart.save()
    return redirect('cart')


@csrf_exempt
def create_checkout_session(request):
    domain_url = request.build_absolute_uri('/')[:-1]
    amount = int(json.load(request)['post_data'])
    final_amount = amount * 100
    user = User.objects.get(email=request.session['email'])
    user_name = f"{user.fname} {user.lname}"
    user_address = f"{user.address}"
    user_mobile = f"{user.mobile}"
    session = stripe.checkout.Session.create(

        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': final_amount,
                'product_data': {
                    'name': 'Checkout Session Data',
                    'description': f'''Customer:{user_name},\n\n
                Address:{user_address},\n
                Mobile:{user_mobile}''',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url = domain_url + f'/confirmation/?user_email={user.email}',
        cancel_url=domain_url + '/cancel/',
        customer_email=user.email,
        shipping_address_collection={
            'allowed_countries': ['IN'],
        }
    )
    return JsonResponse({'id': session.id})


def confirmation(request):
    user_email = request.GET.get('user_email') or request.session.get('email')

    user = None
    if user_email:
        user = User.objects.filter(email=user_email).first()
        request.session['email'] = user_email

    carts = []
    total_amount = 0

    if user:
        # Pehle unpaid carts uthao
        unpaid_carts = list(Cart.objects.filter(user=user, payment_status=False).select_related('product'))

        if unpaid_carts:
            carts = unpaid_carts
            for i in carts:
                total_amount += i.total_price
                i.payment_status = True
                i.save()
        else:
            # Agar page reload hua hai toh recent paid carts le aao
            carts = list(
                Cart.objects.filter(user=user, payment_status=True).select_related('product').order_by('-id')[:5])
            total_amount = sum(i.total_price for i in carts)

    # Session cart clear
    request.session['cart_count'] = 0
    if 'cart' in request.session:
        del request.session['cart']
    request.session.modified = True

    order_id = random.randint(10000, 99999)

    # Email Dispatch
    if user:
        try:
            email_context = {
                'user': user,
                'carts': carts,
                'total_amount': total_amount,
                'order_id': order_id,
            }
            subject = f"Order Placed! Monarch Kicks (#MK-{order_id})"

            try:
                html_message = render_to_string('email_confirmation.html', email_context)
                plain_message = strip_tags(html_message)
            except Exception:
                html_message = None
                plain_message = f"Hello {user.fname}, your order #{order_id} has been placed successfully. Total: ₹{total_amount}"

            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
            to_email = [user.email]

            if html_message:
                email = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=False)
            else:
                from django.core.mail import send_mail
                send_mail(subject, plain_message, from_email, to_email, fail_silently=False)
        except Exception as e:
            print("Mail Error on Render:", e)

    return render(request, 'confirmation.html', {
        'user': user,
        'carts': carts,
        'total_amount': total_amount,
        'order_id': order_id,
    })

def cancel(request):
    return render(request, 'cancel.html')


def myorder(request):
    user = User.objects.get(email=request.session['email'])
    carts = Cart.objects.filter(user=user, payment_status=True).select_related('product')
    return render(request, 'myorder.html', {'carts': carts})