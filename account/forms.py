from django import forms

from account.models import User


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=35, label='Nome studente', help_text='Scrivilo esattamente come riportato '
                                                                                 'sui dati ufficiali scolastici, '
                                                                                 'compreso perciò eventuali secondi '
                                                                                 'nomi.')
    last_name = forms.CharField(max_length=35, label='Cognome studente',
                                help_text='Scrivilo esattamente come riportato '
                                          'sui dati ufficiali scolastici.')
    classe = forms.CharField(max_length=20, label='Classe attuale',
                             help_text='Esempio: <em>5DL</em> oppure <em>1AC</em>')
    email = forms.EmailField(max_length=255, label='Email studente', help_text="L'email studente deve essere diversa "
                                                                               "da quella del genitore.")
    phone = forms.CharField(max_length=20, label='Cellulare studente',
                            help_text='Apponi sempre +39 prima del numero', initial='+39')
    password = forms.CharField(widget=forms.PasswordInput())
    '''privacy_policy_consent = forms.BooleanField(label='Acconsento al trattamento dei miei dati personali come indicato'
                                                      ' nella <a href="#" '
                                                      'class="iubenda-nostyle no-brand iubenda-embed" title="Privacy '
                                                      'Policy ">Privacy Policy</a>')'''


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone', 'classe']
