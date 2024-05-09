from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from accounts.models import User
from django.conf import settings

class News(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # foreign key를 통해 News와 User 모델 연결
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="news")

    # 좋아요를 누른 유저를 찾기 위해 MtoN 관계 이용
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_news")

    # url 필드
    url = models.CharField(max_length=200, validators=[URLValidator()])

    # url 필드 validation
    def clean(self):
        super().clean()
        if not self.image_url.startswith("http://") and not self.image_url.startswith("https://"):
            raise ValidationError("Invalid URL.")

class Comment(models.Model):
    # foreign key를 통해 News와 Comment 모델 연결
    news = models.ForeignKey(
        News, on_delete=models.CASCADE, related_name="comments"    
    )

    # foreign key를 통해 Comment와 User 모델 연결
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="comments")

    # 좋아요를 누른 유저를 찾기 위해 MtoN 관계 이용
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_comments")
    
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)