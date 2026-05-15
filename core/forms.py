from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from .models import BlogPost, BlogComment


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['content', 'image', 'video', 'categories', 'is_featured']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': "What's happening?",
                'class': 'tweet-compose-input',
                'maxlength': 250,
                'data-maxlength': 250,
            }),
            'categories': forms.CheckboxSelectMultiple(),
            'image': forms.ClearableFileInput(attrs={
                'class': 'tweet-image-input',
                'accept': 'image/*',
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'tweet-video-input',
                'accept': 'video/*',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'tweet-featured-checkbox',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            'image',
            'video',
            'categories',
            HTML('<div class="form-check mb-3"><input type="checkbox" name="is_featured" id="is_featured" class="form-check-input" {% if form.is_featured.value %}checked{% endif %}><label for="is_featured" class="form-check-label">Feature this post as an insight</label></div>'),
            Submit('submit', 'Post', css_class='btn btn-trem mt-3 rounded-pill px-4'),
        )

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')

        if image and video:
            raise ValidationError('Please upload either one image or one video, not both.')

        if video:
            content_type = getattr(video, 'content_type', '') or ''
            if not content_type.startswith('video/'):
                raise ValidationError('Only video files are allowed for video uploads.')

            max_size = 30 * 1024 * 1024
            if video.size > max_size:
                raise ValidationError('Video size must be 30MB or less.')

        return cleaned_data


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a reply...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            Submit('submit', 'Reply', css_class='btn btn-trem btn-sm rounded-pill px-4'),
        )