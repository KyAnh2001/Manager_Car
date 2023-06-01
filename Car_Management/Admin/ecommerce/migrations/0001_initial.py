# Generated by Django 4.2 on 2023-05-04 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=96)),
                ('phone', models.CharField(max_length=13)),
                ('email', models.EmailField(max_length=96)),
                ('address', models.CharField(max_length=500)),
                ('rating', models.PositiveSmallIntegerField(choices=[(0, 'Select'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('wallet_balance', models.IntegerField()),
                ('joining_date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
