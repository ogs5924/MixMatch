from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from heapq import nsmallest
from typing import Dict

from .model_managers import UserManager

# Create your models here.


class Hobby(models.Model):
    TYPES = (
        ("Indoor", "Indoor"),
        ("Outdoor", "Outdoor"),
        ("Collection", "Collection"),
        ("Competitive", "Competitive"),
    )
    name = models.CharField('Hobby Name', max_length=255, blank=False, unique=True)
    type = models.CharField('Hobby Type', max_length=30, blank=False, choices=TYPES)

    def __str__(self):
        return "%s - %s" % (self.name, self.type)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model extending Django's AbstractBaseUser.
    Removes the username property and uses an email to log in instead.
    """
    # default choices
    GENDERS = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other")
    )
    # Fields to include in DB
    username = models.CharField('username', unique=True, max_length=30)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', unique=True, blank=True)
    # phone_regex = RegexValidator(regex=r'^0\d{10}$', message="Phone number must be entered. 11 Digits.")
    # phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False)
    dp = models.ImageField(upload_to='display_pictures/', null=True, blank=True)
    dob = models.DateField('Date of Birth', blank=True, null=True)
    gender = models.CharField('Gender', max_length=30, choices=GENDERS, null=True)
    hobbies = models.ManyToManyField(Hobby, blank=True, related_name="users")
    friends = models.ManyToManyField("self")

    objects = UserManager()

    USERNAME_FIELD = 'username'  # Necessary for IDing necessary Field
    REQUIRED_FIELDS = ['first_name', 'last_name']  # List of field names that will be prompted when creating superuser.

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Gets the full name of the user object.
        :return: first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Gets the shorten variant of the name of the user object.
        :return: Short name for the user.
        """
        return self.first_name

    def email_user(self, subject, msg, from_email=None, **kwargs):
        """
        Sends an email to THIS user.
        :param subject: Subject of the email.
        :param msg: Body of the email.
        :param from_email: Email address of sender.
        :param kwargs: additional args.
        :return: Nothing
        """
        send_mail(subject, msg, from_email, [self.email], **kwargs)

    def get_friends_with_similar_hobbies(self, top_k: int = 10):
        users = self.friends.all()
        my_hobbies = self.hobbies.all()
        ranked = {}
        for user in users:
            if user.username is not self.username:
                friend_hobbies = user.hobbies.all()
                score = 0
                for hobby in friend_hobbies:
                    if hobby in my_hobbies:
                        score += 1
                ranked[user] = score
        return [(friend, ranked[friend]) for friend in sorted(ranked, key=ranked.get, reverse=True)][:top_k]


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    time_sent = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # check sender cannot also be recipient
        if self.sender.username == self.recipient.username:
            raise ValidationError("Sender cannot send message to self!")
        elif self.content == '' or self.content is None:
            raise ValueError("Message content cannot be empty!")

        super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return "Message from %s to %s" % (self.sender.username.capitalize(), self.recipient.username.capitalize())


class PendingRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests")

    def respond(self, approve_or_decline):  # True for approve
        if approve_or_decline:
            self.sender.friends.add(self.recipient)
        self.delete()

    def __str__(self):
        return "Friend Request from %s to %s" % (self.sender.username.capitalize(),
                                                 self.recipient.username.capitalize())
