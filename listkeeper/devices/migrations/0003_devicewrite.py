# Generated by Django 3.1 on 2019-12-21 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_deviceread_rssi'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceWrite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(help_text='Type prefix, colon, hex value of tag (e.g. epc:f376ce13434a2b)', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writes', to='devices.Device')),
            ],
        ),
    ]
