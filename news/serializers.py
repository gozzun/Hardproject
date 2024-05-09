from rest_framework import serializers
from .models import News, Comment
from django.contrib.auth.models import User
from django.utils.timezone import now

class CommentSerializer(serializers.ModelSerializer):
    # 좋아요 개수 필드
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("news","user","like_users")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop("news")
        return ret
    
    # 좋아요 개수 세는 함수
    def get_like_count(self, instance):
        return instance.like_users.count()

class NewsSerializer(serializers.ModelSerializer):
    # 좋아요 개수 필드
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = "__all__"
        read_only_fields = ('user', 'like_users')

    # 좋아요 개수 세는 함수
    def get_like_count(self, instance):
        return instance.like_users.count()

class NewsDetailSerializer(NewsSerializer):
    # 댓글 필드(뉴스 디테일 페이지에만 존재)
    comments = CommentSerializer(many=True, read_only=True)

    # 댓글 개수 필드
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
