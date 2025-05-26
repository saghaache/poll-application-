from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

class Poll(models.Model):
    TYPE_VOTE_CHOICES = [
        ('unique', 'Vote unique'),
        ('multiple', 'Vote multiple'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    vote_type = models.CharField(max_length=20, choices=TYPE_VOTE_CHOICES)

    def __str__(self):
        return self.title

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def has_started(self):
        return timezone.now() >= self.start_date

class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    options = models.ManyToManyField(Option)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')
