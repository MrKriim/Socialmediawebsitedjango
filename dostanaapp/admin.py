from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from .models import Post, Reply
from .models import UserProfile, PublicGroup, GroupMessage, GroupMembership, Follower, UnfollowLog, Following, UserActivity, DeviceInfo, SiteConfiguration



# Define a custom admin action
def delete_all_group_messages(modeladmin, request, queryset):
    # Delete all selected group messages
    queryset.delete()

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'has_profile')
    search_fields = ('username', 'email')  # Add the fields you want to search

    def has_profile(self, obj):
        return UserProfile.objects.filter(user=obj).exists()

    has_profile.boolean = True
    has_profile.short_description = 'Has Profile'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)




admin.site.register(Reply)



class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__email', 'gender', 'marital_status', 'star', 'about', 'city')
    list_display = ('user', 'gender', 'scores', 'ban', 'ip_address', 'marital_status', 'star', 'age', 'city', 'followers_count', 'following_count', 'is_private')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['widget'] = ForeignKeyRawIdWidget(
                db_field.remote_field,
                admin.site,
                using=kwargs.get('using'),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(PublicGroup)



admin.site.register(UserActivity)

admin.site.register(DeviceInfo)
admin.site.register(SiteConfiguration)



class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    list_filter = ('user__username')
    search_fields = ('user__username', 'content')
    ordering = ('-created_at',)

admin.site.register(Post, PostAdmin)
