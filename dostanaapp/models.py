from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from dostana.celery import process_uploaded_photo


from django.contrib.auth import get_user_model

class SiteConfiguration(models.Model):
    signup_enabled = models.BooleanField(default=True)  # Add this field to enable or disable signup

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('engineer', 'Engineer'),
        ('doctor', 'Doctor'),
        ('business', 'Business'),
        ('other', 'Other'),
    ]

    PHOBIAS_CHOICES = [
        ('heights', 'Heights'),
        ('spiders', 'Spiders'),
        ('public-speaking', 'Public Speaking'),
        ('flying', 'Flying'),
        ('clowns', 'Clowns'),
        # Add more phobia choices as needed
    ]

    CAST_CHOICES = [
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
        # Add more cast choices as needed
    ]



    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    scores = models.IntegerField(
    default=1,
    help_text="User scores",)

    ban = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_activity_log = models.TextField(blank=True, null=True)  # Store user activity log
    marital_status = models.CharField(max_length=20, default='ghershadishuda')
    star = models.CharField(max_length=50, default='Virgo')
    about = models.TextField(default='i love dostana')
    age = models.PositiveIntegerField(default=14)
    city = models.CharField(max_length=100, default='dostana')
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    # Additional fields for latitude and longitude
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_private = models.BooleanField(default=False)

    date_of_birth = models.DateField(default='2002-09-11', blank=True, null=True)
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, default='student')
    phobias = models.CharField(max_length=20, choices=PHOBIAS_CHOICES, default='')
    cast = models.CharField(max_length=20, choices=CAST_CHOICES, default='general')
    father_name = models.CharField(max_length=100, default='')
    father_occupation = models.CharField(max_length=100, default='')
    father_qualification = models.CharField(max_length=100, default='')
    num_brothers = models.PositiveIntegerField(default=0)
    num_sisters = models.PositiveIntegerField(default=0)
    father_income_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    father_income_yearly = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    personal_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    email = models.EmailField(max_length=100, default='example@example.com')
    phone_number = models.CharField(max_length=15, default='+920000000000')
    watcher_purchased = models.BooleanField(default=False)
    watcher_expiration_date = models.DateTimeField(null=True, blank=True)
    watcher_duration = models.PositiveIntegerField(default=1)  # Default duration is 1 day

    HAD_SEX_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    had_sex = models.CharField(max_length=3, choices=HAD_SEX_CHOICES, default='No')
    HAD_FIRST_KISS_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    had_first_kiss = models.CharField(max_length=3, choices=HAD_FIRST_KISS_CHOICES, default='No')



    def __str__(self):
        return self.user.username

    def update_followers_count(self):
        self.followers_count = self.followers.all().count()
        self.save()

    def update_following_count(self):
        self.following_count = self.followings.count()
        self.save()


class DeviceInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255)
    user_agent = models.TextField()
    fingerprint = models.TextField()
    ip_address = models.GenericIPAddressField()

    # Add a new field
    new_field = models.BooleanField(default=False)

    def __str__(self):
        return f'Device Info for {self.user.username}'

class Post(models.Model):
    POST_TYPE_CHOICES = (
        ('Text', 'Text'),
        ('Picture', 'Picture'),
        ('Video', 'Video'),
    )
    

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='Text')
    content = models.TextField()
    picture = models.ImageField(upload_to='post_pictures/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    disliked_by = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
     # New fields to disable taliyaan and chupair
    last_post_delete_time = models.DateTimeField(null=True, blank=True)
    replies_allowed = models.BooleanField(default=True)
    disable_taliyaan = models.BooleanField(default=False)
    disable_chupair = models.BooleanField(default=False)
    last_post_created_at = models.DateTimeField(null=True, blank=True)
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'post_id': self.id})

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.picture:
            # Call Celery task for photo processing
            process_uploaded_photo.delay(self.picture.path)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id} at {self.created_at}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration_choices = (
        (1, '1 Din'),  # 1 Day
        (2, '2 Din'),  # 2 Days
        (3, '3 Din'),  # 3 Days
    )
    duration = models.PositiveIntegerField(choices=duration_choices, default=1)
    price_in_points = models.PositiveIntegerField()  # No default price

    def __str__(self):
        return self.name
# Create a "Watcher" product instance in the database



class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    hidden = models.BooleanField(default=False)

    # Add a field to track the timestamp of the last sent reply
    last_sent_reply = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reply by {self.user.username} on Post {self.post.id} at {self.created_at}"

    @property
    def reply_count_total(self):
        count = self.child_replies.count()
        for child_reply in self.child_replies.all():
            count += child_reply.reply_count_total
        return count



User = get_user_model()

class PublicGroup(models.Model):
    title = models.CharField(max_length=40)
    rules = models.TextField(max_length=300)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', default=None)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(PublicGroup, on_delete=models.CASCADE)
    member = models.BooleanField(default=False)  # New field to indicate group membership
    kicked = models.BooleanField(default=False)
    kicked_until = models.DateTimeField(null=True, blank=True)
    last_message_timestamp = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} in {self.group.title}"


