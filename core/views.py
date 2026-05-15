from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from django.template.loader import render_to_string
from businesses.models import Business
from accounts.models import UserProfile
from .models import BlogPost, BlogLike, BlogComment, BlogCommentLike
from .forms import BlogPostForm, BlogCommentForm


def _get_blog_posts(user, tab='for_you', hidden_slugs=None):
    """Helper function to get blog posts based on tab filter.
    
    Args:
        user: Request user object
        tab: 'for_you' (global feed) or 'my_blog' (user's posts only)
        hidden_slugs: List of post slugs to exclude (user-hidden posts)
    
    Returns:
        Tuple of (featured_posts, posts)
    """
    if hidden_slugs is None:
        hidden_slugs = []
    
    author_reply_subquery = BlogComment.objects.filter(
        post=OuterRef('pk'),
        author=OuterRef('author'),
    ).order_by('-created_at')
    
    base_filter = {'is_published': True}
    exclude_filter = {'slug__in': hidden_slugs}
    annotate_dict = {
        'author_reply_id': Subquery(author_reply_subquery.values('id')[:1]),
        'author_reply_content': Subquery(author_reply_subquery.values('content')[:1]),
        'author_reply_created_at': Subquery(author_reply_subquery.values('created_at')[:1]),
    }
    
    if tab == 'my_blog':
        # Show only user's posts
        if not user.is_authenticated:
            return [], []
        posts = BlogPost.objects.filter(**base_filter, author=user).exclude(**exclude_filter).annotate(**annotate_dict).select_related('author', 'author__profile').order_by('-created_at')
        return [], posts
    else:  # 'for_you'
        # Show all posts, featured first
        featured_posts = BlogPost.objects.filter(**base_filter, is_featured=True).exclude(**exclude_filter).annotate(**annotate_dict).select_related('author', 'author__profile').order_by('-created_at')
        posts = BlogPost.objects.filter(**base_filter, is_featured=False).exclude(**exclude_filter).annotate(**annotate_dict).select_related('author', 'author__profile').order_by('-created_at')
        return featured_posts, posts


def home(request):
    featured_businesses = Business.objects.filter(is_active=True, is_featured=True)[:6]
    recent_businesses = Business.objects.filter(is_active=True)[:8]
    member_count = UserProfile.objects.count()
    business_count = Business.objects.filter(is_active=True).count()
    return render(request, 'core/home.html', {
        'featured_businesses': featured_businesses,
        'recent_businesses': recent_businesses,
        'member_count': member_count,
        'business_count': business_count,
    })


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')


def cookie_policy(request):
    return render(request, 'core/cookie_policy.html')


def accessibility_statement(request):
    return render(request, 'core/accessibility_statement.html')


def blog(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post successful!')
            return redirect('core:blog')
    else:
        form = BlogPostForm()

    hidden_post_slugs = request.session.get('hidden_post_slugs', [])
    tab = request.GET.get('tab', 'for_you')
    
    # Validate tab parameter
    if tab not in ['for_you', 'my_blog']:
        tab = 'for_you'
    
    # Redirect to 'for_you' if accessing 'my_blog' without authentication
    if tab == 'my_blog' and not request.user.is_authenticated:
        tab = 'for_you'
    
    featured_posts, posts = _get_blog_posts(request.user, tab=tab, hidden_slugs=hidden_post_slugs)
    
    liked_post_ids = set()
    if request.user.is_authenticated:
        all_posts = list(featured_posts) + list(posts)
        liked_post_ids = set(
            BlogLike.objects.filter(user=request.user, post__in=all_posts).values_list('post_id', flat=True)
        )
    return render(request, 'blog/list.html', {
        'form': form,
        'featured_posts': featured_posts,
        'posts': posts,
        'liked_post_ids': liked_post_ids,
        'current_tab': tab,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost.objects.select_related('author', 'author__profile'), slug=slug, is_published=True)
    post.view_count += 1
    post.save(update_fields=['view_count'])
    
    comments = post.comments.select_related('author', 'author__profile').prefetch_related('likes')
    liked = False
    liked_comment_ids = set()
    same_author_replies = comments.filter(author=post.author).exists()
    if request.user.is_authenticated:
        liked = post.likes.filter(user=request.user).exists()
        liked_comment_ids = set(
            BlogCommentLike.objects.filter(user=request.user, comment__in=comments).values_list('comment_id', flat=True)
        )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'author_name': comment.author.get_full_name() or comment.author.username,
                        'author_username': comment.author.username,
                        'author_photo': comment.author.profile.photo.url if comment.author.profile.photo else '',
                        'created_at': comment.created_at.isoformat(),
                    },
                    'comment_count': post.comments.count(),
                })
            messages.success(request, 'Reply posted!')
            return redirect(post)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': False,
                'errors': form.errors.get_json_data(),
            }, status=400)
    else:
        form = BlogCommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form,
        'liked': liked,
        'like_count': post.likes.count(),
        'comment_count': comments.count(),
        'liked_comment_ids': liked_comment_ids,
        'same_author_replies': same_author_replies,
    })


