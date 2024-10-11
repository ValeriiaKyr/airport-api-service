# Generated by Django 5.1.2 on 2024-10-11 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0003_alter_flight_airplane'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='row',
            new_name='rows',
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('flight', 'rows', 'seat')},
        ),
    ]
