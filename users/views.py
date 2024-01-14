from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from account.models import User
from activities.models import Activity


def show_users(request, user_id):
    is_teacher = request.user.groups.filter(name='docente').exists()
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if (not is_staff) and (request.user.id != user_id):
        return HttpResponseForbidden()

    activities = Activity.objects.filter(is_visible=True).order_by('name')

    user = get_object_or_404(User, pk=user_id)

    participations = user.participation_set \
        .order_by('meeting__start_at') \
        .filter(is_active=True)

    return render(request, 'users/show.html', {
        'participations': participations,
        'activities': activities,
        'is_teacher': is_teacher,
        'is_staff': is_staff,
        'user': user
    })
