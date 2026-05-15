from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Business


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'category', 'branch', 'description', 'logo', 'banner',
                  'phone', 'email', 'website', 'address',
                  'instagram', 'twitter', 'facebook', 'whatsapp']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="text-trem fw-bold mb-3">Business Information</h6>'),
            Row(
                Column('name', css_class='col-md-6'),
                Column('category', css_class='col-md-3'),
                Column('branch', css_class='col-md-3'),
            ),
            'description',
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Images</h6>'),
            Row(
                Column('logo', css_class='col-md-6'),
                Column('banner', css_class='col-md-6'),
            ),
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Contact Details</h6>'),
            Row(
                Column('phone', css_class='col-md-4'),
                Column('email', css_class='col-md-4'),
                Column('whatsapp', css_class='col-md-4'),
            ),
            'website',
            'address',
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Social Media</h6>'),
            Row(
                Column('instagram', css_class='col-md-4'),
                Column('twitter', css_class='col-md-4'),
                Column('facebook', css_class='col-md-4'),
            ),
            Submit('submit', 'Save Business', css_class='btn btn-trem mt-3'),
        )
