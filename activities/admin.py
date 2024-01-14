from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.shortcuts import redirect
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from activities.models import *

admin.site.disable_action('delete_selected')


def delete(modeladmin, request, queryset):
    queryset.update(is_active=False)


delete.short_description = "Cancella elementi selezionati"


def undelete(modeladmin, request, queryset):
    queryset.update(is_active=True)


undelete.short_description = "Ripristina elementi selezionati"


class SubjectResource(resources.ModelResource):
    activity__name = Field(attribute='activity__name', column_name='nome attività')
    name = Field(attribute='name', column_name='nome materia')
    count_attended_meetings = Field(attribute='count_attended_meetings', column_name='incontri effettivamente svolti')
    cumulative_duration = Field(attribute='cumulative_duration', column_name='ore effettivamente svolte')
    teachers = Field(attribute='teachers', column_name='docenti')

    class Meta:
        model = Subject
        fields = ('activity__name', 'name', 'count_attended_meetings', 'cumulative_duration', 'teachers')


class SubjectAdmin(ImportExportModelAdmin):
    ordering = ('activity__name', 'name')
    list_display = ('name', 'default_reservations_limit')
    search_fields = ['name']
    list_filter = ('activity__name', 'activity__is_visible', 'is_active')
    actions = [delete, undelete]
    resource_class = SubjectResource


admin.site.register(Subject, SubjectAdmin)


class ActivityResource(resources.ModelResource):
    name = Field(attribute='name', column_name='nome')
    count_attended_meetings = Field(attribute='count_attended_meetings', column_name='incontri effettivamente svolti')
    cumulative_duration = Field(attribute='cumulative_duration', column_name='ore effettivamente svolte')

    class Meta:
        model = Activity
        fields = ('name', 'count_attended_meetings', 'cumulative_duration')


def set_invisible(modeladmin, request, queryset):
    queryset.update(is_visible=False)


set_invisible.short_description = "Archivia"


class ActivityAdmin(ImportExportModelAdmin):
    list_display = ('__str__', 'is_visible')
    list_filter = ('is_visible',)
    actions = ['delete_selected', set_invisible]
    resource_class = ActivityResource


admin.site.register(Activity, ActivityAdmin)


class ParticipationAdmin(ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('__str__', 'is_active', 'updated_at')
    list_filter = ('activity', 'meeting__subject__name')
    date_hierarchy = 'meeting__start_at'
    actions = [delete, undelete]


admin.site.register(Participation, ParticipationAdmin)


def add_users_to_meetings(modeladmin, request, meetings):
    activity_id = meetings.values('activity_id')[0]['activity_id']
    meetings_list = [str(meeting['id']) for meeting in meetings.values('id')]
    meetings_string = ', '.join(meetings_list)
    return redirect('activities:add_users_to_meetings', activity_id, meetings_string)


add_users_to_meetings.short_description = "Aggiungi utenti a incontri"


def delete_meeting(modeladmin, request, meetings):
    for meeting in meetings:
        meeting.delete()


delete_meeting.short_description = "Cancella incontri selezionati e relative partecipazioni"


def reset_default_reservations_limit(modeladmin, request, meetings):
    for meeting in meetings:
        meeting.reservations_limit = meeting.subject.default_reservations_limit
        meeting.save()


reset_default_reservations_limit.short_description = "Resetta limite predefinito di prenotazioni"


class MeetingResource(resources.ModelResource):
    class Meta:
        model = Activity
        fields = ('start_at', 'end_at', 'duration')


class MeetingAdmin(ImportExportModelAdmin):
    ordering = ('-start_at', 'subject__name')
    list_display = ('__str__', 'is_active', 'start_at', 'presences_count', 'reservations_limit')
    list_filter = ('activity__name', 'subject__name', 'is_active')
    actions = [delete_meeting, reset_default_reservations_limit, add_users_to_meetings]
    resource = MeetingResource


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Weekday)
admin.site.register(PresenceType)


class ApplicationResource(resources.ModelResource):
    user__full_name = Field(attribute='user__full_name', column_name='Cognome e Nome')
    user__classe = Field(attribute='user__classe', column_name='Classe')
    user__phone = Field(attribute='user__phone', column_name='Cellulare')
    subject__name = Field(attribute='subject__name', column_name='Materia')
    last_year_grade = Field(attribute='last_year_grade', column_name='Voto ultima pagella')
    weekdays = Field(attribute='weekdays', column_name='Giorni di disponibilità')
    asl_text = Field(attribute='asl_text', column_name='ASL')

    class Meta:
        model = Application
        fields = (
            'user__full_name', 'user__classe', 'user__phone', 'subject__name', 'last_year_grade',
            'weekdays', 'asl_text')
        export_order = (
            'user__full_name', 'user__classe', 'user__phone', 'subject__name', 'last_year_grade',
            'weekdays', 'asl_text')

    def dehydrate_weekdays(self, application):
        return application.implode_weekdays()

    def dehydrate_asl_text(self, application):
        if application.asl:
            return 'Sì'
        else:
            return 'No'


class ApplicationAdmin(ImportExportModelAdmin):
    ordering = ('-created_at',)
    list_display = ('__str__', 'subject', 'user', 'implode_weekdays', 'last_year_grade', 'asl')
    resource_class = ApplicationResource

    def get_export_filename(self, request, queryset, file_format):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % ('candidature',
                                 date_str,
                                 file_format.get_extension())
        return filename


admin.site.register(Application, ApplicationAdmin)


class RegistrationResource(resources.ModelResource):
    user__full_name = Field(attribute='user__full_name', column_name='Cognome e Nome')
    user__classe = Field(attribute='user__classe', column_name='Classe')
    user__email = Field(attribute='user__email', column_name='Email')
    user__phone = Field(attribute='user__phone', column_name='Cellulare')
    biologia_text = Field(attribute='biologia_text', column_name='Biologia')
    chimica_text = Field(attribute='chimica_text', column_name='Chimica')
    matematica_text = Field(attribute='matematica_text', column_name='Matematica')

    class Meta:
        model = Registration
        fields = (
            'user__full_name', 'user__classe', 'user__email', 'user__phone', 'biologia_text',
            'chimica_text',
            'matematica_text')
        export_order = (
            'user__full_name', 'user__classe', 'user__email', 'user__phone', 'biologia_text',
            'chimica_text',
            'matematica_text')

    def dehydrate_biologia_text(self, registration):
        if registration.biologia:
            return 'Sì'
        else:
            return 'No'

    def dehydrate_chimica_text(self, registration):
        if registration.chimica:
            return 'Sì'
        else:
            return 'No'

    def dehydrate_matematica_text(self, registration):
        if registration.matematica:
            return 'Sì'
        else:
            return 'No'


class RegistrationAdmin(ImportExportModelAdmin):
    ordering = ('-created_at',)
    resource_class = RegistrationResource

    def get_export_filename(self, file_format):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % ('iscrizioni',
                                 date_str,
                                 file_format.get_extension())
        return filename


admin.site.register(Registration, RegistrationAdmin)


class DefaultAssignedUserAdmin(ModelAdmin):
    ordering = ('-activity__id', 'subject__name', 'user__full_name')
    list_filter = ('activity__name', 'subject__name', 'group__name')


admin.site.register(DefaultAssignedUser, DefaultAssignedUserAdmin)
admin.site.register(MeetingsGenerationOption)
admin.site.register(ParticipationGroup)
