from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_settings_youtube'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='new_arrival',
            field=models.BooleanField(default=False, verbose_name='Show in New Arrivals'),
        ),
    ]
