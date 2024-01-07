from django import template
from dostanaapp.models import *

register = template.Library()

@register.filter
def add_staff_status(user):
    if user.is_staff:
        return f"{user.username} &#10004;"
    return user.username

@register.filter(name='show_user_points')
def show_user_points(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user_profile = user.userprofile  # Assuming you have a OneToOneField named 'userprofile' in your User model
        
        if user_profile.scores:
            points_text = f"<span style='color: green;'> ({user_profile.scores})</span>"
        else:
            points_text = ""
        
        if user.is_superuser:
            crown = "👑"
            return f"{user.username} {crown}{points_text}"
        
        if user.is_staff:
            staff_icon = "&#10004;"
            return f"{user.username} {staff_icon} {points_text}"
        
        return f"{user.username}{points_text}"
    except User.DoesNotExist:
        return username
        
@register.filter(name='show_star_for_most_posts')
def show_star_for_most_posts(user):
    most_posts_user = User.objects.annotate(post_count=Count('post')).order_by('-post_count').first()
    if user == most_posts_user:
        return f'<span style="color: gold;">⭐</span> {user.username}'
    else:
        return user.username