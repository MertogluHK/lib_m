# Generated migration to make pickup_date required
from django.db import migrations, models
from datetime import date


def set_default_pickup_date(apps, schema_editor):
    """Set default pickup_date for existing NULL entries"""
    Reservation = apps.get_model('reservations', 'Reservation')
    today = date.today()
    Reservation.objects.filter(pickup_date__isnull=True).update(pickup_date=today)


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_reservation_pickup_date'),
    ]

    operations = [
        migrations.RunPython(set_default_pickup_date),
        migrations.AlterField(
            model_name='reservation',
            name='pickup_date',
            field=models.DateField(),
        ),
    ]
