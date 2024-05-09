from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import News, Comment
from .serializers import NewsSerializer, NewsDetailSerializer, CommentSerializer


# 뉴스 목록
class NewsListAPIView(APIView):
    # 뉴스 목록 조회
    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)

    # 뉴스 생성
    @permission_classes([IsAuthenticated])
    def post(self, request):
        title = request.data.get("title")
        content = request.data.get("content")
        url = request.data.get("url")

        # 제목, 내용, url 중 하나라도 비면 에러 발생
        if not (title and content and url):
            return Response({"error": "title, content, url is required"}, status=400)

        url_validator = URLValidator()

        # URLValidator를 통해 url validation 진행
        try:
            url_validator(url)
        except ValidationError:
            return Response({"error": "Invalid URL"}, status=400)

        news = News.objects.create(
            user=request.user,
            title=title,
            content=content,
            url=url
        )

        serializer = NewsSerializer(news)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 뉴스 검색
@api_view(['GET'])
def search(request, search):
    # 제목, 내용, url, 유저네임 중 겹치면 보여줌.
    news_list = News.objects.filter(
        Q(title__icontains=search) |
        Q(content__icontains=search) |
        Q(url__icontains=search) |
        Q(user__username__icontains=search)
    )

    serializer = NewsSerializer(news_list, many=True)

    return Response(serializer.data)


# 최신순 정렬
@api_view(['GET'])
def latest(request):
    news_list = News.objects.order_by('-created_at')
    serializer = NewsSerializer(news_list, many=True)
    return Response(serializer.data)


# 좋아요순 정렬
@api_view(['GET'])
def liked(request):
    # 좋아요 개수가 같다면 최신순으로 정렬
    news_list = News.objects.annotate(like_count=Count(
        'like_users')).order_by('-like_count', '-created_at')
    serializer = NewsSerializer(news_list, many=True)
    return Response(serializer.data)


# 댓글순 정렬
@api_view(['GET'])
def comment(request):
    # 댓글 개수가 같다면 최신순으로 정렬
    news_list = News.objects.annotate(comments_count=Count(
        'comments')).order_by('-comments_count', '-created_at')

    # 뉴스 데이터에 comments_count 추가하여 보여줌.
    serialized_data = []
    for news in news_list:
        data = NewsSerializer(news).data
        data['comments_count'] = news.comments_count
        serialized_data.append(data)

    return Response(serialized_data)


# 뉴스 디테일 페이지
class NewsDetailAPIView(APIView):
    def get_object(self, newsId):
        return get_object_or_404(News, pk=newsId)

    # 뉴스 디테일 조회
    def get(self, request, newsId):
        news = self.get_object(newsId)
        serializer = NewsDetailSerializer(news)
        return Response(serializer.data)

    # 뉴스 수정
    @permission_classes([IsAuthenticated])
    def put(self, request, newsId):
        user = request.user
        news = self.get_object(newsId)

        # 뉴스 수정을 요청한 유저가 해당 뉴스를 생성한 유저와 같을 경우에만 수정
        if user == news.user:
            serializer = NewsDetailSerializer(
                news, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):

                serializer.save()

                return Response(serializer.data)

        return Response({"error": "You are not the author of this news"}, status=status.HTTP_403_FORBIDDEN)

    # 뉴스 삭제
    @permission_classes([IsAuthenticated])
    def delete(self, request, newsId):
        user = request.user
        news = self.get_object(newsId)

        # 뉴스 삭제를 요청한 유저가 해당 뉴스를 생성한 유저와 같을 경우에만 삭제
        if user == news.user:

            news.delete()

            data = {"pk": f"{newsId} is deleted."}

            return Response(data, status=status.HTTP_200_OK)

        return Response({"error": "You are not the author of this news"}, status=status.HTTP_403_FORBIDDEN)


