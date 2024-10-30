from django.shortcuts import render, get_object_or_404
from .models import WikiPage


# Create your views here.

def page_list(request):
    """List all wiki pages."""
    pages = WikiPage.objects.all().order_by('title')
    return render(request, 'wiki/page_list.html', {'pages': pages})


def page_detail(request, slug):
    """Display a single wiki page."""
    page = get_object_or_404(WikiPage, slug=slug)
    
    # Get featured articles
    featured_articles = WikiPage.objects.filter(
        is_featured=True
    )
    
    # Get related articles
    related_articles = WikiPage.objects.filter(
        related_to=page
    ).order_by('title')
    
    context = {
        'page': page,
        'featured_articles': featured_articles,
        'related_articles': related_articles
    }
    
    return render(request, 'wiki/page_detail.html', context)


def page_history(request, slug):
    """View revision history of a wiki page."""
    page = get_object_or_404(WikiPage, slug=slug)
    revisions = page.revisions.all()
    context = {'page': page, 'revisions': revisions}
    return render(request, 'wiki/page_history.html', context)
