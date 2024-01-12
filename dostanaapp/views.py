from django.template.defaultfilters import truncatechars
from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import random
from django.utils.translation import gettext as _
from django.db.models import F
from django.utils.html import strip_tags
from django.contrib.auth.decorators import user_passes_test
from dostanaapp.models import *
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.conf import settings
import os
import socket
import re
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
import string
from django.utils.safestring import mark_safe
from django.db.utils import IntegrityError
import os
import uuid
from django.core.files.base import ContentFile
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db import transaction
from django.template.defaultfilters import truncatechars
from django.db.models import CharField, Value
from django.core.exceptions import ValidationError
from django.http import Http404
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView
from django.core.cache import cache
from django.utils import timesince
from django.utils.timezone import now
from django.http import StreamingHttpResponse

def shop(request):
    # Add your view logic here
    # For example, you can retrieve products from a database
    # and pass them to the template

    # Replace with your actual product model




    return render(request, 'shop.html')

def watcher(request):
    # Add your logic to retrieve the "Watcher" product here
    # For example, you can filter it by name or any other unique identifier
    # Replace 'watcher_product' with your actual product retrieval logic
    watcher_product = Product.objects.get(name="Watcher")

    context = {
        'watcher_product': watcher_product,
    }

    return render(request, 'watcher.html', context)

@login_required
def purchase_watcher(request, product_id):
    # Retrieve the selected product
    product = get_object_or_404(Product, pk=product_id)

    # Define a dictionary to map duration to prices
    duration_prices = {
        1: 10000,   # 1 day price
        2: 20000,   # 2 days price
        3: 30000,   # 3 days price
    }

    selected_duration = int(request.POST.get('duration', 1))

    # Check if the user has enough scores to purchase the product
    if request.user.userprofile.scores >= duration_prices[selected_duration]:
        # Calculate the price based on the selected duration
        price = duration_prices[selected_duration]

        # Deduct the points from the user
        request.user.userprofile.scores -= price
        request.user.userprofile.save()

        # Implement the feature activation logic
        # Update the "Watcher" feature fields
        request.user.userprofile.watcher_purchased = True
        request.user.userprofile.watcher_duration = selected_duration  # Set the purchased duration
        request.user.userprofile.watcher_expiration_date = timezone.now() + timedelta(days=selected_duration)
        request.user.userprofile.save()

        # Check if 'Watcher' feature has expired
        current_time = timezone.now()
        expiration_date = request.user.userprofile.watcher_expiration_date

        if current_time > expiration_date:
            request.user.userprofile.watcher_purchased = False
            request.user.userprofile.watcher_duration = 0
            request.user.userprofile.watcher_expiration_date = None
            request.user.userprofile.save()
            messages.warning(request, "Your Watcher feature has expired.")

        messages.success(request, f"You have successfully purchased the {product.name} for {selected_duration} day(s). Enjoy the feature!")
        return redirect('profile', username=request.user.username)
    else:
        # User does not have enough points to purchase the product
        messages.error(request, "Sorry, you don't have enough points to purchase this product.")
        return redirect('watcher')




@login_required(login_url='/signup/')
def delete_post(request, username, post_id):
    # Get the post based on post_id and username
    post = get_object_or_404(Post, id=post_id, user__username=username)

    # Check if the post can be deleted (5-minute interval restriction)
    if post.last_post_delete_time and (timezone.now() - post.last_post_delete_time) < timedelta(minutes=5):
        remaining_time = (post.last_post_delete_time + timedelta(minutes=5)) - timezone.now()
        messages.error(request, f"Aap sirf har 5 minute baad aik post ko delete kar sakte hain. Baaqi waqt: {remaining_time}.")
    else:
        # Perform the post deletion without recreating it
        post.delete()
        messages.success(request, "Post deleted successfully.")

    return redirect('profile', username=username)



