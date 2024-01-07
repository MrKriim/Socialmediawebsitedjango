from django import template
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from django.db.models import Count, Sum
from django.contrib.auth.models import User 
from django.utils import timezone
from dostanaapp.models import UserActivity
from django.template.defaultfilters import timesince
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='user_info')
def user_info(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user_profile = user.userprofile if hasattr(user, 'userprofile') else None

        crown = "👑" if user.is_superuser else ""
        checkmark = '<img style="width:48px; height:32px;" src="https://dostana.biz/media/rewards/finalverified.png" alt="Verified">' if user.is_staff else ""

        # Get the top 3 users based on post count
        top_users_post_count = User.objects.annotate(post_count=Count('post')).order_by('-post_count')[:7]

        # Get the top 3 users based on scores
        top_users_scores = User.objects.annotate(scores=Sum('userprofile__scores')).order_by('-scores')[:10]

        star = ""  # Initialize star emoji
        for i, top_user in enumerate(top_users_post_count):
            if user == top_user:
                star = '<img style="width:36px; height:36px;" src="https://dostana.biz/media/rewards/stargif3.gif" alt="GIF">'
                break

        for i, top_user in enumerate(top_users_scores):
            if user == top_user:
                if i == 0:
                    star += " 🥇"  # Gold medal for 1st scorer
                elif i == 1:
                    star += " 🥈"  # Silver medal for 2nd scorer
                elif i == 2:
                    star += " 🥉"  # Bronze medal for 3rd scorer
                elif i <= 10:
                    star += " 🌟"  # Star for positions 4 to 7
                break

        points_text = ""
        if user_profile and user_profile.scores:
            points_text = f'<span style="color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); animation: bounce 1s ease infinite;">({user_profile.scores})</span>'

        try:
            user_activity = UserActivity.objects.get(user=user)
            last_seen = timesince(user_activity.last_active)
        except UserActivity.DoesNotExist:
            last_seen = "N/A"

        last_seen_html = f'<br><span style="font-size: 10px;">Last Seen: {last_seen} ago</span>'

        # Add the PUBG badge if the user's city is "Pubg"
        pubg_badge = '<img src="https://dostana.biz/media/rewards/pubg.png" alt="PUBG Badge" style="width: 48px; height: 48px; vertical-align: middle;">' if user_profile and user_profile.city == "Pubg" else ""

        # Add the Star badge if the user's city is "Star"
        star_badge = '<img src="https://dostana.biz/media/custom_emojis/customstar.png" alt="Star Badge" style="width: 32px; height: 32px; vertical-align: middle;">' if user_profile and user_profile.city == "Star" else ""

        # Add the Freefire badge if the user's city is "Freefire"
        freefire_badge = '<img src="https://dostana.biz/media/rewards/freefire.png" alt="Freefire Badge" style="width: 48px; height: 48px; margin-left:2px; vertical-align: middle;">' if user_profile and user_profile.city == "Freefire" else ""

        return f"{user.username} {points_text}{crown}{checkmark} <span style='color: red;'>{star}</span>{last_seen_html}{pubg_badge}{star_badge} {freefire_badge}"
    except User.DoesNotExist:
        return username




@register.filter(name='render_custom_emoji')
def render_custom_emoji(value):
    emoji_mapping = {
        '.a1': '<img src="/media/custom_emojis/a1.png" alt=":a1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.a2': '<img src="/media/custom_emojis/a2.png" alt=":a2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.a3': '<img src="/media/custom_emojis/a3.png" alt=":a3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.a4': '<img src="/media/custom_emojis/a4.png" alt=":a4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.a5': '<img src="/media/custom_emojis/a5.png" alt=":a5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
       '.a6': '<img src="/media/custom_emojis/a6.png" alt=":a6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.a7': '<img src="/media/custom_emojis/a7.png" alt=":a7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.a8': '<img src="/media/custom_emojis/a8.png" alt=":a8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b1': '<img src="/media/custom_emojis/b1.png" alt=":b1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b2': '<img src="/media/custom_emojis/b2.png" alt=":b2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b3': '<img src="/media/custom_emojis/b3.png" alt=":b3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b4': '<img src="/media/custom_emojis/b4.png" alt=":b4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b5': '<img src="/media/custom_emojis/b5.png" alt=":b5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b6': '<img src="/media/custom_emojis/b6.png" alt=":b6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.b7': '<img src="/media/custom_emojis/b7.png" alt=":b7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.b8': '<img src="/media/custom_emojis/b8.png" alt=":b8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.c1': '<img src="/media/custom_emojis/c1.png" alt=":c1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.c2': '<img src="/media/custom_emojis/c2.png" alt=":c2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.c3': '<img src="/media/custom_emojis/c3.png" alt=":c3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.c4': '<img src="/media/custom_emojis/c4.png" alt=":c4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.c5': '<img src="/media/custom_emojis/c5.png" alt=":c5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.c6': '<img src="/media/custom_emojis/c6.png" alt=":c6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.c7': '<img src="/media/custom_emojis/c7.png" alt=":c7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.c8': '<img src="/media/custom_emojis/c8.png" alt=":c8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.d1': '<img src="/media/custom_emojis/d1.png" alt=":d1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
       '.d2': '<img src="/media/custom_emojis/d2.png" alt=":d2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
       
        '.d3': '<img src="/media/custom_emojis/d3.png" alt=":d3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.d4': '<img src="/media/custom_emojis/d4.png" alt=":d4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.d5': '<img src="/media/custom_emojis/d5.png" alt=":d5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.d6': '<img src="/media/custom_emojis/d6.png" alt=":d6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.d7': '<img src="/media/custom_emojis/d7.png" alt=":d7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.d8': '<img src="/media/custom_emojis/d8.png" alt=":d8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e1': '<img src="/media/custom_emojis/e1.png" alt=":e1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e2': '<img src="/media/custom_emojis/e2.png" alt=":e2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e3': '<img src="/media/custom_emojis/e3.png" alt=":e3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e4': '<img src="/media/custom_emojis/e4.png" alt=":e4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e5': '<img src="/media/custom_emojis/e5.png" alt=":e5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e6': '<img src="/media/custom_emojis/e6.png" alt=":e6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e7': '<img src="/media/custom_emojis/e7.png" alt=":e7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.e8': '<img src="/media/custom_emojis/e8.png" alt=":e8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f1': '<img src="/media/custom_emojis/f1.png" alt=":f1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f2': '<img src="/media/custom_emojis/f2.png" alt=":f2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f3': '<img src="/media/custom_emojis/f3.png" alt=":f3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f4': '<img src="/media/custom_emojis/f4.png" alt=":f4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f5': '<img src="/media/custom_emojis/f5.png" alt=":f5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f6': '<img src="/media/custom_emojis/f6.png" alt=":f6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f7': '<img src="/media/custom_emojis/f7.png" alt=":f7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.f8': '<img src="/media/custom_emojis/f8.png" alt=":f8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g1': '<img src="/media/custom_emojis/g1.png" alt=":g1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g2': '<img src="/media/custom_emojis/g2.png" alt=":g2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g3': '<img src="/media/custom_emojis/g3.png" alt=":g3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g4': '<img src="/media/custom_emojis/g4.png" alt=":g4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g5': '<img src="/media/custom_emojis/g5.png" alt=":g5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g6': '<img src="/media/custom_emojis/g6.png" alt=":g6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g7': '<img src="/media/custom_emojis/g7.png" alt=":g7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.g8': '<img src="/media/custom_emojis/g8.png" alt=":g8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
        
        '.h1': '<img src="/media/custom_emojis/h1.png" alt=":h1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h2': '<img src="/media/custom_emojis/h2.png" alt=":h2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h3': '<img src="/media/custom_emojis/h3.png" alt=":h3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h4': '<img src="/media/custom_emojis/h4.png" alt=":h4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h5': '<img src="/media/custom_emojis/h5.png" alt=":h5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h6': '<img src="/media/custom_emojis/h6.png" alt=":h6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h7': '<img src="/media/custom_emojis/h7.png" alt=":h7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.h8': '<img src="/media/custom_emojis/h8.png" alt=":h8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',

'.i1': '<img src="/media/custom_emojis/i1.png" alt=":i1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i2': '<img src="/media/custom_emojis/i2.png" alt=":i2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i3': '<img src="/media/custom_emojis/i3.png" alt=":i3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i4': '<img src="/media/custom_emojis/i4.png" alt=":i4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i5': '<img src="/media/custom_emojis/i5.png" alt=":i5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i6': '<img src="/media/custom_emojis/i6.png" alt=":i6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i7': '<img src="/media/custom_emojis/i7.png" alt=":i7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.i8': '<img src="/media/custom_emojis/i8.png" alt=":i8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',

'.j1': '<img src="/media/custom_emojis/j1.png" alt=":j1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j2': '<img src="/media/custom_emojis/j2.png" alt=":j2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j3': '<img src="/media/custom_emojis/j3.png" alt=":j3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j4': '<img src="/media/custom_emojis/j4.png" alt=":j4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j5': '<img src="/media/custom_emojis/j5.png" alt=":j5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j6': '<img src="/media/custom_emojis/j6.png" alt=":j6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j7': '<img src="/media/custom_emojis/j7.png" alt=":j7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.j8': '<img src="/media/custom_emojis/j8.png" alt=":j8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',

'.k1': '<img src="/media/custom_emojis/k1.png" alt=":k1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k2': '<img src="/media/custom_emojis/k2.png" alt=":k2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k3': '<img src="/media/custom_emojis/k3.png" alt=":k3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k4': '<img src="/media/custom_emojis/k4.png" alt=":k4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k5': '<img src="/media/custom_emojis/k5.png" alt=":k5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k6': '<img src="/media/custom_emojis/k6.png" alt=":k6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k7': '<img src="/media/custom_emojis/k7.png" alt=":k7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.k8': '<img src="/media/custom_emojis/k8.png" alt=":k8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l1': '<img src="/media/custom_emojis/l1.png" alt=":l1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l2': '<img src="/media/custom_emojis/l2.png" alt=":l2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l3': '<img src="/media/custom_emojis/l3.png" alt=":l3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l4': '<img src="/media/custom_emojis/l4.png" alt=":l4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l5': '<img src="/media/custom_emojis/l5.png" alt=":l5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l6': '<img src="/media/custom_emojis/l6.png" alt=":l6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l7': '<img src="/media/custom_emojis/l7.png" alt=":l7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.l8': '<img src="/media/custom_emojis/l8.png" alt=":l8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m1': '<img src="/media/custom_emojis/m1.png" alt=":m1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m2': '<img src="/media/custom_emojis/m2.png" alt=":m2" class "custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m3': '<img src="/media/custom_emojis/m3.png" alt=":m3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m4': '<img src="/media/custom_emojis/m4.png" alt=":m4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m5': '<img src="/media/custom_emojis/m5.png" alt=":m5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m6': '<img src="/media/custom_emojis/m6.png" alt=":m6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m7': '<img src="/media/custom_emojis/m7.png" alt=":m7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.m8': '<img src="/media/custom_emojis/m8.png" alt=":m8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n1': '<img src="/media/custom_emojis/n1.png" alt=":n1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n2': '<img src="/media/custom_emojis/n2.png" alt=":n2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n3': '<img src="/media/custom_emojis/n3.png" alt=":n3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n4': '<img src="/media/custom_emojis/n4.png" alt=":n4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n5': '<img src="/media/custom_emojis/n5.png" alt=":n5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n6': '<img src="/media/custom_emojis/n6.png" alt=":n6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n7': '<img src="/media/custom_emojis/n7.png" alt=":n7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.n8': '<img src="/media/custom_emojis/n8.png" alt=":n8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o1': '<img src="/media/custom_emojis/o1.png" alt=":o1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o2': '<img src="/media/custom_emojis/o2.png" alt=":o2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o3': '<img src="/media/custom_emojis/o3.png" alt=":o3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o4': '<img src="/media/custom_emojis/o4.png" alt=":o4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o5': '<img src="/media/custom_emojis/o5.png" alt=":o5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o6': '<img src="/media/custom_emojis/o6.png" alt=":o6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o7': '<img src="/media/custom_emojis/o7.png" alt=":o7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.o8': '<img src="/media/custom_emojis/o8.png" alt=":o8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p1': '<img src="/media/custom_emojis/p1.png" alt=":p1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p2': '<img src="/media/custom_emojis/p2.png" alt=":p2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p3': '<img src="/media/custom_emojis/p3.png" alt=":p3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p4': '<img src="/media/custom_emojis/p4.png" alt=":p4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p5': '<img src="/media/custom_emojis/p5.png" alt=":p5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p6': '<img src="/media/custom_emojis/p6.png" alt=":p6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p7': '<img src="/media/custom_emojis/p7.png" alt=":p7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.p8': '<img src="/media/custom_emojis/p8.png" alt=":p8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q1': '<img src="/media/custom_emojis/q1.png" alt=":q1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q2': '<img src="/media/custom_emojis/q2.png" alt=":q2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q3': '<img src="/media/custom_emojis/q3.png" alt=":q3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q4': '<img src="/media/custom_emojis/q4.png" alt=":q4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q5': '<img src="/media/custom_emojis/q5.png" alt=":q5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q6': '<img src="/media/custom_emojis/q6.png" alt=":q6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q7': '<img src="/media/custom_emojis/q7.png" alt=":q7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.q8': '<img src="/media/custom_emojis/q8.png" alt=":q8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r1': '<img src="/media/custom_emojis/r1.png" alt=":r1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r2': '<img src="/media/custom_emojis/r2.png" alt=":r2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r3': '<img src="/media/custom_emojis/r3.png" alt=":r3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r4': '<img src="/media/custom_emojis/r4.png" alt=":r4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r5': '<img src="/media/custom_emojis/r5.png" alt=":r5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r6': '<img src="/media/custom_emojis/r6.png" alt=":r6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r7': '<img src="/media/custom_emojis/r7.png" alt=":r7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.r8': '<img src="/media/custom_emojis/r8.png" alt=":r8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s1': '<img src="/media/custom_emojis/s1.png" alt=":s1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s2': '<img src="/media/custom_emojis/s2.png" alt=":s2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s3': '<img src="/media/custom_emojis/s3.png" alt=":s3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s4': '<img src="/media/custom_emojis/s4.png" alt=":s4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s5': '<img src="/media/custom_emojis/s5.png" alt=":s5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s6': '<img src="/media/custom_emojis/s6.png" alt=":s6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s7': '<img src="/media/custom_emojis/s7.png" alt=":s7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.s8': '<img src="/media/custom_emojis/s8.png" alt=":s8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t1': '<img src="/media/custom_emojis/t1.png" alt=":t1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t2': '<img src="/media/custom_emojis/t2.png" alt=":t2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t3': '<img src="/media/custom_emojis/t3.png" alt=":t3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t4': '<img src="/media/custom_emojis/t4.png" alt=":t4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t5': '<img src="/media/custom_emojis/t5.png" alt=":t5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t6': '<img src="/media/custom_emojis/t6.png" alt=":t6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t7': '<img src="/media/custom_emojis/t7.png" alt=":t7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.t8': '<img src="/media/custom_emojis/t8.png" alt=":t8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u1': '<img src="/media/custom_emojis/u1.png" alt=":u1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u2': '<img src="/media/custom_emojis/u2.png" alt=":u2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u3': '<img src="/media/custom_emojis/u3.png" alt=":u3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u4': '<img src="/media/custom_emojis/u4.png" alt=":u4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u5': '<img src="/media/custom_emojis/u5.png" alt=":u5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u6': '<img src="/media/custom_emojis/u6.png" alt=":u6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u7': '<img src="/media/custom_emojis/u7.png" alt=":u7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.u8': '<img src="/media/custom_emojis/u8.png" alt=":u8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v1': '<img src="/media/custom_emojis/v1.png" alt=":v1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v2': '<img src="/media/custom_emojis/v2.png" alt=":v2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v3': '<img src="/media/custom_emojis/v3.png" alt=":v3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v4': '<img src="/media/custom_emojis/v4.png" alt=":v4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v5': '<img src="/media/custom_emojis/v5.png" alt=":v5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v6': '<img src="/media/custom_emojis/v6.png" alt=":v6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v7': '<img src="/media/custom_emojis/v7.png" alt=":v7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.v8': '<img src="/media/custom_emojis/v8.png" alt=":v8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w1': '<img src="/media/custom_emojis/w1.png" alt=":w1" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w2': '<img src="/media/custom_emojis/w2.png" alt=":w2" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w3': '<img src="/media/custom_emojis/w3.png" alt=":w3" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w4': '<img src="/media/custom_emojis/w4.png" alt=":w4" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w5': '<img src="/media/custom_emojis/w5.png" alt=":w5" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w6': '<img src="/media/custom_emojis/w6.png" alt=":w6" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w7': '<img src="/media/custom_emojis/w7.png" alt=":w7" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.w8': '<img src="/media/custom_emojis/w8.png" alt=":w8" class="custom-emoji" style="width: 24px; aspect-ratio: auto 24 / 25; height: 25px;">',
'.x4': '<img src="/media/custom_emojis/x4.png" alt=":x4" class="custom-emoji" style="width: 48px; aspect-ratio: auto 48 / 47; height: 48px;">',


        
        
        
        
       

        # Add more emoji mappings here
    }

    for emoji_code, emoji_html in emoji_mapping.items():
        # Escape HTML characters in the emoji HTML
        emoji_html_escaped = mark_safe(emoji_html)
        value = value.replace(emoji_code, emoji_html_escaped)

    return mark_safe(value)
