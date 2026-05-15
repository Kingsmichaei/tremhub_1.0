from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='branch',
            field=models.CharField(
                choices=[
                    ('headquarters', 'TREM Headquarters'),
                    ('district_church', 'District Church'),
                    ('trem_ijesha', 'TREM Ijesha'),
                    ('lagos_zone_1', 'Lagos Zone 1'),
                    ('lagos_zone_2', 'Lagos Zone 2'),
                    ('lagos_zone_3', 'Lagos Zone 3'),
                    ('lagos_zone_4', 'Lagos Zone 4'),
                    ('lagos_zone_5', 'Lagos Zone 5'),
                    ('lagos_zone_6', 'Lagos Zone 6'),
                    ('lagos_zone_7', 'Lagos Zone 7'),
                    ('lagos_zone_8', 'Lagos Zone 8'),
                    ('lagos_zone_9', 'Lagos Zone 9'),
                    ('lagos_zone_10', 'Lagos Zone 10'),
                    ('lagos_zone_11', 'Lagos Zone 11'),
                    ('lagos_zone_12', 'Lagos Zone 12'),
                    ('lagos_zone_13', 'Lagos Zone 13'),
                    ('lagos_zone_14', 'Lagos Zone 14'),
                    ('south_south_zone_1', 'South-South Zone 1'),
                    ('south_south_zone_2', 'South-South Zone 2'),
                    ('south_south_zone_3', 'South-South Zone 3'),
                    ('south_east_zone_1', 'South-East Zone 1'),
                    ('south_east_zone_2', 'South-East Zone 2'),
                    ('south_east_zone_3', 'South-East Zone 3'),
                    ('south_west_zone_1', 'South-West Zone 1'),
                    ('south_west_zone_2', 'South-West Zone 2'),
                    ('south_west_zone_3', 'South-West Zone 3'),
                    ('northern_zone_1', 'Northern Zone 1'),
                    ('northern_zone_2', 'Northern Zone 2'),
                    ('other', 'Other Branch'),
                ],
                default='other',
                max_length=50,
            ),
            preserve_default=False,
        ),
    ]
