from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Business, CATEGORY_CHOICES, BRANCH_CHOICES
from .forms import BusinessForm


def business_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    branch = request.GET.get('branch', '')

    businesses = Business.objects.filter(is_active=True).select_related('owner', 'owner__profile')

    if query:
        businesses = businesses.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query)
        )
    if category:
        businesses = businesses.filter(category=category)
    if branch:
        businesses = businesses.filter(branch=branch)

    # For AJAX requests, return only the results partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string('businesses/_results.html', {
            'businesses': businesses,
            'query': query,
            'selected_category': category,
            'selected_branch': branch,
        })
        return HttpResponse(html)

    return render(request, 'businesses/list.html', {
        'businesses': businesses,
        'query': query,
        'selected_category': category,
        'selected_branch': branch,
        'categories': CATEGORY_CHOICES,
        'branch_choices': BRANCH_CHOICES,
    })


def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk, is_active=True)
    related = Business.objects.filter(
        category=business.category, is_active=True
    ).exclude(pk=pk)[:3]
    return render(request, 'businesses/detail.html', {
        'business': business,
        'related': related,
    })


@login_required
def business_create(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            messages.success(request, f'"{business.name}" has been listed successfully!')
            return redirect('businesses:detail', pk=business.pk)
    else:
        form = BusinessForm()
    return render(request, 'businesses/form.html', {'form': form, 'title': 'Add Business'})


@login_required
def business_edit(request, pk):
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, 'Business updated successfully!')
            return redirect('businesses:detail', pk=business.pk)
    else:
        form = BusinessForm(instance=business)
    return render(request, 'businesses/form.html', {'form': form, 'title': 'Edit Business', 'business': business})


@login_required
def business_delete(request, pk):
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = business.name
        business.delete()
        messages.success(request, f'"{name}" has been removed.')
        return redirect('accounts:profile')
    return render(request, 'businesses/confirm_delete.html', {'business': business})