@require_POST
def blog_posts_tab(request):
    """AJAX endpoint to fetch posts for a specific tab.
    
    Supports tab switching between 'for_you' and 'my_blog' without page reload.
    """
    tab = request.POST.get('tab', 'for_you')
    
    if tab not in ['for_you', 'my_blog']:
        return JsonResponse({'ok': False, 'error': 'Invalid tab'}, status=400)
    
    # Check authentication for my_blog
    if tab == 'my_blog' and not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Authentication required'}, status=403)
    
    hidden_post_slugs = request.session.get('hidden_post_slugs', [])
    featured_posts, posts = _get_blog_posts(request.user, tab=tab, hidden_slugs=hidden_post_slugs)
    
    # Get liked posts
    all_posts = list(featured_posts) + list(posts)
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            BlogLike.objects.filter(user=request.user, post__in=all_posts).values_list('post_id', flat=True)
        )
    
    # Render posts HTML
    posts_html = render_to_string('blog/_posts_list.html', {
        'posts': posts,
        'featured_posts': featured_posts,
        'liked_post_ids': liked_post_ids,
        'user': request.user,
        'request': request,
        'current_tab': tab,
    })
    
    return JsonResponse({
        'ok': True,
        'tab': tab,
        'posts_html': posts_html,
        'post_count': len(all_posts),
    })


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post successful!')
            return redirect(post)
    else:
        form = BlogPostForm()

    return render(request, 'blog/form.html', {
        'form': form,
        'title': 'Add Blog Post',
    })


@login_required
@require_POST
def blog_like_toggle(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    like = BlogLike.objects.filter(post=post, user=request.user)
    liked = False
    if like.exists():
        like.delete()
    else:
        BlogLike.objects.create(post=post, user=request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'liked': liked,
            'like_count': post.likes.count(),
        })

    return redirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))


@login_required
@require_POST
def blog_delete(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    post.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'deleted': True,
            'slug': slug,
            'redirect_url': '/blog/',
        })
    messages.success(request, 'Your post was deleted.')
    return redirect('core:blog')


@login_required
@require_POST
def blog_hide_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    if post.author_id == request.user.id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': False,
                'error': 'own_post',
            }, status=400)
        messages.error(request, 'You cannot hide your own post.')
        return redirect(request.META.get('HTTP_REFERER', 'core:blog'))

    hidden_post_slugs = request.session.get('hidden_post_slugs', [])
    if slug not in hidden_post_slugs:
        hidden_post_slugs.append(slug)
        request.session['hidden_post_slugs'] = hidden_post_slugs

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'hidden': True,
            'slug': slug,
        })

    messages.success(request, 'Post hidden from your feed.')
    return redirect(request.META.get('HTTP_REFERER', 'core:blog'))


@login_required
@require_POST
def blog_report_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    if post.author_id == request.user.id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': False,
                'error': 'own_post',
            }, status=400)
        messages.error(request, 'You cannot report your own post.')
        return redirect(request.META.get('HTTP_REFERER', 'core:blog'))

    reported_post_slugs = request.session.get('reported_post_slugs', [])
    if slug not in reported_post_slugs:
        reported_post_slugs.append(slug)
        request.session['reported_post_slugs'] = reported_post_slugs

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'reported': True,
            'slug': slug,
            'message': 'Thanks. Your report has been submitted.',
        })

    messages.success(request, 'Thanks. Your report has been submitted.')
    return redirect(request.META.get('HTTP_REFERER', 'core:blog'))


@login_required
@require_POST
def blog_comment_delete(request, pk):
    comment = get_object_or_404(BlogComment, pk=pk)
    if comment.author != request.user and comment.post.author != request.user:
        return redirect(comment.post)

    post_url = comment.post.get_absolute_url()
    post = comment.post
    comment.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'deleted': True,
            'comment_id': pk,
            'comment_count': post.comments.count(),
        })
    messages.success(request, 'Reply deleted.')
    return redirect(post_url)


@login_required
@require_POST
def blog_comment_like_toggle(request, pk):
    comment = get_object_or_404(BlogComment.objects.select_related('post'), pk=pk)
    like = BlogCommentLike.objects.filter(comment=comment, user=request.user)
    liked = False
    if like.exists():
        like.delete()
    else:
        BlogCommentLike.objects.create(comment=comment, user=request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'liked': liked,
            'like_count': comment.likes.count(),
        })

    return redirect(request.META.get('HTTP_REFERER', comment.post.get_absolute_url()))
