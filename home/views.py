from datetime import datetime, date

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from activities.models import Participation, Activity
from aristoph.local_settings import ALGOLIA
from home.models import Announcement


def current_school_year():
    now = datetime.now()
    if now.month >= 9:
        year1 = now.year
        year2 = year1 + 1
    else:
        year2 = now.year
        year1 = year2 - 1
    return f'{year1}/{year2}'


def index(request):
    user = request.user

    if user.is_authenticated:
        if user.groups.filter(name='studente').exists():
            if not user.phone:
                messages.warning(request, 'Inserisci il tuo numero di cellulare')
                return redirect('account:settings')
            if not user.classe:
                messages.warning(request, 'Inserisci la tua classe attuale')
                return redirect('account:settings')
            if not user.parent:
                messages.warning(request, 'Inserisci i dati di un tuo genitore')
                return redirect('account:set_parent')

        announcements = Announcement.objects \
            .filter(start_at__lte=timezone.now(), end_at__gt=timezone.now()) \
            .order_by('-created_at')

        future_participations = user.participation_set \
                                    .filter(is_active=True, meeting__start_at__gte=date.today()) \
                                    .order_by('meeting__start_at')[:2]

        is_staff = request.user.is_staff
        is_teacher = request.user.groups.filter(name='docente').exists()

        activities = []

        if not is_staff and not is_teacher:
            activities = Activity.objects.filter(is_visible=True, allow_new_reservations=True)

        has_tutor_presence = Participation.objects \
                                 .filter(user=request.user, activity_id=1, group_id=2, presence_type_id=2,
                                         is_active=True) \
                                 .count() > 0

        return render(request, 'home/dashboard.html', {
            'is_staff': is_staff,
            'is_teacher': is_teacher,
            'algolia_config': ALGOLIA,
            'has_tutor_presence': has_tutor_presence,
            'announcements': announcements,
            'future_participations': future_participations,
            'activities': activities
        })
    else:
        return render(request, 'home/welcome.html')


def privacy(request):
    return render(request, 'home/privacy.html')


def cookie(request):
    return render(request, 'home/cookie.html')
