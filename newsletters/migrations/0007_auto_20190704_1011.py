# Generated by Django 2.2.3 on 2019-07-04 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsletters', '0006_auto_20170806_2035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'Entries'},
        ),
        migrations.AlterField(
            model_name='source',
            name='newsletter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='newsletters.Newsletter'),
        ),
    ]