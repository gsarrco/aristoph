import csv
from datetime import datetime
from io import StringIO

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, AccountForm
from .models import User


def current_school_year():
    now = datetime.now()
    if now.month >= 9:
        year1 = now.year
        year2 = year1 + 1
    else:
        year2 = now.year
        year1 = year2 - 1
    return f'{year1}/{year2}'


def logout(request):
    auth_logout(request)
    return redirect('/')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            first_name = data['first_name']
            last_name = data['last_name']
            full_name = last_name + ' ' + first_name
            classe = data['classe']
            phone = data['phone']
            email = data['email']
            password = data['password']

            if User.objects.filter(email=email).count() > 0:
                messages.warning(request, 'Questa email è già associata ad un account esistente.')
                return redirect('account:register')

            try:
                user = User.objects.get(full_name__iexact=full_name, classe__iexact=classe, verified=True)
                if user.email:
                    messages.warning(request, 'Questo account è già presente. Contatta ... .')
                    return redirect('account:register')

                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.phone = phone
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                messages.warning(request, 'Il nome, cognome e/o la classe inseriti non corrispondono a quelli di '
                                          'nessuno studente. Riprova scrivendoli come riportato sui dati ufficiali '
                                          'scolastici. Se proprio non riesci, contatta ... .')
                return redirect('account:register')

            messages.success(request, 'Account creato con successo, ora accedi')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {'form': form})


def settings(request):
    account_form = AccountForm(instance=request.user)

    password_change_form = PasswordChangeForm(user=request.user)
    password_change_form.fields['old_password'].widget.attrs.pop("autofocus", None)

    return render(request, 'account/settings.html',
                  {'account_form': account_form, 'password_change_form': password_change_form})


def update_user(request):
    account_form = AccountForm(request.POST, instance=request.user)
    if account_form.is_valid():
        account_form.save()
        messages.success(request, 'Impostazioni salvate con successo')
        return redirect('home:index')


def change_password(request):
    password_change_form = PasswordChangeForm(data=request.POST, user=request.user)
    if password_change_form.is_valid():
        password_change_form.save()
        messages.success(request, 'Nuova password salvata! Ora riaccedi')
        return redirect('login')


def update_notes(request, user_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=user_id)
    user.notes = request.POST['notes']
    user.save()

    messages.success(request, 'Note salvate')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def import_users(request):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    if request.method == 'GET':
        return render(request, 'account/import_users.html')
    else:
        f = StringIO(request.POST['data'])
        csv_reader = csv.reader(f, delimiter=';')
        for row in csv_reader:
            full_name = row[0]
            classe = row[1]
            try:
                user = User.objects.get(full_name=full_name)
                if not user.verified:
                    user.classe = classe
                    user.verified = True
                    user.save()
            except User.DoesNotExist:
                user = User.objects.create(email=None, password=None, full_name=full_name, classe=classe, verified=True)
                user.groups.add(1)
            except User.MultipleObjectsReturned:
                users = User.objects.filter(full_name=full_name).order_by('-date_joined')
                user = users[0]
                if not user.verified:
                    user.classe = classe
                    user.verified = True
                    user.save()

        messages.success(request, 'Utenti importati con successo')
        return redirect('home:index')


def set_parent(request):
    if request.method == 'GET':
        return render(request, 'account/set_parent.html')
    else:
        user = request.user

        parent_first_name = request.POST['first_name']
        parent_last_name = request.POST['last_name']
        parent_full_name = parent_last_name + ' ' + parent_first_name
        parent_email = request.POST['email']

        if user.email == parent_email:
            messages.warning(request, 'L\'email dello studente non può coincidere con quella del genitore.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            parent = User.objects.get(email=parent_email)
            if not parent.groups.filter(name='genitore').exists():
                messages.warning(request,
                                 '<strong>Errore.</strong> L\'utente compilato ha già un account Aristoph ma non è un '
                                 'genitore. Contatta ...')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except User.DoesNotExist:
            parent = User.objects.create(email=parent_email, password=None, full_name=parent_full_name,
                                         last_name=parent_last_name, first_name=parent_first_name)
            parent.groups.add(6)

        user = request.user
        user.parent = parent
        user.save()

        messages.success(request, 'Genitore aggiunto con successo')
        return redirect('home:index')
