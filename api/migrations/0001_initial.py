# Generated by Django 3.2.7 on 2021-09-08 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('identifier', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=80)),
                ('start_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('end_date', models.DateTimeField()),
                ('requirement', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('identifier', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=80)),
                ('description', models.TextField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductStep',
            fields=[
                ('identifier', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=80)),
                ('start_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('end_date', models.DateTimeField()),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.product')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project'),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('identifier', models.AutoField(primary_key=True, serialize=False)),
                ('initial', models.BooleanField(default=False)),
                ('preview', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.node')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.product')),
                ('product_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.productstep')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('identifier', models.AutoField(primary_key=True, serialize=False)),
                ('file_name', models.CharField(default='', max_length=80)),
                ('file_attach', models.FileField(upload_to='uploads/')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.product')),
                ('product_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.productstep')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
        ),
    ]
