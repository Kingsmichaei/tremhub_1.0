from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


BRANCH_CHOICES = [
    ('', 'Select Branch'),
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
]

UNIT_CHOICES = [
    ('', 'Select Unit'),
    ('children', "Children's Ministry"),
    ('youth', 'NextGen'),
    ('women', "Young Women's Ministry"),
    ('men', "Young Men's Ministry"),
    ('women', "Christian Women's Ministry"),
    ('men', "Christian Men's Ministry"),
    ('general', 'General Member'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, blank=True)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    date_joined_church = models.DateField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse('accounts:member_detail', kwargs={'pk': self.user.pk})

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def branch_display(self):
        return dict(BRANCH_CHOICES).get(self.branch, self.branch)

    @property
    def unit_display(self):
        return dict(UNIT_CHOICES).get(self.unit, self.unit)
