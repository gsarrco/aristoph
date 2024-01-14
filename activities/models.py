from datetime import timedelta, datetime

import xlsxwriter
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from account.models import User


class Activity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_visible = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    are_applications_active = models.BooleanField(default=False)
    are_meetings_active = models.BooleanField(default=True)
    are_registrations_active = models.BooleanField(default=False)
    allow_new_reservations = models.BooleanField(default=False)
    allow_student_topics = models.BooleanField(default=False)
    allow_teacher_topics = models.BooleanField(default=True)
    allow_event_overlapping = models.BooleanField(default=True)
    widths = models.CharField(max_length=10, default='9,3')

    def __str__(self):
        return self.name

    def has_default_assigned_users(self):
        return self.defaultassigneduser_set.count() > 0

    def future_meetings_count(self):
        return self.meeting_set.filter(end_at__gte=timezone.now(), is_active=True).count()

    def is_active(self):
        return self.is_visible

    def has_only_one_subject(self):
        return self.subject_set.filter(is_active=True).count() == 1

    def count_attended_meetings(self):
        count = 0

        meetings = self.meeting_set.filter(is_active=True)

        for meeting in meetings:
            if meeting.has_presences():
                count += 1

        return count

    def cumulative_duration(self):
        hours = 0

        meetings = self.meeting_set.filter(is_active=True)

        for meeting in meetings:
            if meeting.has_presences():
                diff = meeting.end_at - meeting.start_at
                hours += diff.total_seconds() / 3600

        return hours

    def student_registry_xlsx(self):
        subjects = self.subject_set.filter(is_active=True)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="registro-studenti_{slugify(self.name)}.xlsx"'
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})

        present_format = workbook.add_format()
        present_format.set_font_color('green')

        absent_format = workbook.add_format()
        absent_format.set_font_color('red')

        header_format = workbook.add_format()
        header_format.set_bold()

        for subject in subjects:
            worksheet = workbook.add_worksheet(subject.name[:31])
            meetings, result = subject.student_registry()

            worksheet.write(0, 0, "Utente", header_format)
            worksheet.write(0, 1, "Classe", header_format)

            columns1 = 2

            for meeting in meetings:
                worksheet.write(0, columns1, meeting.start_at.strftime('%d/%m'), header_format)
                columns1 += 1

            row = 1

            meetings_presences_count = {}
            meetings_absences_count = {}

            for user in result:
                worksheet.write(row, 0, user['full_name'])
                worksheet.write(row, 1, user['classe'])

                columns2 = 2

                for participation in user['participations']:
                    if participation['presence_type'] == 'presente':
                        worksheet.write(row, columns2, participation['presence_type'], present_format)

                        if participation['meeting_id'] in meetings_presences_count:
                            meetings_presences_count[participation['meeting_id']] += 1
                        else:
                            meetings_presences_count[participation['meeting_id']] = 1
                    elif participation['presence_type'] == 'assente':
                        worksheet.write(row, columns2, participation['presence_type'], absent_format)

                        if participation['meeting_id'] in meetings_absences_count:
                            meetings_absences_count[participation['meeting_id']] += 1
                        else:
                            meetings_absences_count[participation['meeting_id']] = 1
                    else:
                        worksheet.write(row, columns2, participation['presence_type'])
                    columns2 += 1

                row += 1

            worksheet.write(row, 0, 'Presenti', header_format)

            column = 2
            for meeting in meetings:
                if meeting.id in meetings_presences_count:
                    worksheet.write(row, column, meetings_presences_count[meeting.id])
                else:
                    worksheet.write(row, column, 0)
                column += 1

            row += 1
            worksheet.write(row, 0, 'Assenti', header_format)

            column = 2
            for meeting in meetings:
                if meeting.id in meetings_absences_count:
                    worksheet.write(row, column, meetings_absences_count[meeting.id])
                else:
                    worksheet.write(row, column, 0)
                column += 1

        workbook.close()
        return response

    class Meta:
        verbose_name = "attività"
        verbose_name_plural = "attività"


