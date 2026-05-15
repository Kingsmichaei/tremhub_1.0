from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


CATEGORY_CHOICES = [
    ('food', 'Food & Restaurants'),
    ('fashion', 'Fashion & Clothing'),
    ('health', 'Health & Beauty'),
    ('tech', 'Technology & IT'),
    ('education', 'Education & Training'),
    ('construction', 'Construction & Real Estate'),
    ('finance', 'Finance & Investment'),
    ('transport', 'Transport & Logistics'),
    ('retail', 'Retail & Shopping'),
    ('hospitality', 'Hospitality & Events'),
    ('agriculture', 'Agriculture & Farming'),
    ('media', 'Media & Entertainment'),
    ('legal', 'Legal & Professional'),
    ('worship', 'Church & Religious'),
    ('other', 'Other'),
]


BRANCH_CHOICES = [
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

class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    description = models.TextField(max_length=1000)
    logo = models.ImageField(upload_to='businesses/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='businesses/banners/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True, max_length=300)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True, help_text='WhatsApp number with country code')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('businesses:detail', kwargs={'pk': self.pk})

    @property
    def category_display(self):
        return dict(CATEGORY_CHOICES).get(self.category, self.category)

    @property
    def branch_display(self):
        return dict(BRANCH_CHOICES).get(self.branch, self.branch)

    @property
    def whatsapp_link(self):
        if self.whatsapp:
            clean = ''.join(filter(str.isdigit, self.whatsapp))
            return f'https://wa.me/{clean}'
        return ''
