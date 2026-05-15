from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import UserProfile
from businesses.models import Business


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to TREMHUB, {user.first_name}! Complete your profile below.')
            return redirect('accounts:edit_profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'accounts:profile'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out. God bless you!')
    return redirect('core:home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    businesses = Business.objects.filter(owner=request.user, is_active=True)
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'businesses': businesses,
    })


@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


def member_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    businesses = Business.objects.filter(owner=user, is_active=True)
    return render(request, 'accounts/member_detail.html', {
        'member': user,
        'profile': profile,
        'businesses': businesses,
    })


@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('core:home')
    return render(request, 'accounts/confirm_delete.html')


def members_directory(request):
    query = request.GET.get('q', '')
    branch = request.GET.get('branch', '')
    unit = request.GET.get('unit', '')

    profiles = UserProfile.objects.select_related('user').filter(user__is_active=True)

    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(occupation__icontains=query)
        )
    if branch:
        profiles = profiles.filter(branch=branch)
    if unit:
        profiles = profiles.filter(unit=unit)

    from .models import BRANCH_CHOICES, UNIT_CHOICES
    
    # For AJAX requests, return only the results partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('accounts/_members_results.html', {
            'profiles': profiles,
            'query': query,
            'selected_branch': branch,
            'selected_unit': unit,
        })
        from django.http import HttpResponse
        return HttpResponse(html)
    
    return render(request, 'accounts/members.html', {
        'profiles': profiles,
        'query': query,
        'selected_branch': branch,
        'selected_unit': unit,
        'branch_choices': BRANCH_CHOICES,
        'unit_choices': UNIT_CHOICES,
    })
