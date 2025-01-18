from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from .models import WikiPage
from django.db.models import Q, F
from django.db.models.functions import Length
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)


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


def search_wiki(request):
    """Search wiki pages by title and content with basic relevance ranking."""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        logger.debug(f"Search query: {query}")
        
        # Split query into words for better matching
        query_words = query.split()
        
        # Base queryset
        base_qs = WikiPage.objects.filter(published=True)
        
        # Create Q objects for each word
        title_q = Q()
        content_q = Q()
        for word in query_words:
            title_q |= Q(title__icontains=word)
            content_q |= Q(content__icontains=word)
        
        # Get all matching results
        results = base_qs.filter(title_q | content_q).distinct()
        
        # Annotate with ranking factors
        for result in results:
            # Calculate ranking score
            score = 0
            
            # Exact title match gets highest score
            if result.title.lower() == query.lower():
                score += 100
            
            # Title contains full query
            elif query.lower() in result.title.lower():
                score += 50
            
            # Count word matches in title
            title_word_matches = sum(
                1 for word in query_words 
                if word.lower() in result.title.lower()
            )
            score += title_word_matches * 10
            
            # Count word matches in content
            content_word_matches = sum(
                1 for word in query_words 
                if word.lower() in result.content.lower()
            )
            score += content_word_matches * 2
            
            # Store score
            result.search_rank = score
        
        # Sort results by score
        results = sorted(
            results,
            key=lambda x: (-x.search_rank, x.title.lower())
        )
        
        logger.debug(f"Found {len(results)} results")
        
        # Pagination
        paginator = Paginator(results, 10)
        page = request.GET.get('page')
        results = paginator.get_page(page)
    
    # Get featured articles for navigation
    featured_articles = WikiPage.objects.filter(
        is_featured=True,
        published=True
    ).order_by('featured_order')
    
    context = {
        'query': query,
        'results': results,
        'featured_articles': featured_articles,
        'search_performed': bool(query)
    }
    
    logger.debug(f"Search context: {context}")
    
    return render(request, 'wiki/search_results.html', context)