# 뉴스 좋아요
class NewsLikeAPIView(APIView):
    # 해당 뉴스에 좋아요를 누른 유저 출력
    def get(self, request, newsId):
        news = get_object_or_404(News, pk=newsId)
        like_users = news.like_users.all()
        usernames = [user.username for user in like_users]
        return Response({"like_users": usernames})

    # 뉴스 좋아요
    @permission_classes([IsAuthenticated])
    def post(self, request, newsId):
        news = get_object_or_404(News, pk=newsId)
        user = request.user

        # 이미 좋아요를 누른 유저는 에러 발생
        if user in news.like_users.all():
            return Response({"error": "You have already liked this news."}, status=status.HTTP_400_BAD_REQUEST)

        news.like_users.add(user)

        return Response({"success": "You liked the news."}, status=status.HTTP_201_CREATED)

    # 뉴스 좋아요 삭제
    @permission_classes([IsAuthenticated])
    def delete(self, request, newsId):
        news = get_object_or_404(News, pk=newsId)
        user = request.user

        # 좋아요를 누르지 않은 유저는 에러 발생
        if user not in news.like_users.all():
            return Response({"error": "You have not liked this news."}, status=status.HTTP_400_BAD_REQUEST)

        news.like_users.remove(user)

        return Response({"success": "You unliked the news."}, status=status.HTTP_204_NO_CONTENT)


# 댓글 목록
class CommentListAPIView(APIView):
    def get_news(self, news_id):
        return get_object_or_404(News, pk=news_id)

    # 해당 뉴스의 댓글 목록 조회
    def get(self, request, newsId):
        news = self.get_news(newsId)
        comments = Comment.objects.filter(news=news)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    # 해당 뉴스에 댓글 작성
    @permission_classes([IsAuthenticated])
    def post(self, request, newsId):
        news = self.get_news(newsId)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            content = serializer.validated_data.get('content')

            # 댓글이 비어있으면 에러 발생
            if not content.strip():
                raise ValidationError("Comment content cannot be empty")

            serializer.save(user=request.user, news=news)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 댓글 디테일 페이지
class CommentDetailAPIView(APIView):
    def get_comment(self, comment_id):
        return get_object_or_404(Comment, pk=comment_id)

    # 댓글 디테일 조회
    def get(self, request, commentId):
        comment = self.get_comment(commentId)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    # 댓글 수정
    @permission_classes([IsAuthenticated])
    def put(self, request, commentId):
        comment = self.get_comment(commentId)

        # 댓글 수정을 요청한 유저가 해당 댓글을 작성한 유저와 다르면 에러 발생
        if comment.user != request.user:
            return Response({"error": "You are not the author of this comment"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(
            comment, data=request.data, partial=True)

        if serializer.is_valid():
            content = serializer.validated_data.get('content')

            # 댓글이 비어있으면 에러 발생
            if not content.strip():
                raise ValidationError("Comment content cannot be empty")

            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 삭제
    @permission_classes([IsAuthenticated])
    def delete(self, request, commentId):
        comment = self.get_comment(commentId)

        # 댓글 삭제를 요청한 유저가 해당 댓글을 작성한 유저와 다르면 에러 발생
        if comment.user != request.user:
            return Response({"error": "You are not the author of this comment"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()

        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# 댓글 좋아요
class CommentLikeAPIView(APIView):
    # 해당 댓글에 좋아요를 누른 유저 출력
    def get(self, request, commentId):
        comment = get_object_or_404(Comment, pk=commentId)
        like_users = comment.like_users.all()
        usernames = [user.username for user in like_users]

        return Response({"like_users": usernames})

    # 댓글 좋아요
    @permission_classes([IsAuthenticated])
    def post(self, request, commentId):
        comment = get_object_or_404(Comment, pk=commentId)
        user = request.user

        # 이미 좋아요를 누른 유저는 에러 발생
        if user in comment.like_users.all():
            return Response({"error": "You have already liked this comment."}, status=status.HTTP_400_BAD_REQUEST)

        comment.like_users.add(user)

        return Response({"success": "You liked the comment."}, status=status.HTTP_201_CREATED)

    # 댓글 좋아요 삭제
    @permission_classes([IsAuthenticated])
    def delete(self, request, commentId):
        comment = get_object_or_404(Comment, pk=commentId)
        user = request.user

        # 좋아요를 누르지 않은 유저는 에러 발생
        if user not in comment.like_users.all():
            return Response({"error": "You have not liked this comment."}, status=status.HTTP_400_BAD_REQUEST)

        comment.like_users.remove(user)

        return Response({"success": "You unliked the comment."}, status=status.HTTP_204_NO_CONTENT)


# 댓글 검색
@api_view(['GET'])
def comment_search(request, search):
    # 내용, 유저네임 중 겹치면 보여줌.
    comments = Comment.objects.filter(
        Q(content__icontains=search) |
        Q(user__username__icontains=search)
    )

    serializer = CommentSerializer(comments, many=True)

    return Response(serializer.data)
