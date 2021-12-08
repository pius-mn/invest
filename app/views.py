"""
Definition of views.
"""

from datetime import datetime
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth import login, authenticate
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string
from .forms import SignUpForm, depositForm
from .tokens import account_activation_token
from .models import Profile
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from django.http import JsonResponse
from .env import MpesaAccessToken, LipanaMpesaPpassword
from .models import MpesaDeposits
from django.views.decorators.csrf import csrf_exempt


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    try:
        profile = Profile.objects.get(user=request.user)
        my_recs = profile.get_recommened_profiles()[0]
        for i in my_recs:
            update = Profile.objects.get(user=i.user)
            if update.signup_confirmation == False and update.amount >= 100:
                update.signup_confirmation = True
                update.save()
                profile.amount += 50
                profile.save()
        mycode = profile.get_recommened_profiles()[1]
        my_balance = profile.get_recommened_profiles()[2]
        available_balance = profile.get_recommened_profiles()[3]
        withDrawable_balance = profile.get_recommened_profiles()[4]
        acc_status = True
        if(available_balance <= 0):
            available_balance = 0.00
            acc_status = False
        if(withDrawable_balance <= 0):
            withDrawable_balance = 0.00
        return render(
            request,
            'app/index.html',
            {
                'title': 'Home Page',
                'year': datetime.now().year,
                'my_recs': my_recs,
                'mycode': mycode,
                'my_balance': my_balance,
                'available_balance': available_balance,
                'referral': f'{SimpleLazyObject(lambda: get_current_site(request))}/signup/{mycode}',
                'withDrawable_balance': withDrawable_balance,
                'status': acc_status,
            }
        )
    except Exception as e:
        print(f'error {e}')
        return render(request, 'app/404.html', {
            'title': 'Page Not Found'
        })


@login_required(login_url='login')
def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title': 'Contact',
            'message': 'Your contact page.',
            'year': datetime.now().year,
        }
    )


@login_required(login_url='login')
def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        }
    )

# Create your views here.


def activation_sent_view(request):
    return render(request, 'app/registration/activation_sent.html', {'title': 'Activation sent', })


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        # login(request, user)
        return redirect('login')
    else:
        return render(request, 'app/registration/activation_invalid.html', {'title': 'invalid link', })


def signup_view(request):
    profile_id = request.session.get('ref_profile')
    print('profile_id', profile_id)
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            if profile_id is not None:
                recommended_by_profile = Profile.objects.get(id=profile_id)
                instance = form.save()
                registered_user = User.objects.get(id=instance.id)
                registered_profile = Profile.objects.get(user=registered_user)
                registered_profile.recommended_by = recommended_by_profile.user
                registered_profile.save()
                registered_user.refresh_from_db()
                registered_user.profile.username = form.cleaned_data.get(
                    'username')

                registered_user.profile.email = form.cleaned_data.get('email')
                registered_user.is_active = False
                registered_user.save()
                current_site = get_current_site(request)
                subject = 'Please Activate Your Account'
                # load a template like get_template()
                # and calls its render() method immediately.
                message = render_to_string('app/registration/activation_request.html', {
                    'user': registered_user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(registered_user.pk)),
                    # method will generate a hash value with user related data
                    'token': account_activation_token.make_token(registered_user),
                })
                registered_user.email_user(subject, message)

            else:
                user = form.save()
                user.refresh_from_db()
                user.profile.username = form.cleaned_data.get('username')
                user.profile.email = form.cleaned_data.get('email')
                # user can't login until link confirmed
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Please Activate Your Account'
                # load a template like get_template()
                # and calls its render() method immediately.
                message = render_to_string('app/registration/activation_request.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    # method will generate a hash value with user related data
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)

            # username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=password)
            # login(request, user)
            return redirect('activation_sent')
            # return redirect('main-view')
    else:
        form = SignUpForm()
    return render(request, 'app/registration/signup.html', {'form': form,
                                                            'title': 'SignIn'})


@login_required(login_url='login')
def main_view(request, *args, **kwargs):
    code = str(kwargs.get('ref_code'))
    form = SignUpForm()
    try:
        profile = Profile.objects.get(code=code)
        request.session['ref_profile'] = profile.id
        print('printing id', profile.id)
    except:
        pass
    print(request.session.get_expiry_age())
    return redirect('signup-view')


@login_required(login_url='login')
def deposit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = depositForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            amount = form.cleaned_data['amount']
            user = User.objects.get(id=request.user.id)
            phone=f'254{user.first_name}'
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            request = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA":'254708374149',  # replace with your phone number to get stk push
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": '254708374149',  # replace with your phone number to get stk push
                "CallBackURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/confirmation",
                "AccountReference": "safcom",
                "TransactionDesc": "Testing stk push"
            }

            response = requests.post(api_url, json=request, headers=headers)
            
            
            return  HttpResponse(type(response))
    

    # if a GET (or any other method) we'll create a blank form
    else:
        form = depositForm()

    return render(request, 'app/depositForm.html', {'form': form, 'title': 'Deposit'})


@login_required(login_url='login')
def withdraw(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = depositForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            user = User.objects.get(id=request.user.id)
            return HttpResponse(user.first_name)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = depositForm()

    return render(request, 'app/depositForm.html', {'form': form, 'title': 'Withdraw'})
#########################################################################################


def getAccessToken(request):
    consumer_key = 'EmAmcJJDGPbUgm5g7xRhawDZkRE1z1Ur'
    consumer_secret = 'QbgkZnGRHYdnqQLT'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)

    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)
@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/confirmation",
               "ValidationURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(context)


@csrf_exempt
def confirmation(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaDeposits(

        phone_number=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'],
        reference=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
        transaction_date=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
        amount=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],

    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
