# Generated by Django 5.2.4 on 2025-07-19 06:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('monthly_salary', models.IntegerField()),
                ('approved_limit', models.IntegerField()),
                ('current_debt', models.IntegerField(default=0)),
                ('age', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('loan_id', models.AutoField(primary_key=True, serialize=False)),
                ('loan_amount', models.FloatField()),
                ('tenure', models.IntegerField()),
                ('interest_rate', models.FloatField()),
                ('monthly_repayment', models.FloatField()),
                ('emis_paid_on_time', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creditApprovalApp.customer')),
            ],
        ),
    ]
