from django.utils import timezone
from account.models import UserConsent, User

file = "Anguilano,Davide,1DL;Barella,Andrea,1EL;Baronio,Giorgia,1AL;Camera,Flaminia,1AL;Candioli,Margherita,1CL;Castriziani,Sofia,1CL;Cattaneo,Giorgia,1AC;Dal Buono,Gaia,1DL;Damiani,Irene,1AC;De Angeli,Laura,1GL;De Angelis,Sveva,1GL;De Cristofaris,Francesca,1AC;De Grandis,Leonardo,1EC;Del Monte,Emma,1BC;Della Penna,Virginia,1AL;D'Erme,Nilo,1CC;Dessì,Claudia,1BL;Di Genova,Giulia,1DL;Di Marco,Tommaso,1EL;Farris,Lara,1EL;Ferrara,Flaminia,1CC;Fiasconaro,Irene,1AL;Gentili,Margherita,1BC;Guerra,Valentina,1EC;Macci,Alice,1BL;Mancuso,Letizia,1AL;Mancuso,Francesco,1CL;Manetti,Francesco,1CC;Mellone,Francesca,1AC;Mohamed El Nagar,Mena,1EL;Morana,Sara,1AL;Moreltejada,Oliver,1FL;Muti,Giulia,1CL;Olivieri,Lavinia,1GL;Onorati,Daniele,1AL;Palmiero,Agnese,1CC;Pandolfini,Giulia,1DL;Parini,Martina,1FL;Persico,Lorenzo,1CC;Petrossi,Elisa,1BC;Pieretto,Ilaria,1DL;Pischedda,Elenoire,1CL;Poggi,Beatrice,1CC;Ranalli,Giorgia,1EC;Repetto,Chloe,1AC;Rizzi,Giuseppe,1BL;Scagnetto,Giulia,1AL;Shlash,Asmaa,1AL;Soda,Federico,1CC;Sorrentino,Giovanni,1CC;Tidei,Davide,1EC;Tomasicchio,Michela,1CL;Vitello,Ludovica,1AL"

users = file.split(';')

for user in users:
    last_name, first_name, classe = user.split(',')

    if User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).count() == 0:
        user = User.objects.create_user(first_name + classe + '@example.com', None, first_name=first_name, last_name=last_name,
                                        phone=None, birth_date=None, classe=classe)
        UserConsent.objects.create(user=user, privacy_policy_consent=timezone.now())
        user.groups.add(1)
