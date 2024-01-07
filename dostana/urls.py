"""
URL configuration for dostana project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from dostanaapp import views
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.conf.urls import handler404
from dostanaapp.views import page_not_found
from dostanaapp .models import Post, Reply
admin.site.site_header = "Dostana "
admin.site.site_title = "Dostana Administration"
admin.site.index_title = "Dostana|Administration"
from django.contrib.sitemaps.views import sitemap
from dostanaapp.sitemap import PostSitemap
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth import views as auth_views
handler404 = page_not_found


handler404 = 'dostanaapp.views.page_not_found'
sitemaps={
        'posts':PostSitemap
    }

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('gift_points/<str:username>/', views.gift_points, name='gift_points'),
    path('toggle_signup/<int:site_config_id>/', views.toggle_signup, name='toggle_signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('shop/', views.shop, name='shop'),
    path('login/', views.userlogin, name='userlogin'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('shop/', views.shop, name='shop'),
    path('watcher/', views.watcher, name='watcher'),
    path('purchase_watcher/<int:product_id>/', views.purchase_watcher, name='purchase_watcher'),
    path('contactus/', views.contactus, name='contactus'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('terms&conditions/', views.termsconditions, name='terms&conditions'),
    path('rules/', views.rules, name='rules'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('Search/', views.Search, name='Search'),
    path('Share/', views.Share, name='Share'),
    path('Notifications/', views.notifications, name='Notifications'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('add_reply/<int:post_id>/', views.add_reply, name='add_reply'),
    path('reply/<int:post_id>/<int:reply_id>/', views.add_reply, name='add_reply'),
    path('send_reply/', views.Notification, name='send_reply'),
    path('post/<int:post_id>/liked-users/', views.liked_users, name='liked_users'),
    path('post/<int:post_id>/disliked-users/', views.disliked_users, name='disliked_users'),
    path('more/', views.more_view, name='More'),
    path('top-scores/', views.top_scores_view, name='TopScores'),
    path('public-group/', views.public_group_view, name='PublicGroup'),
    path('public-group/<int:group_id>/', views.public_group_detail, name='public_group_detail'),
    path('create-group/', views.create_group, name='create-group'),
    path('popular-groups/', views.popular_groups_view, name='popular-groups'),
    path('private-group/', views.private_group_view, name='PrivateGroup'),
    path('one-on-one/', views.one_on_one_view, name='OneOnOne'),
    path('games/', views.games_view, name='Games'),
    path('public-group/<int:group_id>/change-rules/', views.change_rules, name='change_rules'),
    path('public-group/<int:group_id>/join/', views.join_group, name='join_group'),
    path('group/<int:group_id>/kick/<int:user_id>/', views.kick_user, name='kick_user'),
    path('group/<int:group_id>/hide/<int:message_id>/', views.hide_message, name='hide_message'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('remove_follower/<str:username>/', views.remove_follower, name='remove_follower'),
    path('followers/<str:username>/', views.followers_list, name='followers_list'),
    path('following/<str:username>/', views.following_list, name='following_list'),
    path('', views.for_me_view, name='for_me_view'),
    path('remove_all_posts/', views.remove_all_posts, name='remove_all_posts'),
    path('emoji-list/', views.emoji_list, name='emoji_list'),
    path('online_users/', views.online_users, name='online_users'),
    path('initiate_chat/<int:recipient_id>/', views.initiate_chat, name='initiate_chat'),
    path('received_invitations/', views.received_invitations, name='received_invitations'),
    path('sent_invitations/', views.sent_invitations, name='sent_invitations'),
    path('accept_invitation/<int:invitation_id>/', views.accept_invitation, name='accept_invitation'),
    path('reject_invitation/<int:invitation_id>/', views.reject_invitation, name='reject_invitation'),
    path('one_on_one_chats/', views.list_one_on_one_chats, name='list_one_on_one_chats'),
    path('leave_chat/<int:chat_id>/', views.leave_chat, name='leave_chat'),
    path('admin-tools/', views.admin_tools, name='admin_tools_url_name'),
    path('send_message/<int:chat_id>/', views.send_message, name='send_message'),
    
    path('send_invitation/<int:recipient_id>/', views.send_invitation, name='send_invitation'),
    path('public_group/clear_messages/<int:group_id>/', views.clear_group_messages, name='clear_group_messages'),

    path('send_message/<int:chat_id>/', views.send_message, name='send_message'),
    path('chat_detail/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('text_posts/', views.text_posts_view, name='text_posts'),
    path('picture_posts/', views.picture_posts_view, name='picture_posts'),
    path('video_posts/', views.video_posts_view, name='video_posts'),
    path('profile/<str:username>/', views.Profile, name='profile'),
    path('toggle_comment_visibility/<int:reply_id>/', views.toggle_comment_visibility, name='toggle_comment_visibility'),
    # Edit profile view
    path('edit_profile/<str:username>/', views.edit_profile, name='edit_profile'),
    path('access-denied/', views.access_denied_view, name='access_denied'),

    path('reply-help/', views.reply_help, name='replyhelp'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('hide_comment/<int:post_id>/<int:reply_id>/', views.hide_comment, name='hide_comment'),
    path('unhide_comment/<int:post_id>/<int:reply_id>/', views.unhide_comment, name='unhide_comment'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }), ]
