from datetime import datetime, timedelta
from io import BytesIO

import xlsxwriter
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.postgres.aggregates import StringAgg
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import HttpResponseForbidden, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from xhtml2pdf import pisa

from account.models import User
from aristoph.settings import ALGOLIA
from .models import Activity, Subject, Meeting, Participation, Application, Registration, DefaultAssignedUser, \
    MeetingsGenerationOption, PresenceType, ParticipationGroup


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def current_school_year():
    now = datetime.now()
    if now.month >= 9:
        year1 = now.year
        year2 = year1 + 1
    else:
        year2 = now.year
        year1 = year2 - 1
    return f'{year1}/{year2}'


def list_activities(request):
    active_activities = Activity.objects.filter(is_visible=True)
    past_activities = Activity.objects.filter(is_visible=False)

    is_staff = request.user.groups.filter(name='organizzatore peer').exists()
    is_teacher = request.user.groups.filter(name='docente').exists()

    return render(request, 'activities/list.html',
                  {'active_activities': active_activities, 'past_activities': past_activities,
                   'is_staff': is_staff, 'is_teacher': is_teacher})


def create_activities(request):
    is_teacher = request.user.groups.filter(name='docente').exists()

    if not is_teacher and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'GET':
        return render(request, 'activities/create.html')
    else:
        activity_name = request.POST['name']

        if Activity.objects.filter(name=activity_name).count() > 0:
            messages.warning(request, "Il nome dell'attività è già presente. Accedi all'attività cercandola tramite la "
                                      "barra di ricerca sotto 'Attività'")
            return redirect('home:index')

        activity = Activity.objects.create(name=activity_name, allow_student_topics=False,
                                           allow_teacher_topics=True, allow_new_reservations=False,
                                           are_meetings_active=True)

        activity.groups.add(1, 3)

        if 'are_subjects_present' in request.POST:
            subjects = request.POST['subjects'].split('\n')

            for subject_name in subjects:
                Subject.objects.create(activity=activity, name=subject_name)

            messages.success(request, 'Attività e suddivisioni create. Per aggiungere incontri e utenti, '
                                      'seleziona la materia/suddivisione e clicca "+ incontri".')
            return redirect('activities:show_activity', activity.id)
        else:
            subject = Subject.objects.create(activity=activity, name=activity_name)
            messages.success(request, 'Attività creata. Per aggiungere incontri e utenti continua in questa pagina.')

            return redirect('activities:create_meetings', activity.id, subject.id)


def show_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if not activity.is_visible and not request.user.is_staff:
        return HttpResponseForbidden()

    are_there_meetings = activity.meeting_set.filter(is_active=True).count() > 0

    subjects = activity.subject_set.filter(is_active=True)
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()
    is_teacher = request.user.groups.filter(name='docente').exists()

    if request.user.is_authenticated:
        participations = activity.participation_set.filter(user=request.user, is_active=True,
                                                           meeting__start_at__gte=timezone.now()).order_by(
            'meeting__start_at')[:4]
    else:
        participations = []

    groups = activity.groups.order_by('id')

    context = {
        'activity': activity,
        'subjects': subjects,
        'participations': participations,
        'algolia_config': ALGOLIA,
        'is_staff': is_staff,
        'is_teacher': is_teacher,
        'groups': groups,
        'are_there_meetings': are_there_meetings
    }
    return render(request, 'activities/show.html', context)


