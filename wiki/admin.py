from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import WikiPage, WikiRevision, FeaturedImage

# Register your models here.

class FeaturedImageInline(admin.StackedInline):
    model = FeaturedImage
    can_delete = True
    max_num = 1
    
    class Media:
        js = ('wiki/js/featured-image-component.js',)
        css = {
            'all': ('wiki/css/admin.css',)
        }
    
    def get_fields(self, request, obj=None):
        fields = ['image', 'banner', 'show_texture']
        return fields

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['image', 'banner']:
            formfield.widget.template_name = 'wiki/admin/image_input.html'
        return formfield

@admin.register(WikiPage)
class WikiPageAdmin(admin.ModelAdmin):
    """Admin interface for wiki pages."""
    
    list_display = (
        'title', 'creator', 'last_editor', 'created_at', 
        'updated_at', 'is_featured'
    )
    list_filter = ('created_at', 'updated_at', 'is_featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_featured')
        }),
        ('Content', {
            'fields': ('content', 'right_content'),
            'classes': ('wide',)
        }),
        ('Related Articles', {
            'fields': ('related_to',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creator', 'last_editor', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [FeaturedImageInline]

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'right_content':
            formfield.widget.attrs['placeholder'] = (
                'Optional content for the right sidebar. '
                'Leave empty to hide sidebar.'
            )
            # Make the text area shorter than the main content
            formfield.widget.attrs['rows'] = 10
        elif db_field.name == 'content':
            # Make the main content area larger
            formfield.widget.attrs['rows'] = 20
        return formfield

    def save_model(self, request, obj, form, change):
        """Override save_model to pass the current user to the model's save method."""
        obj.save(current_user=request.user)

    def save_related(self, request, form, formsets, change):
        """Override save_related to ensure related objects are saved after the main object."""
        super().save_related(request, form, formsets, change)
        # Update last_editor after related objects are saved
        form.instance.last_editor = request.user
        form.instance.save(current_user=request.user)


@admin.register(WikiRevision)
class WikiRevisionAdmin(admin.ModelAdmin):
    """Admin interface for wiki revisions."""
    
    list_display = ('page', 'editor', 'edited_at', 'comment')
    list_filter = ('edited_at', 'editor')
    search_fields = ('page__title', 'content', 'comment')
    readonly_fields = ('edited_at',)
    
    fieldsets = (
        (None, {
            'fields': ('page', 'content', 'comment')
        }),
        ('Metadata', {
            'fields': ('editor', 'edited_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FeaturedImage)
class FeaturedImageAdmin(admin.ModelAdmin):
    list_display = ('page', 'show_texture')
    list_filter = ('show_texture',)
