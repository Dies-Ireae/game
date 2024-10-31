from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from .models import WikiPage


# Create your views here.

def page_list(request):
    """Show index page if one exists, otherwise show list of pages."""
    try:
        index_page = WikiPage.objects.get(is_index=True)
        return page_detail(request, index_page.slug)
    except WikiPage.DoesNotExist:
        pages = WikiPage.objects.all().order_by('title')
        return render(request, 'wiki/page_list.html', {'pages': pages})


def page_detail(request, slug):
    """Display a single wiki page."""
    page = get_object_or_404(WikiPage, slug=slug)
    
    # Get featured articles - include current page if it's featured
    featured_articles = WikiPage.objects.filter(
        is_featured=True,
        published=True
    ).order_by('title')[:5]  # Remove .exclude(pk=page.pk)
    
    # Get related articles
    related_articles = page.related_to.all().order_by('title')
    
    context = {
        'page': page,
        'featured_articles': featured_articles,
        'related_articles': related_articles
    }
    
    return render(request, 'wiki/base_wiki.html', context)


def page_history(request, slug):
    """View revision history of a wiki page."""
    page = get_object_or_404(WikiPage, slug=slug)
    revisions = page.revisions.all()
    context = {'page': page, 'revisions': revisions}
    return render(request, 'wiki/page_history.html', context)


class WikiPageDetailView(DetailView):
    model = WikiPage
    template_name = 'wiki/page_detail.html'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured articles, ordered by featured_order (including current page)
        context['featured_articles'] = WikiPage.objects.filter(
            is_featured=True,
            published=True
        ).order_by('featured_order')
        
        if self.object:
            context['related_articles'] = self.object.related_to.filter(
                published=True
            )
        
        return context