def show_subject(request, activity_id, subject_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    subject = get_object_or_404(Subject, pk=subject_id)

    is_staff = request.user.groups.filter(name='organizzatore peer').exists()
    is_teacher = request.user.groups.filter(name='docente').exists()

    if 'show_more_future_meetings' in request.GET:
        future_meetings = subject.meeting_set.filter(end_at__gte=timezone.now(), is_active=True).order_by('start_at')
        show_more_future_meetings = True
    else:
        future_meetings = subject.meeting_set.filter(end_at__gte=timezone.now(), is_active=True).order_by('start_at')[
                          :6]
        show_more_future_meetings = False

    if 'show_more_past_meetings' in request.GET:
        past_meetings = subject.meeting_set.filter(end_at__lt=timezone.now(), is_active=True).order_by('-start_at')
        show_more_past_meetings = True
    else:
        past_meetings = subject.meeting_set.filter(end_at__lt=timezone.now(), is_active=True).order_by('-start_at')[:3]
        show_more_past_meetings = False

    context = {'future_meetings': future_meetings, 'past_meetings': past_meetings, 'subject': subject,
               'is_staff': is_staff, 'is_teacher': is_teacher, 'show_more_future_meetings': show_more_future_meetings,
               'show_more_past_meetings': show_more_past_meetings, 'activity': activity}
    return render(request, 'activities/subjects/show.html', context)


def show_meeting(request, activity_id, subject_id, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    activity = meeting.activity

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

    if not meeting.is_active:
        messages.warning(request, 'L\'incontro che hai provato a visitare è stato cancellato, insieme alle sue '
                                  'relative partecipazioni.')
        return redirect('activities:show_subject', activity.id, meeting.subject_id)

    if user.is_authenticated:
        has_reservation = Participation.objects.filter(user=user, meeting=meeting, is_active=True).count() > 0
    else:
        has_reservation = False

    is_teacher = user.groups.filter(name='docente').exists()
    is_staff = user.groups.filter(name='organizzatore peer').exists()

    is_student = user.groups.filter(name='studente').exists()
    meeting_has_started = timezone.now() >= meeting.start_at

    grades_exist = meeting.participation_set.filter(is_active=True, grade__isnull=False).count() > 0

    teacher_topic = ''

    if is_teacher or is_staff:
        participation = meeting.is_teacher_assigned(user)

        if participation:
            teacher_topic = participation.topic

    groups = []

    if 'Peer education' in activity.name:
        for group in activity.groups.order_by('id'):
            group = {'id': group.id, 'name': group.name,
                     'participations': meeting.participation_set.filter(group_id=group.id, is_active=True).order_by(
                         'group_color', 'participation_group_id', 'user__classe', 'user__full_name')}
            groups.append(group)
    else:
        for group in activity.groups.order_by('id'):
            group = {'id': group.id, 'name': group.name,
                     'participations': meeting.participation_set.filter(group_id=group.id, is_active=True).order_by(
                         'group_color', 'participation_group_id', 'user__full_name', 'user__classe')}
            groups.append(group)

    widths = activity.widths.split(',')

    for i, width in enumerate(widths):
        groups[i]['width'] = width

    context = {'meeting': meeting, 'groups': groups, 'is_student': is_student,
               'has_reservation': has_reservation, 'is_staff': is_staff, 'is_teacher': is_teacher,
               'activity': activity,
               'meeting_has_started': meeting_has_started,
               'algolia_config': ALGOLIA,
               'grades_exist': grades_exist,
               'teacher_topic': teacher_topic}

    return render(request, 'activities/subjects/meetings/show.html', context)


def reserve_meeting(request, activity_id, subject_id, meeting_id):
    if request.method == 'POST':
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        activity = meeting.activity
        user = request.user

        if not meeting.is_active:
            messages.warning(request, 'L\'incontro che hai provato a visitare è stato cancellato, insieme alle sue '
                                      'relative partecipazioni.')
            return redirect('activities:show_subject', activity.id, meeting.subject_id)

        if user.is_authenticated:
            has_reservation = Participation.objects.filter(user=user, meeting=meeting,
                                                           is_active=True).count() > 0
        else:
            has_reservation = False

        reservations_limit = meeting.reservations_limit
        topic = request.POST['topic']

        if timezone.now() >= meeting.max_time_limit():
            messages.warning(request, 'Limite temporale di prenotazione superato')
            return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)

        if timezone.now() < meeting.min_time_limit():
            messages.warning(request,
                             'Non è possibile effettuare prenotazioni a distanza di più di un mese dall\'incontro')
            return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)

        if meeting.is_full():
            if reservations_limit == 0:
                message = "Non sono ammesse prenotazioni per questo incontro"
            else:
                message = f"Limite massimo di {reservations_limit} prenotazioni raggiunto. Prenotati per un altro " \
                          f"incontro. "
            messages.warning(request, message)
            return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)

        if has_reservation:
            messages.warning(request, 'Ti sei già prenotato per questo incontro')
            return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)

        if user.participation_set.filter(is_active=True, presence_type_id=3,
                                         activity=activity).count() > 0:
            messages.warning(request, "A causa della tua assenza senza alcun preavviso a un incontro passato "
                                      "non sei più abilitato a prenotarti autonomamente su Aristoph. Se vuoi "
                                      "prenotare una nuova lezione devi far mandare dai tuoi genitori una mail che "
                                      "giustifichi la tua assenza a ...@... .")
            return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)

        if user.groups.filter(name='studente').exists():
            if not user.phone or not user.classe:
                messages.warning(request, 'Compila i dati mancanti prima di poterti prenotare')
                return redirect('account:settings')

        participation = Participation.objects.create(activity_id=activity_id, meeting=meeting, user=user,
                                                     classe=user.classe, group_id=1,
                                                     topic=topic)

        html_message = render_to_string('activities/participations/email.html', {
            'participation': participation,
            'user': user,
            'meeting': meeting
        })

        message = strip_tags(html_message)

        send_mail('La tua prenotazione Aristoph', message, 'Aristoph <noreply@...>',
                  [user.email], True,
                  html_message=html_message)

        success_text = '<h4 class="alert-heading">Prenotazione effettuata con successo!</h4><br><strong>In caso non ' \
                       'potrai più andare, cancellala il prima possibile</strong> ' \
                       'in "Mie partecipazioni" nella ' \
                       'pagina dell\'attività. <strong>In caso di assenza senza preavviso, non potrai più prenotarti ' \
                       'autonomamente</strong> su Aristoph per una nuova lezione. '

        messages.success(request, success_text)
        return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)


