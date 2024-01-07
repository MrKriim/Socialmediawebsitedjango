from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = 'hourly'
    priority = 0.9

    def items(self):
        return Post.objects.order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at
