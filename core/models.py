from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video


class BlogCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=30, blank=True, default='bi bi-tag')

    class Meta:
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.CharField(max_length=250)
    content = models.TextField(max_length=250)
    image = models.ImageField(upload_to='blog/posts/', blank=True, null=True)
    # video = models.FileField(upload_to='blog/posts/videos/', blank=True, null=True)
    video = models.FileField(
        upload_to='blog/posts/videos/',
        blank=True,
        null=True,
        storage=VideoMediaCloudinaryStorage(),
        validators=[validate_video]
    )
    categories = models.ManyToManyField(BlogCategory, related_name='posts', blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:blog_detail', kwargs={'slug': self.slug})

    @property
    def has_distinct_title(self):
        title_text = (self.title or '').strip()
        first_line = (self.content or '').strip().splitlines()[0].strip() if (self.content or '').strip() else ''
        return bool(title_text and first_line and title_text.lower() != first_line.lower())

    def save(self, *args, **kwargs):
        if not self.title:
            first_line = self.content.strip().splitlines()[0] if self.content.strip() else ''
            self.title = (first_line[:80] or 'TREMHUB Update').strip()

        if not self.excerpt:
            excerpt_source = self.content.strip().replace('\n', ' ')
            self.excerpt = (excerpt_source[:260] or self.title).strip()

        if not self.slug:
            base_slug = slugify(self.title) or 'tremhub-update'
            slug_candidate = base_slug
            suffix = 1
            while BlogPost.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                suffix += 1
                slug_candidate = f'{base_slug}-{suffix}'
            self.slug = slug_candidate

        super().save(*args, **kwargs)


class BlogLike(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} on {self.post}'


class BlogCommentLike(models.Model):
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f'{self.user} liked comment {self.comment_id}'