class CustomLogoutView(LogoutView):
    """
    Custom logout view that logs the user out and redirects to a specific page.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Redirect to a desired page after logout (e.g., the home page).
        return redirect('index')  # Change 'home' to the name of your desired landing page.



def toggle_signup(request, site_config_id):
    try:
        site_config = SiteConfiguration.objects.get(pk=site_config_id)
        site_config.signup_enabled = not site_config.signup_enabled
        site_config.save()

        if site_config.signup_enabled:
            messages.success(request, 'Signup feature has been turned on.')
        else:
            messages.success(request, 'Signup feature has been turned off.')
    except SiteConfiguration.DoesNotExist:
        messages.error(request, 'SiteConfiguration not found.')

    context = {
        'site_config': site_config,
    }

    return render(request, 'admin_tools.html', context)


@staff_member_required  # Restrict access to superusers
def admin_tools(request):
    # Get the SiteConfiguration object
    site_config = SiteConfiguration.objects.first()

    # Debug: Print the site_config.id


    context = {
        'site_config': site_config,
    }

    return render(request, 'admin_tools.html', context)


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Update the user's last_active field when they log in
    UserActivity.objects.update_or_create(user=user, defaults={'last_active': timezone.now()})

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # Update the user's last_active field when they log out
    UserActivity.objects.update_or_create(user=user, defaults={'last_active': timezone.now()})





def base(request):

    user = request.user
    notifications = Notification.objects.filter(user=user, is_read=False)

    unread_notification_count = notifications.count()

    context = {
        'unread_notification_count': unread_notification_count,
        # You can include other context data here as needed
    }

    return render(request, 'base.html', context)



@user_passes_test(lambda u: not u.is_authenticated, login_url='/index/')


# Regular expression pattern to match valid username characters

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        comma_index = x_forwarded_for.find(',')
        if comma_index != -1:
            ip = x_forwarded_for[:comma_index].strip()  # Extract IP before the first comma
        else:
            ip = x_forwarded_for.strip()  # No comma found, use the entire string
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ... other imports ...


def get_user_location(ip_address):
    # Simulate a response with dummy data
    dummy_data = {
        "ip": ip_address,
        "hostname": "dummy-hostname",
        "city": "Dummy City",
        "region": "Dummy Region",
        "country": "Dummy Country",
        "loc": "0,0",  # Latitude and longitude, you can set your desired values
    }

    location = dummy_data.get('loc', '').split(',')
    return location

@user_passes_test(lambda u: not u.is_authenticated, login_url='/index/')


# Regular expression pattern to match valid username characters

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        comma_index = x_forwarded_for.find(',')
        if comma_index != -1:
            ip = x_forwarded_for[:comma_index].strip()  # Extract IP before the first comma
        else:
            ip = x_forwarded_for.strip()  # No comma found, use the entire string
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip




def signup(request):
    signup_error = None  # Initialize the signup error variable

    # Check if signup is enabled
    site_config = SiteConfiguration.objects.first()  # Assuming you have a single configuration object
    signup_enabled = site_config.signup_enabled if site_config else False  # Default to False if site_config doesn't exist

    if signup_enabled:
        # Proceed with signup logic if signup is enabled

        if request.method == 'POST':
            uname = request.POST.get('username')
            upass = request.POST.get('password')
            profile_pic = request.FILES.get('profile_pic')
            device_id = request.POST.get('device_id')
            user_agent = request.META.get('HTTP_USER_AGENT')
            fingerprint = request.POST.get('fingerprint')
            ip_address = get_client_ip(request)

            # Validate and sanitize username
            uname = uname.strip()  # Remove leading/trailing spaces
            if len(uname) < 5 or len(uname) > 15:
                signup_error = 'Username should be at least 5 characters and at most 15 characters long.'
            VALID_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
            # Check if username contains dangerous characters or spaces
            if not VALID_USERNAME_PATTERN.match(uname):
                signup_error = 'Username should only contain English letters, numbers, and underscores.'
            if ' ' in uname:
                signup_error = 'Username should not contain spaces.'

            # Additional check for restricted usernames
            RESTRICTED_USERNAMES = ['denz', 'denzz', 'deenz', 'danz', 'kriim', 'admin']
            if uname.lower() in RESTRICTED_USERNAMES:
                signup_error = 'The chosen username is not allowed.'

            # Validate and sanitize password
            if len(upass) < 5 or len(upass) > 20:
                signup_error = 'Password should be at least 5 characters and at most 20 characters long.'

            if signup_error is None:  # Proceed only if no signup error
                ip_address = request.META.get('REMOTE_ADDR')

                # Get the user's location using ipinfo.io API
                location = get_user_location(ip_address)
                latitude, longitude = location if len(location) == 2 else (None, None)

                # Check if the username already exists
                try:
                    my_user = User.objects.create_user(username=uname, password=upass)
                except IntegrityError:
                    signup_error = 'A user with this username already exists.'
                    my_user = None

                if my_user:
                    # Create the associated user profile
                    my_profile = UserProfile(
                        user=my_user,
                        profile_pic=profile_pic,
                        gender='M',  # Default to Male
                        scores=1,  # Default scores
                        ban=False,  # Default ban status
                        ip_address=request.META.get('REMOTE_ADDR'),  # Save the user's IP address
                        user_activity_log='',  # Initialize user activity log
                        marital_status='ghershadishuda',  # Default marital status
                        star='Virgo',  # Default star sign (update this field if needed)
                        about='i love dostana',  # Default about
                        age=14,  # Default age
                        city='dostana',  # Default city
                        latitude=latitude,
                        longitude=longitude,
                    )
                    my_profile.save()

                    # Create and save the device info with the my_user object
                    device_info = DeviceInfo(
                        user=my_user,
                        device_id=device_id,
                        user_agent=user_agent,
                        fingerprint=fingerprint,
                        ip_address = "127.0.0.1"
                    )
                    device_info.save()

                    # Authenticate and login the user if they are not authenticated
                    if not request.user.is_authenticated:
                        user = authenticate(request, username=uname, password=upass)
                        if user is not None:
                            login(request, user)

                    return redirect('index')  # Redirect to index after a successful signup

    return render(request, 'signup.html', {'signup_error': signup_error, 'signup_enabled': signup_enabled})





def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            return redirect('index')  # Replace 'index' with the appropriate URL name for the index page
        else:
            # Display an error message for incorrect username or password
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def aboutus(request):
    # Add your view logic here if needed
    return render(request, 'aboutus.html')

def contactus(request):
    # Add your view logic here if needed
    return render(request, 'contactus.html')

def termsconditions(request):
    # Add your view logic here if needed
    return render(request, 'terms&conditions.html')

def privacypolicy(request):
    # Add your view logic here if needed
    return render(request, 'privacypolicy.html')


def rules(request):
    # Add your view logic here if needed
    return render(request, 'rules.html')

@login_required(login_url='/signup/')
def Search(request):
    # Add your view logic here if needed
    return render(request, 'Search.html')

@transaction.atomic
@login_required(login_url='/signup/')
def Share(request):
    update_user_activity(request)
    
    POST_INTERVAL_SECONDS = 30
    content_error, picture_title_error, video_error, dangerous_characters_error = "", "", "", ""

    disable_taliyaan = request.POST.get('disable_taliyaan')
    disable_chupair = request.POST.get('disable_chupair')
    turn_off_replies = request.POST.get('turn_off_replies')

    last_post = request.user.post_set.order_by('-created_at').first()
    time_since_last_post = timezone.now() - last_post.created_at if last_post else timedelta(seconds=0)
    error_message = f"Please wait {max(0, POST_INTERVAL_SECONDS - time_since_last_post.total_seconds())} seconds before creating another post." if time_since_last_post < timedelta(seconds=POST_INTERVAL_SECONDS) else None

    if request.method == 'POST':
        content, picture_title = strip_tags(request.POST.get('content', '')), strip_tags(request.POST.get('picture_title', ''))
        content_error = "Content cannot be blank." if not content else "Content must be between 5 and 300 characters." if not 5 <= len(content) <= 300 else ""
        dangerous_characters_error = "Content contains illegal and dangerous characters." if contains_dangerous_characters(content) else ""

        if error_message:
            return render(request, 'Share.html', {'content_error': error_message})

        try:
            if 'picture' in request.FILES:
                picture = request.FILES['picture']
                validate_image_size(picture.size)
                post = create_post(request.user, content, picture_title, picture, turn_off_replies, disable_taliyaan, disable_chupair)
            elif 'video' in request.FILES:
                video = request.FILES['video']
                validate_video_size(video.size)
                validate_video_format(video.name)
                post = create_post(request.user, content, picture_title, video=video, turn_off_replies=turn_off_replies)
            else:
                post = create_post(request.user, content, turn_off_replies=turn_off_replies, disable_taliyaan=disable_taliyaan, disable_chupair=disable_chupair)
        except ValidationError as e:
            return render(request, 'Share.html', {'content': content, 'content_error': str(e)})

        request.user.userprofile.scores += 20 if 'picture' in request.FILES else 0
        request.user.userprofile.save()

    return render(request, 'Share.html', {
        'content_error': content_error,
        'dangerous_characters_error': dangerous_characters_error,
        'picture_title_error': picture_title_error,
        'video_error': video_error,
        'error_message': error_message,
    })


def contains_dangerous_characters(text):
    dangerous_characters = [';', "'", '/', '\\', '<', '>', '&']
    return any(char in text for char in dangerous_characters)


@login_required(login_url='/signup/')
def add_reply(request, post_id):
    update_user_activity(request)
    post = get_object_or_404(Post, id=post_id)
    error_message = ""

    if request.method == 'POST':
        reply_content = request.POST.get('reply_content')

        # Check if the user has already commented on this post
        existing_comment = Comment.objects.filter(user=request.user, post=post).first()

        if not existing_comment:
            # If the user hasn't commented on this post yet, create a comment
            comment = Comment.objects.create(user=request.user, post=post)
        else:
            # If the user has already commented, use the existing comment
            comment = existing_comment

        # Create a reply associated with the comment
        reply = Reply.objects.create(
            user=request.user,
            post=post,
            content=reply_content,
            comment=comment
        )

        # Send notifications to post owner and all users on the post except the comment author
        notification_users = User.objects.filter(Q(post=post) | Q(comment__post=post)).exclude(id=request.user.id)
        for user in notification_users:
            # Check if a notification already exists for this reply and user
            existing_notification = Notification.objects.filter(user=user, post=post, reply=reply).first()
            if not existing_notification:
                notification = Notification.objects.create(
                    user=user,
                    post=post,
                    reply=reply,
                    timestamp=reply.created_at
                )
                # Ensure that only the latest 10 notifications per user are retained
       

        return redirect('post_detail', post_id=post_id)

    replies = Reply.objects.filter(post=post).order_by('-created_at')
    return render(request, 'post_detail.html', {'post': post, 'replies': replies, 'error_message': error_message})




@login_required(login_url='/signup/')
def toggle_comment_visibility(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)

    # Ensure that only the post owner can toggle comment visibility
    if reply.post.user == request.user:
        reply.hidden = not reply.hidden
        reply.save()

    return redirect('post_detail', post_id=reply.post.id)


def post_detail(request, post_id):
    update_user_activity(request)
    post = get_object_or_404(Post, id=post_id)

    # Load only the latest 25 replies
    latest_replies = Reply.objects.filter(post=post).order_by('-created_at')[:25]

    commenters = User.objects.exclude(id=request.user.id).filter(reply__post=post).distinct()

    return render(request, 'post_detail.html', {'post': post, 'replies': latest_replies, 'commenters': commenters})





@login_required(login_url='/signup/')
def hide_comment(request, post_id, reply_id):
    post = get_object_or_404(Post, id=post_id)
    reply = get_object_or_404(Reply, id=reply_id, post=post)

    # Ensure that only the post owner can hide a comment
    if post.user == request.user:
        reply.hidden = True
        reply.save()

    return redirect('post_detail', post_id=post.id)

@login_required(login_url='/signup/')
def unhide_comment(request, post_id, reply_id):
    post = get_object_or_404(Post, id=post_id)
    reply = get_object_or_404(Reply, id=reply_id, post=post)

    # Ensure that only the post owner can unhide a comment
    if post.user == request.user:
        reply.hidden = False
        reply.save()

    return redirect('post_detail', post_id=post.id)

def get_picture_post_count(user):
    return Post.objects.filter(user=user, post_type='Picture').count()



@login_required
def public_group_detail(request, group_id):
    update_user_activity(request)
    group = get_object_or_404(PublicGroup, pk=group_id)
    MESSAGE_INTERVAL = timedelta(seconds=8)
    message_text_error = None
    image_error = None
    remaining_time = None
    remaining_hours = None
    remaining_minutes = None
    remaining_seconds = None

    join_message = None
    kick_message = None
    rules_change_message = None

    if request.method == 'POST':
        # Check if the user has recently sent a message
        last_message = group.groupmessage_set.filter(sender=request.user).order_by('-timestamp').first()

        if last_message and last_message.timestamp:
            time_since_last_message = timezone.now() - last_message.timestamp

            if time_since_last_message < MESSAGE_INTERVAL:
                time_remaining = MESSAGE_INTERVAL - time_since_last_message
                message_text_error = f" Dubara message bejh sakegay {int(time_remaining.total_seconds())} seconds baad."

        # Check if the user has recently uploaded an image
        last_image_message = group.groupmessage_set.filter(sender=request.user, image__isnull=False).order_by('-timestamp').first()

        if last_image_message and last_image_message.timestamp:
            time_since_last_image = timezone.now() - last_image_message.timestamp

            if time_since_last_image < MESSAGE_INTERVAL:
                time_remaining = MESSAGE_INTERVAL - time_since_last_image
                image_error = f"Dubara tasveer bejh sakegay  {int(time_remaining.total_seconds())} seconds baad."

        # Validate message and image
        message_text = request.POST.get('message_text')
        image = request.FILES.get('image')

        if not message_text or len(message_text) < 4 or len(message_text) > 200:
            message_text_error = "Message should be between 4 and 200 characters."

        if image:
            if not image.content_type.startswith('image'):
                image_error = "Only image files are allowed."
            elif image.size > 10 * 1024 * 1024:  # 10MB limit
                image_error = "Image size should be less than 10MB."

        # If no errors, create a new message or image, and update the timestamp
        if not message_text_error and not image_error:
            message = GroupMessage.objects.create(group=group, sender=request.user, message_text=message_text, image=image)
            message.timestamp = timezone.now()
            message.save()
            request.user.userprofile.scores += 2
            request.user.userprofile.save()

            user_membership = group.groupmembership_set.filter(user=request.user).first()
            user_is_member = user_membership.member if user_membership else False

            if not user_is_member:
                join_message = f"{request.user.username} joined the group."

            return redirect('public_group_detail', group_id=group_id)  # PRG pattern

    user_membership = group.groupmembership_set.filter(user=request.user).first()
    user_is_member = user_membership.member if user_membership else False
    user_was_kicked = user_membership.kicked if user_membership else False

    if user_was_kicked:
        remaining_time = user_membership.kicked_until - timezone.now()
        remaining_hours = int(remaining_time.total_seconds() // 3600)
        remaining_minutes = int((remaining_time.total_seconds() // 60) % 60)
        remaining_seconds = int(remaining_time.total_seconds() % 60)

    active_members_count = group.groupmembership_set.filter(member=True, kicked=False).count()

    messages = group.groupmessage_set.order_by('-timestamp')[:25]

    group_rules_lines = group.rules.split('\n')
    unique_lines = set()

    for line in group_rules_lines:
        if line.strip():
            unique_lines.add(line.strip())

    context = {
        'group': group,
        'user_is_member': user_is_member,
        'user_was_kicked': user_was_kicked,
        'active_members_count': active_members_count,
        'messages': messages,
        'message_text_error': message_text_error,
        'image_error': image_error,
        'admin_username': group.admin.username,
        'remaining_hours': remaining_hours,
        'remaining_minutes': remaining_minutes,
        'remaining_seconds': remaining_seconds,
        'join_message': join_message,
        'kick_message': kick_message,
        'rules_change_message': rules_change_message,
        'group_rules_lines': unique_lines,
    }

    return render(request, 'public_group_detail.html', context)







def access_denied_view(request):
    return render(request, 'access_denied.html')



def can_view_private_profile(user):
    # Get the username from the user object
    username = user.username

    # Check if the user is the profile owner or the profile is not private
    try:
        profile = UserProfile.objects.get(user__username=username)

        # Additional check for "Watcher" power
        if user.userprofile.watcher_purchased:
            return True

        return user == profile.user or not profile.is_private
    except UserProfile.DoesNotExist:
        return False

@login_required
@user_passes_test(can_view_private_profile, login_url='/access-denied/')
def Profile(request, username):
    update_user_activity(request)
    user = request.user
    user_profile = get_object_or_404(UserProfile, user__username=username)

    # Fetch the top 3 scorers
    top_scorers = UserProfile.objects.order_by('-scores')[:3]

    # Calculate the maximum points that can be gifted by the logged-in user (50% of their score)
    max_gift_points = request.user.userprofile.scores // 2

    # Check if the logged-in user is in the top 3 scorers
    is_top_scorer = request.user.userprofile in top_scorers

    # Calculate the points to be added to the user whose profile is being viewed (e.g., +10 points)
    points_to_add = 10  # You can adjust this value as needed

    if request.method == 'POST':
        if 'make_private' in request.POST:
            # Logic to make the profile private (you might already have this)
            user_profile.is_private = True
            user_profile.save()
        elif 'make_public' in request.POST:
            # Logic to make the profile public
            user_profile.is_private = False
            user_profile.save()
        elif 'points_to_gift' in request.POST:
            # Logic to handle gifting points
            points_to_gift = int(request.POST['points_to_gift'])

            # Ensure that the logged-in user is a top scorer and has enough points to gift
            if is_top_scorer and points_to_gift > 0 and points_to_gift <= max_gift_points:
                # Deduct the gifted points from the sender's score
                request.user.userprofile.scores -= points_to_gift
                request.user.userprofile.save()

                # Add the gifted points to the user whose profile is being viewed
                user_profile.scores += points_to_gift
                user_profile.save()

    # Retrieve all posts for the user's profile
    all_posts = Post.objects.filter(user=user_profile.user).order_by('-created_at')
    for post in all_posts:
        post.truncated_content = truncatechars(post.content, 300)
        post.show_read_more = len(post.content) > 300
    paginator = Paginator(all_posts, 25)  # Show 25 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    current_time = timezone.now()

    # Add the image_url field to each post object
    for post in page_obj:
        if post.picture:
            post.image_url = os.path.join(settings.MEDIA_URL, post.picture.name)

    # Retrieve the groups for which the user is the admin
    admin_groups = PublicGroup.objects.filter(admin=user_profile.user)

    # Count of users who follow this profile
    follower_count = user_profile.followers_count

    # Calculate the following count using the Following model
    following_count = Following.objects.filter(following_user_profile=user_profile).count()

    is_follower = False
    can_become_follower = True
    remaining_time = None

    if request.user.is_authenticated and not user_profile.user == request.user:
        follower_relationship = Follower.objects.filter(follower=request.user.userprofile, following_user_profile=user_profile).first()

        if follower_relationship:
            is_follower = True
            follower_since = follower_relationship.created_at
            time_passed = timezone.now() - follower_since
            can_become_follower = time_passed >= timedelta(days=7)
            if not can_become_follower:
                remaining_time = follower_since + timedelta(days=7) - timezone.now()

    has_unfollowed = UnfollowLog.objects.filter(unfollow_user=request.user.userprofile, unfollow_target=user_profile).exists()

    # Check if the profile is private and the username in the URL doesn't match
    if user_profile.is_private and username != request.user.username:
         if not user.userprofile.watcher_purchased:
             return redirect('/access-denied/')

    context = {
        'user_profile': user_profile,
        'editable': user_profile.user == request.user,
        'page_obj': page_obj,
        'admin_groups': admin_groups,
        'follower_count': follower_count,
        'following_count': following_count,
        'is_follower': is_follower,
        'can_become_follower': can_become_follower,
        'remaining_time': remaining_time,
        'has_unfollowed': has_unfollowed,
        'max_gift_points': max_gift_points,
        'is_top_scorer': is_top_scorer,
    }

    context['current_time'] = current_time
    return render(request, 'Profile.html', context)



@login_required
def gift_points(request, username):
    # Retrieve the recipient's user profile
    recipient_profile = get_object_or_404(UserProfile, user__username=username)

    if request.method == 'POST':
        # Get the number of points to gift from the form
        points_to_gift = int(request.POST.get('points_to_gift', 0))

        # Ensure that the top scorer has enough points to gift
        top_scorer_profile = request.user.userprofile
        if points_to_gift <= 0 or points_to_gift > top_scorer_profile.scores:
            # Invalid points or insufficient balance, handle this case
            return HttpResponse("Invalid gift points request")

        # Deduct the gift points from the top scorer's profile
        top_scorer_profile.scores -= points_to_gift
        top_scorer_profile.save()

        # Add the gift points to the recipient's profile
        recipient_profile.scores += points_to_gift
        recipient_profile.save()

        # Redirect back to the user profile being viewed
        return redirect('profile', username=username)



@login_required(login_url='/signup/')
def edit_profile(request, username):
    update_user_activity(request)
    user_profile = UserProfile.objects.get(user__username=username)

    # Check if the logged-in user matches the user profile being edited
    if request.user == user_profile.user:
        if request.method == 'POST':
            # Process the form submission and update the profile fields
            profile_pic = request.FILES.get('profile_pic')
            gender = request.POST.get('gender')
            marital_status = request.POST.get('marital_status')
            about = request.POST.get('about')
            city = request.POST.get('city')
            age = request.POST.get('age')
            star = request.POST.get('star')

            # Check if age is within the valid range
            if not (12 <= int(age) <= 100):
                return render(request, 'edit_profile.html', {'user_profile': user_profile, 'error_message': 'Enter a valid age (12-100)'})

            # Update the user profile with the new data
            user_profile.gender = gender
            user_profile.marital_status = marital_status
            user_profile.about = about
            user_profile.city = city
            user_profile.age = age
            user_profile.star = star

            # Check if a profile picture is uploaded
            if profile_pic:
                # Check if the uploaded file is an image
                if not profile_pic.content_type.startswith('image'):
                    return render(request, 'edit_profile.html', {'user_profile': user_profile, 'error_message': 'Please upload a valid image file'})

                # Check if the image size is below 10 MB
                if profile_pic.size > 10 * 1024 * 1024:
                    return render(request, 'edit_profile.html', {'user_profile': user_profile, 'error_message': 'Image size should be below 10 MB'})

                # Generate a random name for the image file
                import uuid
                from os import path
                random_name = str(uuid.uuid4())[:12]  # Adjust the length as needed
                file_extension = path.splitext(profile_pic.name)[1]  # Get the file extension

                # Save the image with the random name and original extension
                user_profile.profile_pic.save(f'{random_name}{file_extension}', profile_pic, save=True)

            user_profile.save()

            # Redirect to the user's profile page after updating
            return redirect('profile', username=request.user.username)
        else:
            # Display the form with the current profile data
            return render(request, 'edit_profile.html', {'user_profile': user_profile})
    else:
        # Redirect the user to their own profile page if not the owner
        return redirect(reverse('profile', kwargs={'username': request.user.username}))




def rules(request):
    # Add your view logic here if needed
    return render(request, 'rules.html')

@login_required(login_url='/signup/')
def Search(request):
    # Add your view logic here if needed
    return render(request, 'Search.html')



def page_not_found(request, exception):
    return render(request, '404.html')


@login_required(login_url='/signup/')
def Search(request):
    username = request.GET.get('username')
    users = None

    if username:
        users = User.objects.filter(username__icontains=username)

    return render(request, 'Search.html', {'users': users})


def reply_help(request):
    return render(request, 'reply_help.html')

@login_required(login_url='/signup/')
def notifications(request):
    update_user_activity(request)
    user = request.user

    if request.method == 'POST' and 'delete_notifications' in request.POST:
        # Delete all notifications for the logged-in user
        Notification.objects.filter(user=user).delete()
        return render(request, 'Notifications.html')

    # Update unread notifications to be read when the user visits the notifications page
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    # Retrieve regular notifications
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')

    # Retrieve group-related notifications
    group_notifications = Notification.objects.filter(user=user, is_group_notification=True).order_by('-timestamp')
    message_notifications = Notification.objects.filter(user=user, is_1on1_message_notification=True).order_by('-timestamp')

    # Retrieve other specific types of notifications
    # Example: 1-on-1 message notifications, invite notifications, accept/reject notifications, 1-on-1 chat notifications
    group_notifications = Notification.objects.filter(user=user, is_group_notification=True).order_by('-timestamp')
    one_on_one_message_notifications = Notification.objects.filter(user=user, is_1on1_message_notification=True).order_by('-timestamp')
    invite_notifications = Notification.objects.filter(user=user, is_invite_notification=True).order_by('-timestamp')
    accept_invite_notifications = Notification.objects.filter(user=user, is_accept_invite_notification=True).order_by('-timestamp')
    reject_invite_notifications = Notification.objects.filter(user=user, is_reject_invite_notification=True).order_by('-timestamp')
    one_on_one_chat_notifications = Notification.objects.filter(user=user, is_1on1_chat_notification=True).order_by('-timestamp')
    for notification in message_notifications:
    # Assuming each notification has a reference to the chat (you might need to adjust this)
        one_on_one_chat = notification.one_on_one_chat  # Replace with the actual reference to the chat object in the notification

    # Generate HTML for the button for each notification




    # Now, add this button HTML to the notification object or pass it in the context to render in the template


    context = {
        'notifications': notifications,
        'message_notifications': message_notifications,  # Include message-related notifications
        'group_notifications': group_notifications,
        'invite_notifications': invite_notifications,
        'accept_invite_notifications': accept_invite_notifications,
        'reject_invite_notifications': reject_invite_notifications,
        'one_on_one_chat_notifications': one_on_one_chat_notifications,

        'unread_notification_count': 0,  # Set count to 0 when on the notifications page
    }
    if request.method == 'POST':
        if 'accepted_invite_notification' in request.POST:
            accepted_user = ...  # Retrieve user who accepted the invite
            notification_content = f"{accepted_user.username} ne apka invite accept karlia!"
            accept_notification = Notification.objects.create(
            user=user,
            content=notification_content,
            timestamp=timesince(timezone.now()),  # Convert timestamp to time ago format
            is_accept_invite_notification=True
            )

        elif 'rejected_invite_notification' in request.POST:
            rejected_user = ...  # Retrieve user who rejected the invite
            notification_content = f"{rejected_user.username} rejected your invitation."
            reject_notification = Notification.objects.create(
                user=user,
                content=notification_content,
                timestamp=timezone.now(),
                is_reject_invite_notification=True
            )

        elif 'sent_invite_notification' in request.POST:
            invited_user = ...  # Retrieve user who received the invitation
            notification_content = f"You sent an invitation to {invited_user.username}."
            invite_sent_notification = Notification.objects.create(
                user=user,
                content=notification_content,
                timestamp=timezone.now(),
                is_invite_notification=True
            )

        elif request.method == 'POST':
            # Check if the request is for leaving a one-on-one chat
            if 'leave_one_on_one_chat' in request.POST:
                chat_id = request.POST.get('chat_id')  # Get the chat ID from the form
                chat = OneOnOneChat.objects.get(id=chat_id)

                # Check if the user is a participant in the chat
                if user in chat.participants.all():
                    # Remove the user from the participants
                    chat.participants.remove(user)

                    # Create a notification for leaving the one-on-one chat
                    content = f"{user.username} left the one-on-one chat"
                    Notification.create_1on1_leave_notification(user=user, content=content)

        # Handling replies (example placeholder code)
        selected_reply_id = request.POST.get('selected_reply_id')
        selected_reply = Reply.objects.get(id=selected_reply_id)

        # Check if the reply content contains 'clapped' or 'slapped' and exclude them from notification
        if selected_reply.post.user != user and 'clapped' not in selected_reply.content.lower() and 'slapped' not in selected_reply.content.lower():
            # Create and save the notification for reply action
            is_read = False if 'notifications' not in request.META.get('HTTP_REFERER', '').lower() else True
            notification = Notification.objects.create(
                user=selected_reply.post.user,  # Send notification to the post owner
                post=selected_reply.post,
                content=f"{user.username} replied to your post:",
                timestamp=timezone.now(),
                is_read=is_read
            )

        # Handling group-related notifications (example placeholder code)
        if 'group_notification' in request.POST:
            # Logic to handle group-related notifications
            pass
        if request.method == 'POST':
        # Check if the request is for leaving a one-on-one chat
            if 'leave_one_on_one_chat' in request.POST:
                chat_id = request.POST.get('chat_id')  # Get the chat ID from the form
                chat = OneOnOneChat.objects.get(id=chat_id)

            # Check if the user is a participant in the chat
            if user in chat.participants.all():
                # Remove the user from the participants
                chat.participants.remove(user)

                # Create a notification for leaving the one-on-one chat
                content = f"{user.username} left the one-on-one chat"
                Notification.create_1on1_leave_notification(user=user, content=content)

                # Handle any additional logic related to leaving the chat
    return render(request, 'Notifications.html', context)


def index(request):
    update_user_activity(request)
    timeout = 5  # Set a timeout for the socket connection attempt
    internet_status = "online"  # Default to "online" status

    try:
        # Attempt to create a socket connection to a known external host (e.g., Google's DNS server)
        socket.create_connection(("8.8.8.8", 53), timeout)
    except OSError:
        internet_status = "offline"

    # Check for a custom header that might be added by Free Basics
    is_freebasics_user = 'HTTP_X_FB_PLATFORM' in request.META

    # Retrieve latest 25 posts and order them by created_at
    latest_posts = Post.objects.order_by('-created_at')[:25]

    # Apply character truncation for content in each post in the view
    for post in latest_posts:
        post.truncated_content = truncatechars(post.content, 300)
        post.show_read_more = len(post.content) > 300

    unread_notification_count = 0

    if request.user.is_authenticated:
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        unread_notification_count = notifications.count()

    # Add the image_url field to each post object
    for post in latest_posts:
        if post.picture:
            post.image_url = os.path.join(settings.MEDIA_URL, post.picture.name)

    context = {
        'latest_posts': latest_posts,
        'unread_notification_count': unread_notification_count,
        'internet_status': internet_status,
        'is_freebasics_user': is_freebasics_user,
        # Other context data for this page
    }

    return render(request, 'index.html', context)




@login_required(login_url='/signup/')
def like_post(request, post_id):
    update_user_activity(request)
    if request.user.is_authenticated:
        user = request.user
        post = Post.objects.get(pk=post_id)

        if user == post.user:
            # User cannot clap their own post, show error message
            messages.error(request, "You cannot clap your own post!")
        elif user in post.liked_by.all():
            # User has already liked the post, handle this scenario if needed
            pass
        else:
            post.liked_by.add(user)

            # Check if the logged-in user is in the top 3 posters
            top_posters = UserProfile.objects.annotate(total_posts=Count('user__post')).order_by('-total_posts')[:7]

            if user.userprofile in top_posters:
                # Add 500 points to the post creator's score
                post.user.userprofile.scores += 40
            else:
                # Add 10 points to the post creator's score
                post.user.userprofile.scores += 10

            # Save the changes
            post.user.userprofile.save()
            post.save()




    # Redirect back to the current page
    return redirect(request.META.get('HTTP_REFERER', 'post_list'))



@login_required(login_url='/signup/')
def dislike_post(request, post_id):
    update_user_activity(request)
    if request.user.is_authenticated:
        user = request.user
        post = Post.objects.get(pk=post_id)

        if user == post.user:
            # User cannot dislike their own post, show error message
            messages.error(request, "You cannot dislike your own post!")
        elif user in post.disliked_by.all():
            # User has already disliked the post, handle this scenario if needed
            pass
        else:
            post.disliked_by.add(user)

            # Check if the logged-in user is in the top 3 posters
            top_posters = UserProfile.objects.annotate(total_posts=Count('user__post')).order_by('-total_posts')[:7]

            if user.userprofile in top_posters:
                # Subtract 40 points from the post creator's score
                post.user.userprofile.scores -= 40
            else:
                # Subtract 1 point from the post creator's score
                post.user.userprofile.scores -= 1

            # Save the changes
            post.user.userprofile.save()
            post.save()

    # Redirect back to the current page
    return redirect(request.META.get('HTTP_REFERER', 'post_list'))





def liked_users(request, post_id):
    update_user_activity(request)
    post = get_object_or_404(Post, pk=post_id)
    liked_users = post.liked_by.all()

    top_posters = UserProfile.objects.annotate(total_posts=Count('user__post')).order_by('-total_posts')[:7]

    for user in liked_users:
        if user.userprofile in top_posters:
            user.points = 40
        else:
            user.points = 10

    return render(request, 'liked_users.html', {'post': post, 'users': liked_users})



def disliked_users(request, post_id):
    update_user_activity(request)
    post = get_object_or_404(Post, pk=post_id)
    disliked_users = post.disliked_by.all()

    top_posters = UserProfile.objects.annotate(total_posts=Count('user__post')).order_by('-total_posts')[:7]

    for user in disliked_users:
        if user.userprofile in top_posters:
            user.points = -40
        else:
            user.points = -1

    return render(request, 'disliked_users.html', {'post': post, 'users': disliked_users})




def more_view(request):
    update_user_activity(request)
    # You can add any logic or data processing here
    context = {
        'content': 'This is the content of the "More" link.',
    }
    return render(request, 'more_template.html', context)

def top_scores_view(request):
    update_user_activity(request)
    top_scorers = UserProfile.objects.order_by('-scores')[:21]
    return render(request, 'top_scores.html', {'top_scorers': top_scorers})


@login_required
def public_group_view(request):
    update_user_activity(request)
    # Retrieve the joined groups for the current user
    joined_group_memberships = GroupMembership.objects.filter(user=request.user, member=True)
    joined_groups = [membership.group for membership in joined_group_memberships]

    context = {
        'joined_groups': joined_groups
    }

    return render(request, 'public_group.html', context)

@login_required
def create_group(request):
    update_user_activity(request)
    if request.method == 'POST':
        title = request.POST.get('title')
        rules = request.POST.get('rules')

        if len(title) < 10:
            messages.error(request, 'Group title should be at least 10 characters.')
            return render(request, 'create_group.html')

        if len(rules) < 20:
            messages.error(request, 'Rules should be at least 20 characters.')
            return render(request, 'create_group.html')

        if len(title) > 40:
            messages.error(request, 'Group title should be shorter.')
            return render(request, 'create_group.html')

        if len(rules) > 300:
            messages.error(request, 'Rules should be shorter.')
            return render(request, 'create_group.html')

        if not title or not rules:
            messages.error(request, 'Title and rules are required.')
            return render(request, 'create_group.html')

        # Check if the user has enough scores
        if request.user.userprofile.scores < 500:
            messages.error(request, 'You need at least 500 points to create a group.')
            return render(request, 'create_group.html')

        # Check if the user already has 5 groups
        if PublicGroup.objects.filter(admin=request.user).count() >= 5:
             messages.error(request, 'You cannot create more than 5 groups.')
             return render(request, 'create_group.html')



        # Check if a group with the same name already exists
        if PublicGroup.objects.filter(title=title).exists():
            messages.error(request, 'A group with this name already exists. Choose another name.')
            return render(request, 'create_group.html')

        # Deduct 500 scores from the user
        request.user.userprofile.scores -= 500
        request.user.userprofile.save()

        group = PublicGroup.objects.create(title=title, rules=rules, admin=request.user)
        GroupMembership.objects.create(user=request.user, group=group, member=True)


        return redirect('public_group_detail', group_id=group.pk)

    return render(request, 'create_group.html')

@login_required
def change_rules(request, group_id):
    update_user_activity(request)
    group = get_object_or_404(PublicGroup, pk=group_id)

    if request.method == 'POST':
        new_rules = request.POST.get('new_rules')

        # Split rules into lines containing 40 characters
        rule_lines = [new_rules[i:i+40] for i in range(0, len(new_rules), 40)]
        formatted_rules = '\n'.join(rule_lines)

        group.rules = formatted_rules
        group.save()

        # Send a message to the group indicating the rule change
        GroupMessage.objects.create(group=group, sender=group.admin, message_text=f"Admin changed the rules: {formatted_rules}")

        return redirect('public_group_detail', group_id=group.pk)

    return render(request, 'change_rules.html', {'group': group})





@login_required
def join_group(request, group_id):
    update_user_activity(request)
    group = get_object_or_404(PublicGroup, pk=group_id)
    user_membership = group.groupmembership_set.filter(user=request.user).first()

    if not user_membership and not group.groupmembership_set.filter(user=request.user, kicked=True, kicked_until__gte=timezone.now()).exists():
        with transaction.atomic():
            GroupMembership.objects.create(user=request.user, group=group, member=True)
            GroupMessage.objects.create(group=group, sender=request.user, message_text=f"{request.user.username} has joined the group.")
        messages.success(request, 'You have joined the group.')
    elif user_membership and user_membership.kicked:
        remaining_time = user_membership.kicked_until - timezone.now()
        remaining_hours = int(remaining_time.total_seconds() // 3600)
        messages.error(request, f'You got kicked from this group. You can join again after {remaining_hours} hours.')
    else:
        messages.info(request, 'You are already a member of this group.')

    return redirect('public_group_detail', group_id=group.pk)



@login_required
def clear_group_messages(request, group_id):
    group = get_object_or_404(PublicGroup, pk=group_id)

    # Check if the logged-in user is the group admin
    if request.user == group.admin:
        # Clear all messages in the group
        group.groupmessage_set.all().delete()

        # Add a success message
        messages.success(request, 'Group messages have been cleared successfully.')
    else:
        # Add a permission error message
        messages.error(request, 'Only the group creator can clear messages.')

    return redirect('public_group_detail', group_id=group_id)







@login_required
def kick_user(request, group_id, user_id):
    update_user_activity(request)
    group = get_object_or_404(PublicGroup, pk=group_id)
    user_to_kick = get_object_or_404(User, pk=user_id)

    if request.user == group.admin:
        # Update the user's kicked_until attribute
        group_membership = GroupMembership.objects.get(group=group, user=user_to_kick)
        group_membership.kicked = True  # Set kicked to True
        group_membership.kicked_until = timezone.now() + timedelta(days=1)  # Kick for 24 hours
        group_membership.member = False  # Remove user from active members
        group_membership.save()

        # Remove all messages of the kicked user from the group
        GroupMessage.objects.filter(group=group, sender=user_to_kick).delete()

        # Create a group message to inform about the kick
        GroupMessage.objects.create(
            group=group,
            sender=group.admin,
            message_text=f"{user_to_kick.username} got kicked by admin."
        )

        messages.success(request, f'You have kicked {user_to_kick.username} from the group.')

    return redirect('public_group_detail', group_id=group_id)



@login_required
def hide_message(request, group_id, message_id):
    update_user_activity(request)
    group = get_object_or_404(PublicGroup, pk=group_id)
    message = get_object_or_404(GroupMessage, pk=message_id)

    # Check if the user making the request is the group admin
    if request.user == group.admin:
        message.delete()

    return redirect('public_group_detail', group_id=group_id)





@login_required
def follow(request, username):
    update_user_activity(request)
    current_user_profile = request.user.userprofile
    target_user_profile = get_object_or_404(UserProfile, user__username=username)

    if not Follower.objects.filter(follower=current_user_profile, following_user_profile=target_user_profile).exists():
        Follower.objects.create(follower=current_user_profile, following_user_profile=target_user_profile)

        # Increase follower count for the target user and following count for the current user
        target_user_profile.followers_count += 1
        current_user_profile.following_count += 1

        target_user_profile.save()
        current_user_profile.save()

        # Create a new entry in the Following model
        Following.objects.create(following_user_profile=current_user_profile, follower=target_user_profile)

    return redirect('profile', username=username)

def followers_list(request, username):
    update_user_activity(request)
    user_profile = get_object_or_404(UserProfile, user__username=username)
    followers = Follower.objects.filter(following_user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'followers': followers,
    }

    return render(request, 'followers_list.html', context)

def following_list(request, username):
    update_user_activity(request)
    user_profile = get_object_or_404(UserProfile, user__username=username)
    following = Following.objects.filter(following_user_profile=user_profile)

    context = {
        'user_profile': user_profile,
        'following': following,
    }

    return render(request, 'following_list.html', context)



def online_users(request):
    # Get the current time
    current_time = timezone.now()

    # Get the user's UserActivity record, or create one if it doesn't exist
    user_activity, created = UserActivity.objects.get_or_create(user=request.user)

    # Update the last_active timestamp for the user
    user_activity.last_active = current_time
    user_activity.save()

    # Get online users (those active in the last 5 minutes)
    online_users = UserActivity.objects.filter(last_active__gte=current_time - timezone.timedelta(minutes=5))




    # Order online users by date joined in descending order
    online_users = online_users.order_by('-user__date_joined')

    # Render the template with the online users and current_time
    return render(request, 'online_users.html', {'online_users': online_users, 'current_time': current_time})



@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Update the user's last active timestamp when they log in

    UserActivity.objects.update_or_create(user=user, defaults={'last_active': timezone.now()})
    online_users = UserActivity.objects.filter(last_active__gte=timezone.now() - timezone.timedelta(minutes=5))

@receiver(pre_save, sender=User)
def user_activity_handler(sender, instance, **kwargs):
    # Update the user's last active timestamp whenever they interact with the site
    if instance.pk:
        UserActivity.objects.update_or_create(user=instance, defaults={'last_active': timezone.now()})

def update_user_activity(request):
    if request.user.is_authenticated:
        # Get the user's UserActivity record, or create one if it doesn't exist
        user_activity, created = UserActivity.objects.get_or_create(user=request.user)

        # Update the last_active timestamp for the user
        user_activity.last_active = timezone.now()
        user_activity.save()



@login_required
def unfollow(request, username):
    update_user_activity(request)
    current_user_profile = request.user.userprofile
    target_user_profile = get_object_or_404(UserProfile, user__username=username)

    # Check if there's a follower relationship to unfollow
    follower_relationship = Follower.objects.filter(follower=current_user_profile, following_user_profile=target_user_profile).first()
    if follower_relationship:
        follower_relationship.delete()

        # Decrease following count for the current user and followers count for the target user
        current_user_profile.following_count -= 1
        target_user_profile.followers_count -= 1

        current_user_profile.save()
        target_user_profile.save()

        # Update the following count for the current user
        current_user_profile.update_following_count()

        # Delete the corresponding Following entry for two-way unfollow
        Following.objects.filter(following_user_profile=current_user_profile, follower=target_user_profile).delete()
        Following.objects.filter(following_user_profile=target_user_profile, follower=current_user_profile).delete()

    return redirect('profile', username=username)


@login_required
def remove_follower(request, username):
    update_user_activity(request)
    user_profile = get_object_or_404(UserProfile, user__username=username)

    if Follower.objects.filter(follower=request.user.userprofile, following_user_profile=user_profile).exists():
        Follower.objects.filter(follower=request.user.userprofile, following_user_profile=user_profile).delete()

        # Update follower and following counts
        user_profile.followers_count -= 1
        request.user.userprofile.following_count -= 1

        user_profile.save()
        request.user.userprofile.save()

        return redirect('followers_list', username=user_profile.user.username)
    else:
        return redirect('profile', username=user_profile.user.username)


@login_required
def for_me_view(request):
    update_user_activity(request)
    user_profile = request.user.userprofile

    # Get the IDs of the users that the current user is following
    following_user_ids = Follower.objects.filter(follower=user_profile, unfollow_time=None).values_list('following_user_profile__user_id', flat=True)

    if not following_user_ids:
        # The user is not following anyone
        followed_users_posts = None
    else:
        # Get the latest 10 posts from the users that the current user is following
        followed_users_posts = Post.objects.filter(user__userprofile__user_id__in=following_user_ids).order_by('-created_at')[:10]

    context = {
        'followed_users_posts': followed_users_posts,
    }

    return render(request, 'for_me.html', context)





@login_required
def remove_all_posts(request):
    # Get the user's followed users' posts
    update_user_activity(request)
    user_profile = request.user.userprofile
    following_users = Following.objects.filter(follower=user_profile).values_list('following_user_profile', flat=True)
    followed_users_posts = Post.objects.filter(user__in=following_users)

    # Delete the posts
    followed_users_posts.delete()

    # Show a success message
    messages.success(request, 'All posts have been removed successfully.')

    # Redirect back to the for_me view
    return redirect('for_me_view')


def emoji_list(request):
    emoji_mapping = {
    '.behosh': 'behosh',
    '.chupairlarka': 'chupairlarka',
    '.chupairlarki': 'chupairlarki',
    '.cry': 'cry',
    '.kalaroye': 'kalaroye',
    '.dance': 'dance',
    '.emotionalman': 'emotionalman',
    '.femaledance': 'femaledance',
    '.getoutmale': 'getoutmale',
    '.heartattack': 'heartattack',
    '.jeetkedikha': 'jeetkedikha',
    '.jokerclap': 'jokerclap',
    '.jokerlaugh': 'jokerlaugh',
    '.2jokerlaugh': '2jokerlaugh',
    '.jokertaliyaan': 'jokertaliyaan',
    '.kissfemale': 'kissfemale',
    '.kissmale': 'kissmale',
    '.malelaugh': 'malelaugh',
    '.pankha': 'pankha',
    '.reject': 'reject',
    '.rip': 'rip',
    '.sad': 'sad',
    '.womenlaugh': 'womenlaugh',
    '.beankiss': 'beankiss',
    '.foreheadkiss': 'foreheadkiss',
    '.funnykiss': 'funnykiss',
    '.hugcouple': 'hugcouple',
    '.aglagaduga': 'aglagaduga',
    '.laughcry': 'laughcry',
    '.sleepkid': 'sleepkid',
    '.sleepmale': 'sleepmale',
    '.kill': 'kill',
    '.chura': 'chura',
    '.femalekill': 'femalekill',
    '.cold': 'cold',
    '.2cold': '2cold',
    '.beanking': 'beanking',
    '.king': 'king',
    '.queen': 'queen',
    '.love': 'love',
    '.Dostana': 'Dostana',
    '.dostana': 'dostana',
    '.garmi': 'garmi',
}


    emoji_items = list(emoji_mapping.items())  # Convert dict_items to a list of tuples
    paginator = Paginator(emoji_items, 40)  # Paginate the list
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'emoji_list.html', {'page_obj': page_obj})








def popular_groups_view(request):
    update_user_activity(request)
    popular_groups = PublicGroup.objects.annotate(num_members=Count('groupmembership')).order_by('-num_members')[:10]
    return render(request, 'popular_groups.html', {'popular_groups': popular_groups})


def private_group_view(request):
    update_user_activity(request)
    # Your view logic here
    return render(request, 'private_group.html')

def one_on_one_view(request):
    update_user_activity(request)
    # Your view logic here
    return render(request, 'one_on_one.html')

def games_view(request):
    update_user_activity(request)
    # Your view logic here
    return render(request, 'games.html')

@login_required
def send_invitation(request, recipient_id):
    recipient = User.objects.get(pk=recipient_id)

    existing_invitation = ChatInvitation.objects.filter(sender=request.user, recipient=recipient).first()

    if existing_invitation:
        messages.error(request, 'You have already sent an invitation to this user.')
    else:
        # Create a new chat invitation
        invitation = ChatInvitation(sender=request.user, recipient=recipient, status='pending')
        invitation.save()

        # Send notification to the recipient
        content = f"Apko {request.user.username} ne 1 on 1 invite bejha hai! ✨😯"
        Notification.create_invite_notification(recipient, content, sent_by=request.user)  # Updated to include sent_by field

        messages.success(request, 'Invitation sent successfully.')

    return redirect('index')

@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(ChatInvitation, id=invitation_id, recipient=request.user)
    existing_chat = OneOnOneChat.objects.filter(participants=request.user).filter(participants=invitation.sender).first()

    if not existing_chat:
        chat = OneOnOneChat.objects.create()
        chat.participants.add(request.user, invitation.sender)
    else:
        chat = existing_chat

    invitation.delete()

    # Send notification to the sender and the recipient
    content_sender = mark_safe(f"{request.user.username} ne apka 1 on 1 invite accept karlia! 🎉")
    Notification.create_accept_invite_notification(invitation.sender, content_sender, accepted_by=request.user)  # Updated to include accepted_by field


    return redirect('chat_detail', chat_id=chat.pk)

@login_required
def reject_invitation(request, invitation_id):
    invitation = get_object_or_404(ChatInvitation, id=invitation_id, recipient=request.user)
    invitation.delete()

    # Send notification to the sender
    content = f"{request.user.username} ka invite reject Kardia he 🙃."
    Notification.create_reject_invite_notification(invitation.sender, content, rejected_by=request.user)  # Updated to include rejected_by field

    return redirect('received_invitations')


def chat_detail(request, chat_id):
    update_user_activity(request)
    chat = get_object_or_404(OneOnOneChat, id=chat_id)

    # Check if the current user is a participant in the chat
    if request.user not in chat.participants.all():
        # You can handle unauthorized access here, e.g., redirect to an error page
        return render(request, 'access_denied.html')  # Create an access denied template

    # Retrieve chat messages (You'll need to define the OneOnOneMessage model)
    messages = OneOnOneMessage.objects.filter(chat=chat)

    context = {
        'chat': chat,
        'messages': messages,
    }

    return render(request, 'chat_detail.html', context)



@login_required
def received_invitations(request):
    # Query the received chat invitations for the currently logged-in user
    received_invitations = ChatInvitation.objects.filter(recipient=request.user)

    context = {
        'received_invitations': received_invitations,  # Pass the correct context variable
    }

    return render(request, 'received_invitations.html', context)

@login_required
def sent_invitations(request):
    sent_invitations = ChatInvitation.objects.filter(sender=request.user, status='pending')
    return render(request, 'sent_invitations.html', {'sent_invitations': sent_invitations})


@login_required
@require_POST
def skip_notification(request):
    notification_id = request.POST.get('notification_id')
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
    except Notification.DoesNotExist:
        pass  # Handle the case where the notification doesn't exist

    return HttpResponse(status=204)  # A success response with no content





@login_required
def send_message(request, chat_id):
    update_user_activity(request)
    chat = get_object_or_404(OneOnOneChat, id=chat_id)

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        image_name = request.POST.get('image_name', '')
        video_name = request.POST.get('video_name', '')

        error_messages = []  # To collect error messages

        if not (message_text or image or video):
            error_messages.append('No message, image, or video received.')

        # Check if the current user is a participant in the chat
        if request.user not in chat.participants.all():
            raise PermissionDenied

        # Create a new chat message
        message = OneOnOneMessage(chat=chat, sender=request.user, content=message_text)

        if image:
            # Check if the image type is valid
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                error_messages.append('Invalid image format. Valid formats: PNG, JPG, JPEG, GIF.')

            # Generate a unique name for the image
            image_name = generate_unique_name(image_name, image)
            message.image_name = image_name

            
            

        if video:
            # Check if the video type is valid
            if not video.name.lower().endswith(('.mp4', '.mov', '.avi')):
                error_messages.append('Invalid video format. Valid formats: MP4, MOV, AVI.')

            # Generate a unique name for the video
            video_name = generate_unique_name(video_name, video)
            message.video_name = video_name

            # Check if video size is less than 100 MB
            if video.size > 100 * 1024 * 1024:
                error_messages.append('Video file size exceeds 100 MB.')
            else:
                message.video = video

        if error_messages:
            # Pass error messages to the template
            context = {
                'error_messages': error_messages,
            }
            return render(request, 'chat_detail.html', {'chat_id': chat.id, 'context': context})

        # Save the message
        message.save()

        # Send notifications to both users
        participants = chat.participants.all()


    for participant in chat.participants.all():
        if participant != request.user:
            notification_content = f"Apko 1 on 1 chat me {request.user.username} ne message bejha hai."

            # Create the notification for the participant
            Notification.create_1on1_message_notification(user=participant, content=notification_content)

            # Generate the HTML for the 'Go to Chat' button
            button_html = f'<a href="{reverse("chat_detail", kwargs={"chat_id": chat.id})}" class="btn btn-primary">Go to Chat</a>'

            # Update the notification content by adding the button HTML
            notification_content_with_button = f"{notification_content}<br>{button_html}"

# Redirect back to the chat_detail view
    return redirect('chat_detail', chat_id=chat.id)



# Function to generate a unique name for a file
def generate_unique_name(base_name, file):
    ext = os.path.splitext(file.name)[1]
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{base_name}-{random_string}{ext}"



@login_required
def chat_detail(request, chat_id):
    # Retrieve the chat object
    chat = get_object_or_404(OneOnOneChat, id=chat_id)

    # Check if the current user is a participant in the chat
    if request.user not in chat.participants.all():
        # You can handle unauthorized access here, e.g., redirect to an error page
        raise PermissionDenied

    # Retrieve all chat messages for this chat in ascending order (oldest first)
    messages = OneOnOneMessage.objects.filter(chat=chat).order_by('timestamp')

    # Get all messages but display only the most recent 25
    all_messages = list(messages)
    recent_messages = all_messages[-10:]

    context = {
        'chat': chat,
        'messages': recent_messages,  # Display only the most recent 25 messages
    }

    return render(request, 'chat_detail.html', context)




@login_required
def leave_chat(request, chat_id):
    update_user_activity(request)
    chat = get_object_or_404(OneOnOneChat, id=chat_id)

    # Check if the current user is a participant in the chat
    if request.user not in chat.participants.all():
        # Handle unauthorized access, e.g., redirect to an error page
        return render(request, 'access_denied.html')

    # Check if the chat is active; if it's active, the user can leave it
    if chat.status == 'active':
        # Retrieve the other participant in the chat
        other_participant = chat.participants.exclude(id=request.user.id).first()

        # Create and save a notification for chat leave in the Notification model
        content = f"{request.user.username} ne 1 on 1 chat leave kardi hai 💔😭💔"
        Notification.create_1on1_leave_notification(user=other_participant, content=content, left_by=request.user)

        # Update the corresponding notification field for chat leave
        Notification.objects.filter(user=other_participant, content=content).update(is_1on1_leave_notification=True)

        # Remove the current user from the participants
        chat.participants.remove(request.user)

        # Check if the chat has no more participants; if so, mark it as ended
        if chat.participants.count() == 0:
            chat.status = 'ended'
            chat.save()

    # Redirect the user to their list of 1-on-1 chats or any other appropriate page
    return redirect('list_one_on_one_chats')




@login_required
def list_one_on_one_chats(request):
    update_user_activity(request)
    user = request.user
    one_on_one_chats = OneOnOneChat.objects.filter(participants=user)

    # Create a list of dictionaries with chat and other_user username
    chat_data = []
    for chat in one_on_one_chats:
        other_user = chat.participants.exclude(id=user.id).first()
        if other_user is not None:
            chat_data.append({'chat': chat, 'other_user_username': other_user.username})
        else:
            # Handle the case where other_user is None (e.g., if chat is not properly configured)
            # You can choose to skip this chat or handle it differently based on your requirements.
            pass

    context = {
        'chat_data': chat_data,
    }

    return render(request, 'list_one_on_one_chats.html', context)



@login_required
def initiate_chat(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    # Check if an active chat with the same participants already exists
    chat = OneOnOneChat.objects.filter(participants=request.user).filter(participants=recipient).filter(status='active').first()

    if not chat:
        # If no active chat exists, create one
        chat = OneOnOneChat.objects.create()
        chat.participants.add(request.user, recipient)

    # Create a chat invitation (you may want to implement this)
    ChatInvitation.objects.create(sender=request.user, recipient=recipient)

    # Redirect to the chat detail view
    return redirect('chat_detail', chat_id=chat.id)



def text_posts_view(request):
    text_posts = Post.objects.filter(Q(picture__isnull=True) | Q(video__isnull=True) | Q(picture='')).order_by('-created_at')
    paginator = Paginator(text_posts, 5)  # Display 5 text posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'text_posts.html', {'page_obj': page_obj})





def picture_posts_view(request):
    picture_posts = Post.objects.exclude(picture__isnull=True).exclude(picture__exact='').order_by('-created_at')
    paginator = Paginator(picture_posts, 5)  # Display 5 picture posts per page
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'picture_posts.html', {'page': page})

def video_posts_view(request):
    video_posts = Post.objects.exclude(video__exact='').order_by('-created_at')
    paginator = Paginator(video_posts, 5)  # Display 5 videos per page
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'video_posts.html', {'page': page})