def show_participation(request, activity_id, participation_id):
    participation = Participation.objects.get(activity_id=activity_id, pk=participation_id)

    if request.user != participation.user:
        return HttpResponseForbidden()

    return render(request, 'activities/participations/show.html', {'participation': participation})


def delete_participation(request, activity_id, participation_id):
    if request.method == 'POST':
        participation = Participation.objects.get(activity_id=activity_id, pk=participation_id)

        if request.user != participation.user:
            return HttpResponseForbidden()

        meeting = participation.meeting

        if timezone.now() >= meeting.delete_time_limit():
            warning_text = 'Limite temporale di cancellazione superato per Aristoph. Contatta ' \
                           '...@... per disdire. '
            messages.warning(request, warning_text)
            return redirect('activities:show_participation', activity_id, participation_id)

        participation.is_active = False
        participation.save()

        messages.success(request, 'Partecipazione cancellata')
        return redirect('activities:show_activity', activity_id)


def show_date(request, activity_id, year, month, day):
    activity = get_object_or_404(Activity, pk=activity_id)

    date = datetime(year, month, day)
    prev_date = date - timedelta(days=1)
    next_date = date + timedelta(days=1)

    meetings = activity.meeting_set.filter(start_at__gte=date, start_at__lt=next_date, is_active=True).order_by(
        'start_at', 'subject__name')
    context = {'meetings': meetings, 'date': date, 'prev_date': prev_date, 'next_date': next_date,
               'activity': activity}
    return render(request, 'activities/dates/show.html', context)


