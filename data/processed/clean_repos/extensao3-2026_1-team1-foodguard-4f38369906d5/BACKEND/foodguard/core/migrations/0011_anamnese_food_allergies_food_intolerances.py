# Generated for sign-up integration (campos de alergia/intolerância na anamnese)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_message_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='anamnese',
            name='food_allergies',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Possui alergia a algum alimento? Se sim, qual?'),
        ),
        migrations.AddField(
            model_name='anamnese',
            name='food_intolerances',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Tem intolerância a algum alimento? Se sim, qual?'),
        ),
    ]