class Weekday(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "giorno settimanale"
        verbose_name_plural = "giorni settimanali"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('active'), default=True)
    weekdays = models.ManyToManyField(Weekday, blank=True)
    default_room = models.CharField(max_length=30, default=None, blank=True, null=True)
    default_start_time = models.TimeField(default=None, blank=True, null=True)
    default_end_time = models.TimeField(default=None, blank=True, null=True)
    default_reservations_limit = models.PositiveIntegerField(default=10)
    offers_asl = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def count_attended_meetings(self):
        count = 0

        meetings = self.meeting_set.filter(is_active=True)

        for meeting in meetings:
            if meeting.has_presences():
                count += 1

        return count

    def cumulative_duration(self):
        hours = 0

        meetings = self.meeting_set.filter(is_active=True)

        for meeting in meetings:
            if meeting.has_presences():
                diff = meeting.end_at - meeting.start_at
                hours += diff.total_seconds() / 3600

        return hours

    def teachers(self):
        teacher_names = [teacher.user.full_name for teacher in self.defaultassigneduser_set.filter(group_id=3)]

        return ','.join(teacher_names)

    def student_registry(self):
        activity = self.activity

        defaultassignedusers = self.defaultassigneduser_set.filter(group_id=1).order_by('user__full_name')
        meetings = activity.meeting_set.filter(subject=self, is_active=True, end_at__lt=datetime.now()) \
            .order_by('start_at')
        result = []
        for defaultassigneduser in defaultassignedusers:
            user = defaultassigneduser.user
            participations = []
            for meeting in meetings:
                try:
                    participation = Participation.objects.get(user=user, meeting=meeting, activity=activity,
                                                              is_active=True)
                    presence_type = participation.presence_type
                    participations.append({'presence_type': presence_type.name,
                                           'text_class': presence_type.text_class,
                                           'meeting_id': participation.meeting_id})
                except Participation.DoesNotExist:
                    participations.append({'presence_type': 'non aggiunto', 'text_class': 'text-secondary'})
                except Participation.MultipleObjectsReturned:
                    print(f'User {user.id} is duplicated in meeting {meeting.id}')

            result.append({'full_name': user.full_name, 'classe': user.classe, 'participations': participations})

        return meetings, result

    class Meta:
        verbose_name = "materia"
        verbose_name_plural = "materie"
        ordering = ['name']


class Meeting(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    duration = models.FloatField(default=1.5)
    room = models.CharField(max_length=30, default=None, blank=True, null=True)
    reservations_limit = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(_('active'), default=True)

    def __str__(self):
        return self.subject.name + ' ' + self.start_at.strftime("%d/%m/%y")

    def max_time_limit(self):
        return (self.start_at - timedelta(days=2)).replace(hour=23, minute=0)

    def min_time_limit(self):
        return self.start_at - timedelta(days=30)

    def delete_time_limit(self):
        return (self.start_at - timedelta(days=1)).replace(hour=11, minute=0)

    def is_full(self):
        reservations_count = self.participation_set.filter(is_active=True, group_id=1).count()
        reservations_limit = self.reservations_limit

        return reservations_count >= reservations_limit

    def has_presences(self):
        return self.participation_set.filter(is_active=True, group_id=1, presence_type_id=2).count() > 0

    def presences_count(self):
        return self.participation_set.filter(is_active=True, group_id=1, presence_type_id=2).count()

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()
        for participation in self.participation_set.filter(is_active=True):
            participation.is_active = False
            participation.save()

    def is_teacher_assigned(self, user):
        try:
            participation = self.participation_set.get(user=user, is_active=True)
            return participation
        except Participation.DoesNotExist:
            return False

    def is_today(self):
        return self.start_at.date() == datetime.today().date()

    def calculate_duration(self):
        diff = self.end_at - self.start_at
        self.duration = diff.total_seconds() / 3600

    class Meta:
        verbose_name = "incontro"
        verbose_name_plural = "incontri"


class PresenceType(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "tipo di presenza"
        verbose_name_plural = "tipi di presenza"
        ordering = ['id']

    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=50)
    text_class = models.CharField(max_length=50)


class ParticipationGroup(models.Model):
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def active_participations_count(self):
        return self.participation_set.filter(is_active=True).count()


class Participation(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classe = models.CharField(max_length=3, default=None, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    topic = models.TextField(default=None, blank=True, null=True)
    grade = models.CharField(max_length=100, default=None, blank=True, null=True)
    group_color = models.CharField(max_length=10, default=None, blank=True, null=True)
    presence_type = models.ForeignKey(PresenceType, default=1, on_delete=models.CASCADE)
    participation_group = models.ForeignKey(ParticipationGroup, default=None, blank=True, null=True,
                                            on_delete=models.SET_NULL)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        meeting = self.meeting
        user = self.user
        return meeting.subject.name + ' ' + meeting.start_at.strftime(
            "%d/%m/%y") + ', ' + user.full_name

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        return self.save()

    class Meta:
        verbose_name = "partecipazione"
        verbose_name_plural = "partecipazioni"
        ordering = ['id']


class Application(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    weekdays = models.ManyToManyField(Weekday)
    last_year_grade = models.PositiveIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    asl = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def implode_weekdays(self):
        return " ".join(weekday.name for weekday in self.weekdays.all())

    class Meta:
        verbose_name = 'candidatura'
        verbose_name_plural = 'candidature'


class Registration(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    biologia = models.BooleanField(default=False)
    chimica = models.BooleanField(default=False)
    matematica = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user = self.user
        return user.full_name

    class Meta:
        verbose_name = 'iscrizione'
        verbose_name_plural = 'iscrizioni'


class DefaultAssignedUser(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.activity.name + ', ' + self.subject.name + ', ' + self.user.full_name


class MeetingsGenerationOption(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(default=None, blank=True, null=True)
    number_of_meetings = models.PositiveIntegerField(default=None, blank=True, null=True)

    class Meta:
        verbose_name = 'opzione generazione incontri'
        verbose_name_plural = 'opzioni generazione incontri'