def edit_participations(request):
    is_teacher = request.user.groups.filter(name='docente').exists()
    is_staff = request.user.is_staff
    is_peer_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_teacher and not is_staff and not is_peer_staff:
        return HttpResponseForbidden()

    selected_participations = request.POST.getlist('selected_participations[]')
    action = request.POST['action']

    participation_group = None

    if action == 'group':
        if len(selected_participations) <= 1:
            messages.warning(request, 'Devi selezionare almeno 2 partecipazioni per creare un gruppo')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        participation_group = ParticipationGroup.objects.create(color=request.POST['color'])

    for selected_participation in selected_participations:
        participation = Participation.objects.get(pk=selected_participation)
        meeting = participation.meeting

        if not is_staff and not is_peer_staff:
            if not meeting.is_teacher_assigned(request.user):
                messages.warning(request, "Non sei inserito come docente nell'incontro della prenotazione perciò non "
                                          "puoi modificarla.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if action == 'delete':
            participation.is_active = False

        if action == 'group':
            participation.participation_group = participation_group
            participation.save()

        if action == 'delete_group':
            participation.participation_group = None
            participation.group_color = None

        if is_teacher or is_staff:
            if action == 'present':
                participation.presence_type_id = 2
                participation.is_active = True

            if action == 'absent':
                participation.presence_type_id = 3
                participation.is_active = True

            if action == 'unspecified_presence':
                participation.presence_type_id = 1
                participation.is_active = True

            if action == 'justify':
                participation.presence_type_id = 4
                participation.is_active = True

            if action == 'absent_morning':
                participation.presence_type_id = 5
                participation.is_active = True

            if action == 'late_entry':
                participation.presence_type_id = 6
                participation.is_active = True

            if action == 'early_exit':
                participation.presence_type_id = 7
                participation.is_active = True

            if action == 'set_grade':
                grade = request.POST['grade']

                if grade == '':
                    participation.grade = None
                else:
                    participation.grade = grade

                participation.is_active = True

        participation.save()
        user = participation.user
        user.save()

    messages.success(request, 'Partecipazioni modificate con successo')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_meetings(request, activity_id, subject_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()
    is_teacher = request.user.groups.filter(name='docente').exists()

    if not is_staff and not is_teacher:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.method == 'GET':
        default_assigned_users = subject.defaultassigneduser_set.all()

        weekdays = subject.weekdays.all()

        dates = []

        if weekdays:

            for subject_weekday in weekdays:
                start_date = timezone.now()
                end_date = start_date + timedelta(days=100)
                number_of_meetings = None

                try:
                    meetings_generation_option = subject.meetingsgenerationoption
                    if meetings_generation_option.start_date:
                        start_date = meetings_generation_option.start_date

                    if meetings_generation_option.end_date:
                        end_date = meetings_generation_option.end_date

                    if meetings_generation_option.number_of_meetings:
                        number_of_meetings = meetings_generation_option.number_of_meetings

                except MeetingsGenerationOption.DoesNotExist:
                    pass

                days_ahead = subject_weekday.id - 1 - start_date.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                date = start_date + timedelta(days=days_ahead)

                if number_of_meetings is None:
                    while date <= end_date:
                        dates.append(date)
                        date += timedelta(days=7)
                else:
                    i = 0
                    while date <= end_date and i < number_of_meetings:
                        dates.append(date)
                        date += timedelta(days=7)
                        i += 1

            dates.sort()

        groups = activity.groups.order_by('id')

        return render(request, 'activities/subjects/meetings/create.html', {
            'dates': dates,
            'activity': activity,
            'subject': subject,
            'algolia_config': ALGOLIA,
            'groups': groups,
            'default_assigned_users': default_assigned_users
        })
    else:
        dates = request.POST.getlist('dates[]')
        users = request.POST.getlist('users[]')

        if request.POST['type'] == 'automatic':

            for date in dates:
                start_at = datetime.strptime(date + ' ' + subject.default_start_time.strftime('%H:%M:%S'),
                                             '%Y-%m-%d %H:%M:%S')
                end_at = datetime.strptime(date + ' ' + subject.default_end_time.strftime('%H:%M:%S'),
                                           '%Y-%m-%d %H:%M:%S')

                meeting = Meeting.objects.create(activity_id=activity_id, subject=subject, start_at=start_at,
                                                 end_at=end_at,
                                                 room=subject.default_room,
                                                 reservations_limit=subject.default_reservations_limit)

                for user in users:
                    user_id, group_id = user.split(',')
                    try:
                        user = User.objects.get(pk=user_id)
                        Participation.objects.create(
                            activity_id=activity_id, meeting_id=meeting.id,
                            user=user, classe=user.classe, group_id=group_id)

                        if 'make_default' in request.POST:
                            if DefaultAssignedUser.objects.filter(activity_id=activity_id,
                                                                  subject_id=meeting.subject_id, group_id=group_id,
                                                                  user=user).count() == 0:
                                DefaultAssignedUser.objects.create(activity_id=activity_id,
                                                                   subject_id=meeting.subject_id,
                                                                   group_id=group_id, user=user)
                    except User.DoesNotExist:
                        pass

        else:
            start_ats = request.POST.getlist('start_ats[]')
            end_ats = request.POST.getlist('end_ats[]')
            topics = request.POST.getlist('topics[]')

            for i in range(len(dates)):
                try:
                    start_at = datetime.strptime(dates[i] + ' ' + start_ats[i], '%Y-%m-%d %H:%M')
                    end_at = datetime.strptime(dates[i] + ' ' + end_ats[i], '%Y-%m-%d %H:%M')
                except ValueError:
                    messages.warning(request, 'Il formato delle ore di inizio o di fine è sbagliato. Deve essere HH:MM')
                    return redirect('activities:create_meetings', activity_id, subject_id)

                if not activity.allow_event_overlapping:
                    if activity.meeting_set.filter(end_at__gt=start_at, start_at__lt=end_at, is_active=True).count() > 0:
                        messages.warning(request, "Esiste già un incontro a quest'ora per questa attività.")
                        return redirect('activities:create_meetings', activity_id, subject_id) 


                meeting = Meeting.objects.create(activity_id=activity_id, subject=subject, start_at=start_at,
                                                 end_at=end_at,
                                                 reservations_limit=subject.default_reservations_limit)
                

                for user in users:
                    user_id, group_id = user.split(',')
                    try:
                        user = User.objects.get(pk=user_id)

                        if group_id == "3":
                            Participation.objects.create(
                                activity_id=activity_id, meeting_id=meeting.id,
                                user=user, classe=user.classe, group_id=group_id, topic=topics[i])
                        else:
                            Participation.objects.create(
                                activity_id=activity_id, meeting_id=meeting.id,
                                user=user, classe=user.classe, group_id=group_id)

                        if 'make_default' in request.POST:
                            if DefaultAssignedUser.objects.filter(activity_id=activity_id,
                                                                  subject_id=meeting.subject_id, group_id=group_id,
                                                                  user=user).count() == 0:
                                DefaultAssignedUser.objects.create(activity_id=activity_id,
                                                                   subject_id=meeting.subject_id,
                                                                   group_id=group_id, user=user)
                    except User.DoesNotExist:
                        pass

        messages.success(request, 'Incontri aggiunti con successo')
        return redirect('activities:show_activity', activity_id)


def list_participations(request, activity_id):
    is_teacher = request.user.groups.filter(name='docente').exists()
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff and not is_teacher:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)

    _vals = {'is_active': True}

    participation_group = 0
    if 'participation_group' in request.GET:
        participation_group = int(request.GET['participation_group'])
        if participation_group != 0:
            _vals['group_id'] = participation_group

    presence_type = 0
    if 'presence_type' in request.GET:
        presence_type = int(request.GET['presence_type'])
        if presence_type != 0:
            _vals['presence_type_id'] = presence_type

    subject = 0
    if 'subject' in request.GET:
        subject = int(request.GET['subject'])
        if subject != 0:
            _vals['meeting__subject_id'] = subject

    classe = ''
    if 'classe' in request.GET:
        classe = request.GET['classe']
        if classe != '':
            _vals['user__classe'] = classe.upper()

    time = 0
    if 'time' in request.GET:
        time = int(request.GET['time'])
        if time == 1:
            _vals['meeting__start_at__lt'] = timezone.now()
        if time == 2:
            _vals['meeting__start_at__gte'] = timezone.now()

    participations = activity.participation_set.filter(**_vals).order_by('user__full_name', 'meeting__start_at',
                                                                         'meeting__subject__name')

    paginator = Paginator(participations, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    participation_groups = activity.groups.order_by('id')
    presence_types = PresenceType.objects.all()
    subjects = activity.subject_set.all()

    return render(request, 'activities/participations/list.html', {
        'page_obj': page_obj,
        'activity': activity,
        'is_teacher': is_teacher,
        'is_staff': is_staff,
        'participation_groups': participation_groups,
        'presence_types': presence_types,
        'participation_group_id': participation_group,
        'presence_type_id': presence_type,
        'classe': classe,
        'subjects': subjects,
        'subject_id': subject,
        'time': time
    })


def list_participations_xlsx(request, activity_id):
    is_teacher = request.user.groups.filter(name='docente').exists()
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff and not is_teacher:
        return HttpResponseForbidden()

    response = HttpResponse(content_type='application/vnd.ms-excel')

    response['Content-Disposition'] = 'attachment; filename="partecipazioni.xlsx"'

    workbook = xlsxwriter.Workbook(response, {'in_memory': True})

    worksheet = workbook.add_worksheet()

    activity = get_object_or_404(Activity, pk=activity_id)

    _vals = {'is_active': True}

    participation_group = 0
    if 'participation_group' in request.GET:
        participation_group = int(request.GET['participation_group'])
        if participation_group != 0:
            _vals['group_id'] = participation_group

    presence_type = 0
    if 'presence_type' in request.GET:
        presence_type = int(request.GET['presence_type'])
        if presence_type != 0:
            _vals['presence_type_id'] = presence_type

    subject = 0
    if 'subject' in request.GET:
        subject = int(request.GET['subject'])
        if subject != 0:
            _vals['meeting__subject_id'] = subject

    classe = ''
    if 'classe' in request.GET:
        classe = request.GET['classe']
        if classe != '':
            _vals['user__classe'] = classe.upper()

    time = 0
    if 'time' in request.GET:
        time = int(request.GET['time'])
        if time == 1:
            _vals['meeting__start_at__lt'] = timezone.now()
        if time == 2:
            _vals['meeting__start_at__gte'] = timezone.now()

    participations = activity.participation_set.filter(**_vals).order_by('user__full_name', 'meeting__start_at',
                                                                         'meeting__subject__name')

    row = 0

    worksheet.write(row, 0, "utente")
    worksheet.write(row, 1, "classe")
    worksheet.write(row, 2, "tipo")
    worksheet.write(row, 3, "data")
    worksheet.write(row, 4, "materia")
    worksheet.write(row, 5, "presenza")

    row += 1

    for participation in participations:
        worksheet.write(row, 0, participation.user.full_name)
        worksheet.write(row, 1, participation.classe)
        worksheet.write(row, 2, participation.group.name)
        worksheet.write(row, 3, participation.meeting.start_at.strftime("%d/%m/%Y"))
        worksheet.write(row, 4, participation.meeting.subject.name)
        worksheet.write(row, 5, participation.presence_type.name)
        row += 1

    workbook.close()
    return response


def list_participations_by_user(request, activity_id, user_id):
    is_teacher = request.user.groups.filter(name='docente').exists()
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if (not is_staff) and (request.user.id != user_id):
        return HttpResponseForbidden()

    activities = Activity.objects.filter(is_visible=True).order_by('name')

    user = get_object_or_404(User, pk=user_id)

    participations = user.participation_set \
        .order_by('-meeting__start_at') \
        .filter(activity_id=activity_id, is_active=True)

    return render(request, 'activities/participations/list_by_user.html', {
        'participations': participations,
        'activities': activities,
        'is_teacher': is_teacher,
        'is_staff': is_staff,
        'activity_id': activity_id,
        'user': user
    })


def list_participations_stats(request, activity_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activities = Activity.objects.filter(start_at__lte=timezone.now(), end_at__gt=timezone.now())

    participations = Participation.objects.filter(activity_id=activity_id, is_active=True)

    return render(request, 'activities/participations/list_stats.html', {
        'participations': participations,
        'activities': activities,
        'activity_id': activity_id
    })


def list_meetings_stats(request, activity_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activities = Activity.objects.filter(start_at__lte=timezone.now(), end_at__gt=timezone.now())

    meetings = Meeting.objects \
        .filter(activity_id=activity_id, is_active=True, start_at__lte=timezone.now()) \
        .order_by('start_at')

    return render(request, 'activities/meetings/list_stats.html', {
        'meetings': meetings,
        'activities': activities,
        'activity_id': activity_id
    })


def subject_stats(request, activity_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)
    subjects_db = activity.subject_set.filter(is_active=True).order_by('name')
    subjects = []
    for subject_db in subjects_db:
        presences_count = 0
        absences_count = 0
        attended_meetings = 0
        unattended_meetings = 0
        meetings = subject_db.meeting_set.filter(is_active=True, end_at__lte=timezone.now())
        for meeting in meetings:
            meeting_presences_count = meeting.participation_set.filter(is_active=True, group_id=1,
                                                                       presence_type_id=2).count()
            meeting_absences_count = meeting.participation_set.filter(is_active=True, group_id=1).filter(
                Q(presence_type_id=3) | Q(presence_type_id=4)).count()
            if meeting_presences_count > 0:
                attended_meetings += 1
            else:
                unattended_meetings += 1
            presences_count += meeting_presences_count
            absences_count += meeting_absences_count

        subject = {
            'name': subject_db.name,
            'presences_count': presences_count,
            'absences_count': absences_count,
            'attended_meetings': attended_meetings,
            'unattended_meetings': unattended_meetings
        }
        subjects.append(subject)

    return render(request, 'activities/stats/subjects.html', {'subjects': subjects, 'activity': activity})


def user_stats(request, activity_id, participation_group_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)
    participation_group = get_object_or_404(Group, pk=participation_group_id)
    users = Participation.objects.values('user__full_name', 'user__classe') \
        .filter(activity=activity, group=participation_group, presence_type_id=2, is_active=True) \
        .order_by('user__full_name') \
        .annotate(
        presences_count=Count('id'),
        meeting_duration_sum=Sum('meeting__duration'),
        subjects_string=StringAgg('meeting__subject__name', ', '))

    return render(request, 'activities/stats/users.html', {
        'users': users, 'activity': activity, 'participation_group': participation_group})


def user_stats_xlsx(request, activity_id, participation_group_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff:
        return HttpResponseForbidden()

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="riepilogo-ore.xlsx"'
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    activity = get_object_or_404(Activity, pk=activity_id)
    participation_group = get_object_or_404(Group, pk=participation_group_id)
    users = Participation.objects.values('user__full_name', 'user__classe') \
        .filter(activity=activity, group=participation_group, presence_type_id=2, is_active=True) \
        .order_by('user__full_name') \
        .annotate(
        presences_count=Count('id'),
        meeting_duration_sum=Sum('meeting__duration'),
        subjects_string=StringAgg('meeting__subject__name', ', '))

    row = 0

    worksheet.write(row, 0, participation_group.name.capitalize())
    worksheet.write(row, 1, "Classe")
    worksheet.write(row, 2, "N. presenze")
    worksheet.write(row, 3, "Ore di presenza")
    worksheet.write(row, 4, "Materie")

    row += 1

    for user in users:
        worksheet.write(row, 0, user['user__full_name'])
        if user['user__classe']:
            worksheet.write(row, 1, user['user__classe'])
        else:
            worksheet.write(row, 1, "")
        worksheet.write(row, 2, user['presences_count'])
        worksheet.write(row, 3, user['meeting_duration_sum'])
        worksheet.write(row, 4, user['subjects_string'])
        row += 1

    workbook.close()
    return response


def classe_stats(request, activity_id, participation_group_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists() or request.user.groups.filter(
        name='docente').exists()

    if not is_staff:
        return HttpResponseForbidden()

    activity = get_object_or_404(Activity, pk=activity_id)
    participation_group = get_object_or_404(Group, pk=participation_group_id)

    classi = Participation.objects \
        .values('user__classe') \
        .filter(activity=activity, group=participation_group, is_active=True) \
        .order_by('user__classe') \
        .annotate(
        presences_count=Count('id', filter=Q(presence_type_id=2)),
        absences_count=Count('id', filter=Q(presence_type_id=3)),
        present_users_count=Count('user_id', filter=Q(presence_type_id=2), distinct=True),
        absent_users_count=Count('user_id', filter=Q(presence_type_id=3), distinct=True))

    return render(request, 'activities/stats/classi.html', {
        'classi': classi, 'activity': activity, 'participation_group': participation_group})


def delete_meeting(request, activity_id, subject_id, meeting_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()

    if not is_staff or not request.method == 'POST':
        return HttpResponseForbidden()

    meeting = get_object_or_404(Meeting, pk=meeting_id)

    if request.POST['message'] != '':
        for participation in meeting.participation_set.filter(group_id=1, is_active=True):
            user = participation.user
            email = send_mail('Avviso di cancellazione incontro ' + meeting.activity.name,
                              "Gentile " + user.full_name + ",\n\n" + request.POST['message'],
                              'Assistenza Aristoph <...@...>', [user.email])

    meeting.delete()

    messages.success(request, 'L\'incontro e le sue relative partecipazioni sono state cancellate.')
    return redirect('activities:show_subject', meeting.activity_id, meeting.subject_id)


def create_applications(request, activity_id, subject_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    is_student = request.user.groups.filter(name='studente').exists()

    if not is_student:
        return HttpResponseForbidden()

    if not activity.are_applications_active:
        return HttpResponseForbidden()

    subject = get_object_or_404(Subject, pk=subject_id)

    if Application.objects.filter(activity=activity, subject=subject, user=request.user, group_id=2).count() > 0:
        messages.warning(request, "Già hai inviato una candidatura per questa materia. Per modificarla contattare "
                                  "l'assistenza.")
        return redirect('activities:show_activity', activity.id)

    if request.method == 'GET':
        return render(request, 'activities/subjects/applications/create.html', {
            'subject': subject, 'activity': activity})
    else:
        last_year_grade = request.POST['last_year_grade']
        weekdays = request.POST.getlist('weekdays[]')

        if len(weekdays) == 0:
            messages.warning(request, 'Devi selezionare almeno un giorno settimanale in cui sarai disponibile.')
            return redirect('activities:create_applications', activity.id, subject.id)

        asl = False

        if 'asl' in request.POST:
            asl = True

        application = Application.objects.create(activity=activity, subject=subject, user=request.user, group_id=2,
                                                 last_year_grade=last_year_grade, asl=asl)

        for weekday in weekdays:
            application.weekdays.add(weekday)

        messages.success(request, "Candidatura inviata! Per candidarti anche per un'altra materia, compila di nuovo "
                                  "il modulo selezionando la materia interessata.")
        return redirect('activities:show_activity', activity.id)


def create_registrations(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    is_student = request.user.groups.filter(name='studente').exists()

    if not is_student:
        return HttpResponseForbidden()

    if not activity.are_registrations_active:
        return HttpResponseForbidden()

    if Registration.objects.filter(activity=activity, user=request.user).count() > 0:
        messages.warning(request, "Hai già inviato un'iscrizione. Per modificarla contattare "
                                  "l'assistenza.")
        return redirect('activities:show_activity', activity.id)

    if request.method == 'GET':
        chimica = 30 - Registration.objects.filter(activity=activity, chimica=True).count()
        biologia = 30 - Registration.objects.filter(activity=activity, biologia=True).count()
        matematica = 30 - Registration.objects.filter(activity=activity, matematica=True).count()

        return render(request, 'activities/registrations/create.html', {
            'activity': activity, 'biologia': biologia, 'matematica': matematica, 'chimica': chimica})
    else:
        courses = request.POST.getlist('courses[]')

        if 'biologia' in courses:
            if Registration.objects.filter(activity=activity, biologia=True).count() < 30:
                biologia = True
            else:
                biologia = False
        else:
            biologia = False

        if 'chimica' in courses:
            if Registration.objects.filter(activity=activity, chimica=True).count() < 30:
                chimica = True
            else:
                chimica = False
        else:
            chimica = False

        if 'matematica' in courses:
            if Registration.objects.filter(activity=activity, matematica=True).count() < 30:
                matematica = True
            else:
                matematica = False
        else:
            matematica = False

        if not matematica and not biologia and not chimica:
            messages.warning(request, "Devi selezionare almeno un'opzione.")
            return redirect('activities:create_registrations', activity.id)

        Registration.objects.create(activity=activity, user=request.user, biologia=biologia, chimica=chimica,
                                    matematica=matematica)

        messages.success(request, "Iscrizione inviata!")
        return redirect('activities:show_activity', activity.id)


def edit_topic(request, activity_id, subject_id, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    participation = meeting.is_teacher_assigned(request.user)

    if not participation:
        messages.warning(request, "Non sei inserito come docente nell'incontro della prenotazione perciò non "
                                  "puoi modificarla.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    topic = request.POST['topic']
    topic_len = len(topic)

    if topic_len > 300:
        message_text = "L'argomento che hai scritto è lungo " + str(
            topic_len) + " caratteri, mentre il limite è di 300."
        messages.warning(request, message_text)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    participation.topic = request.POST['topic']
    participation.save()

    messages.success(request, "Argomento della lezione modificato!")
    return redirect('activities:show_meeting', activity_id, subject_id, meeting_id)


def add_users_to_meetings(request, activity_id, meetings):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists() or request.user.groups.filter(
        name='docente').exists()

    if not is_staff:
        return HttpResponseForbidden()

    meetings_list = meetings.split(',')

    if request.method == 'GET':
        meeting = get_object_or_404(Meeting, pk=meetings_list[0])

        default_assigned_users = meeting.subject.defaultassigneduser_set.all()

        activity = get_object_or_404(Activity, pk=activity_id)
        groups = activity.groups.order_by('id')

        return render(request, 'activities/add_users_to_meetings.html', {
            'activity': activity, 'meetings': meetings, 'algolia_config': ALGOLIA, 'groups': groups,
            'default_assigned_users': default_assigned_users})
    else:

        users = request.POST.getlist('users[]')

        for meeting_id in meetings_list:
            try:
                meeting = Meeting.objects.get(pk=meeting_id)

                if not is_staff:
                    if not meeting.is_teacher_assigned(request.user):
                        messages.warning(request,
                                         "Non sei inserito come docente nell'incontro della prenotazione perciò non "
                                         "puoi modificarla.")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                for user in users:
                    user_id, group_id = user.split(',')
                    try:
                        user = User.objects.get(pk=user_id)
                        Participation.objects.create(
                            activity_id=activity_id, meeting_id=meeting_id,
                            user=user, classe=user.classe, group_id=group_id)

                        if 'make_default' in request.POST:
                            if DefaultAssignedUser.objects.filter(activity_id=activity_id,
                                                                  subject_id=meeting.subject_id, group_id=group_id,
                                                                  user=user).count() == 0:
                                DefaultAssignedUser.objects.create(activity_id=activity_id,
                                                                   subject_id=meeting.subject_id,
                                                                   group_id=group_id, user=user)
                    except User.DoesNotExist:
                        pass
            except Meeting.DoesNotExist:
                pass

        messages.success(request, 'Utenti aggiunti con successo')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def clean_up_presences(request):
    now = datetime.now()

    if now.hour >= 17:
        this_year = datetime(2019, 9, 1)

        meetings = Meeting.objects.filter(start_at__gte=this_year, end_at__lt=now, is_active=True)

        for meeting in meetings:
            for participation in meeting.participation_set.filter(is_active=True, presence_type_id=1):
                participation.presence_type_id = 3
                participation.save()

    return HttpResponse('ok')


def show_activity_users(request, activity_id, subject_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    subject = get_object_or_404(Subject, pk=subject_id, activity_id=activity_id)
    activity = subject.activity

    if request.method == 'GET':
        users = subject.defaultassigneduser_set.order_by('group_id', 'user__full_name')

        return render(request, 'activities/subjects/show_activity_users.html', {
            'users': users, 'subject': subject, 'activity': activity})
    else:
        default_assigned_users = request.POST.getlist('users[]')
        action = request.POST['action']

        if action == 'delete':
            for default_assigned_user_id in default_assigned_users:
                default_assigned_user = DefaultAssignedUser.objects.get(pk=default_assigned_user_id)
                default_assigned_user.delete()

                meetings = subject.meeting_set.filter(end_at__gte=timezone.now(), is_active=True).order_by('start_at')

                for meeting in meetings:
                    try:
                        participation = meeting.participation_set.get(is_active=True,
                                                                      user_id=default_assigned_user.user_id,
                                                                      group_id=default_assigned_user.group_id)
                        participation.is_active = False
                        participation.save()
                    except Participation.DoesNotExist:
                        pass

            messages.success(request, 'Utenti rimossi con successo')
            return redirect('activities:show_activity_users', activity_id, subject_id)


def add_users_by_classe(request, activity_id, subject_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    subject = get_object_or_404(Subject, pk=subject_id, activity_id=activity_id)
    activity = subject.activity

    if request.method == 'GET':
        return render(request, 'activities/add_users_by_classe.html', {
            'activity': activity, 'subject': subject})
    else:
        users = User.objects.filter(classe=request.POST['classe'], verified=True)

        for user in users:
            DefaultAssignedUser.objects.create(activity=activity,
                                               subject=subject,
                                               group_id=1, user=user)

        messages.success(request, 'Utenti aggiunti con successo')
        return redirect('activities:show_activity_users', activity.id, subject.id)


def create_subjects(request, activity_id):
    is_staff = request.user.groups.filter(name='organizzatore peer').exists()
    is_teacher = request.user.groups.filter(name='docente').exists()

    if not is_staff and not is_teacher:
        return HttpResponseForbidden()
    
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == 'GET':
        return render(request, 'activities/subjects/create.html', {'activity': activity})
    else:
        Subject.objects.create(activity=activity, name=request.POST['name'])
        return redirect('activities:show_activity', activity.id)