class GroupMessage(models.Model):
    group = models.ForeignKey(PublicGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.TextField()  # Text of the message
    image = models.ImageField(upload_to='group_images/', blank=True, null=True)  # Image attached to the message
    timestamp = models.DateTimeField()

    # Add a new field to store the timestamp of the last sent message by the same sender in the same group
    last_message_timestamp = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.timestamp:
            # Set the timestamp to the current time if it's not set
            self.timestamp = timezone.now()

        # Update the last_message_timestamp field with the current timestamp when saving
        self.last_message_timestamp = self.timestamp

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message by {self.sender.username} in {self.group.title}"


@classmethod
def retain_latest_messages(cls, group):
    # Get the IDs of the latest 25 messages for the group
    latest_message_ids = cls.objects.filter(group=group).order_by('-timestamp')[:25].values_list('id', flat=True)

    # Delete older messages for the group
    cls.objects.filter(group=group).exclude(id__in=latest_message_ids).delete()

class OneOnOneChat(models.Model):
    participants = models.ManyToManyField(User, related_name='one_on_one_chats')
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('ended', 'Ended')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat #{self.id}'

    def get_other_participant(self, user):
        # Determine and return the other participant in the chat
        participants = self.participants.all()
        if user in participants:
            return participants.exclude(id=user.id).first()
        else:
            # Handle the case where the user is not a participant in this chat
            return None



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Fields for group-related notifications
    is_group_notification = models.BooleanField(default=False)
    group = models.ForeignKey(PublicGroup, on_delete=models.CASCADE, null=True, blank=True)
    group_message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, null=True, blank=True)

    # New fields for different notification types
    is_1on1_message_notification = models.BooleanField(default=False)
    is_invite_notification = models.BooleanField(default=False)
    is_accept_invite_notification = models.BooleanField(default=False)
    is_reject_invite_notification = models.BooleanField(default=False)
    is_1on1_chat_notification = models.BooleanField(default=False)

    sent_by = models.ForeignKey(User, related_name='sent_by', on_delete=models.CASCADE, null=True, blank=True)
    accepted_by = models.ForeignKey(User, related_name='accepted_by', on_delete=models.CASCADE, null=True, blank=True)
    rejected_by = models.ForeignKey(User, related_name='rejected_by', on_delete=models.CASCADE, null=True, blank=True)
    is_1on1_leave_notification = models.BooleanField(default=False)
    left_by = models.ForeignKey(User, related_name='left_by', on_delete=models.CASCADE, null=True, blank=True)
    is_1on1_message_notification = models.BooleanField(default=False)
    one_on_one_chat = models.ForeignKey(OneOnOneChat, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"Notification for {self.post} ({self.timestamp})"



@classmethod
def retain_latest_notifications(cls, user):
        # Get the IDs of the latest 10 notifications for the user
            latest_notification_ids = cls.objects.filter(user=user).order_by('-timestamp')[:10].values_list('id', flat=True)

        # Delete older notifications for the user that are not in the latest list
            cls.objects.filter(user=user).exclude(id__in=latest_notification_ids).delete()



    # Add a method to create group notifications
@classmethod
def create_group_notification(cls, user, group, group_message, content):
        return cls.objects.create(
            user=user,
            is_group_notification=True,
            group=group,
            group_message=group_message,
            content=content
        )
@classmethod
def create_1on1_leave_notification(cls, user, content, left_by=None):
        return cls.objects.create(
            user=user,
            is_1on1_leave_notification=True,
            content=content,
            left_by=left_by
        )
    # Methods to create different types of notifications
@classmethod
def create_1on1_message_notification(cls, user, content):
        return cls.objects.create(
            user=user,
            is_1on1_message_notification=True,
            content=content
        )

@classmethod
def create_invite_notification(cls, user, content, sent_by=None):
        return cls.objects.create(
        user=user,
        is_invite_notification=True,
        content=content,
        sent_by=sent_by
    )

@classmethod
def create_accept_invite_notification(cls, user, content, accepted_by=None):
        return cls.objects.create(
        user=user,
        is_accept_invite_notification=True,
        content=content,
        accepted_by=accepted_by  # Include the accepted_by field when creating the notification
    )


@classmethod
def create_reject_invite_notification(cls, user, content, rejected_by=None):
        return cls.objects.create(
        user=user,
        is_reject_invite_notification=True,
        content=content,
        rejected_by=rejected_by
    )
@classmethod
def create_1on1_chat_notification(cls, user, content):
        return cls.objects.create(
            user=user,
            is_1on1_chat_notification=True,
            content=content
        )




User = get_user_model()
class Follower(models.Model):
    follower = models.ForeignKey(UserProfile, related_name='followers', on_delete=models.CASCADE)
    following_user_profile = models.ForeignKey(UserProfile, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    unfollow_time = models.DateTimeField(null=True, blank=True)  # Field to store unfollow time

    def unfollow(self):
        self.unfollow_time = timezone.now()
        self.save()

class Following(models.Model):
    following_user_profile = models.ForeignKey(UserProfile, related_name='followings', on_delete=models.CASCADE)
    follower = models.ForeignKey(UserProfile, related_name='following_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    unfollow_time = models.DateTimeField(null=True, blank=True)  # Field to store unfollow time

    def unfollow(self):
        self.unfollow_time = timezone.now()
        self.save()


class UnfollowLog(models.Model):
    unfollow_user = models.ForeignKey(UserProfile, related_name='unfollowed', on_delete=models.CASCADE)
    unfollow_target = models.ForeignKey(UserProfile, related_name='unfollowed_by', on_delete=models.CASCADE)
    unfollow_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.unfollow_user.user.username} unfollowed {self.unfollow_target.user.username} at {self.unfollow_time}"

class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username



class ChatInvitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])
    accepted = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"Chat Invitation from {self.sender.username} to {self.recipient.username}"

class OneOnOneMessage(models.Model):
    chat = models.ForeignKey(OneOnOneChat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    video = models.FileField(upload_to='chat_videos/', blank=True, null=True)

    def __str__(self):
        return f'Message #{self.id}'



