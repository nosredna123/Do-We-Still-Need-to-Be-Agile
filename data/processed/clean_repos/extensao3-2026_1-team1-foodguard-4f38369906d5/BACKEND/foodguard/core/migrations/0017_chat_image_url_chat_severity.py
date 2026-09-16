from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_message_recommends_doctor'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='chat',
            name='severity',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
