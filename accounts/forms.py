from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'username',
            'email',
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Submit('submit', 'Create Account', css_class='btn btn-trem w-100 mt-2'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Sign In', css_class='btn btn-trem w-100 mt-2'),
        )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['photo', 'phone', 'bio', 'branch', 'unit', 'occupation',
                  'date_joined_church', 'instagram', 'twitter', 'facebook', 'linkedin']
        widgets = {
            'date_joined_church': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="text-trem fw-bold mb-3">Personal Information</h6>'),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            'bio',
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Church Details</h6>'),
            Row(
                Column('branch', css_class='col-md-6'),
                Column('unit', css_class='col-md-6'),
            ),
            Row(
                Column('occupation', css_class='col-md-6'),
            ),
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Profile Photo</h6>'),
            'photo',
            HTML('<h6 class="text-trem fw-bold mb-3 mt-3">Social Media</h6>'),
            Row(
                Column('instagram', css_class='col-md-6'),
                Column('twitter', css_class='col-md-6'),
            ),
            Row(
                Column('facebook', css_class='col-md-6'),
                Column('linkedin', css_class='col-md-6'),
            ),
            Submit('submit', 'Save Profile', css_class='btn btn-trem mt-3'),
        )
