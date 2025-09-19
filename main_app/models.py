from django.db import models
from django.contrib.auth.models import User

class Interest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Respondent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    interests = models.ManyToManyField(Interest, blank=True)
    image = models.ImageField(upload_to='respondents/', null=True, blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pub_date = models.DateTimeField("date published")
    
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Response(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.respondent.name} → {self.choice.choice_text}"
