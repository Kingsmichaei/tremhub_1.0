from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_blogpost_video_alter_blogpost_content_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.blogcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment_likes', to='auth.user')),
            ],
            options={
                'unique_together': {('comment', 'user')},
            },
        ),
    ]
