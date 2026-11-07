from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_products_new_arrival'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='header_scripts',
            field=models.TextField(blank=True, help_text='Added before &lt;/head&gt; on every page. Paste full tags, e.g. &lt;script&gt;...&lt;/script&gt; or &lt;meta ...&gt;.', null=True),
        ),
        migrations.AddField(
            model_name='settings',
            name='footer_scripts',
            field=models.TextField(blank=True, help_text='Added before &lt;/body&gt; on every page. Paste full tags, e.g. &lt;script&gt;...&lt;/script&gt;.', null=True),
        ),
    ]
