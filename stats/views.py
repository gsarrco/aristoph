from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from activities.models import Activity, Subject


def presences_by_meeting_and_user(request, activity_id, subject_id, group_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)

    if request.GET.get('format') == 'xlsx':
        response = activity.student_registry_xlsx()

        return response

    subject = get_object_or_404(Subject, pk=subject_id)

    meetings, result = subject.student_registry()

    return render(request, 'stats/presences_by_meeting_and_user.html', {
        'activity': activity, 'subject': subject, 'result': result, 'meetings': meetings})


def student_registry(request, activity_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)

    response = activity.student_registry_xlsx()

    return response
