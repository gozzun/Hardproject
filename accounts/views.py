from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer

from news.models import News, Comment
from news.serializers import NewsSerializer, CommentSerializer


# 회원가입
@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        password = serializer.validated_data.get('password')

        # validate_password를 통해 패스워드 검증
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # 패스워드를 해시화하여 저장함.
        hashed_password = make_password(password)
        serializer.validated_data['password'] = hashed_password

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 유저 디테일 페이지
class UserDetailAPIView(APIView):
    def get_object(self, username):
        return get_object_or_404(User, username=username)

    # 유저 정보 조회
    def get(self, request, username):
        user = self.get_object(username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # 회원 정보 수정
    @permission_classes([IsAuthenticated])
    def put(self, request, username):
        user = self.get_object(username)

        # 회원 정보 수정을 요청한 유저가 해당 유저와 다르면 에러 발생
        if request.user != user:
            return Response({"error": "You are not authorized to update this user."}, status=status.HTTP_403_FORBIDDEN)

        # 유저네임, 패스워드 중 원하는 정보 선택하여 수정 가능
        serializer = UserSerializer(user, data=request.data, partial=True)

        new_password = serializer.initial_data.get('password')

        # validate_password를 통해 패스워드 검증
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if new_password:

            # check_password를 통해 현재 패스워드와 새 패스워드가 같을 때 에러 발생
            if user.check_password(new_password):
                return Response({"error": "You cannot use the same password."}, status=status.HTTP_400_BAD_REQUEST)

            # 패스워드를 해시화하여 저장함.
            hashed_password = make_password(new_password)
            serializer.initial_data['password'] = hashed_password

        new_username = serializer.initial_data.get('username')

        # 현재 유저네임과 새 유저네임이 같을 때 에러 발생
        if new_username and new_username == user.username:
            return Response({"error": "You cannot use the same username."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원 탈퇴
    @permission_classes([IsAuthenticated])
    def delete(self, request, username):
        user = self.get_object(username)

        # 탈퇴를 요청한 유저와 유저네임이 같을 경우에만 탈퇴
        if request.user != user:
            return Response({"error": "You are not authorized to delete this user."}, status=status.HTTP_403_FORBIDDEN)

        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# 내가 작성한 뉴스,댓글 조회
def my(request, username):
    user = get_object_or_404(User, username=username)

    # 내가 작성한 뉴스, 댓글 가져옴.
    my_news = News.objects.filter(user=user)
    my_comments = Comment.objects.filter(user=user)

    news_serializer = NewsSerializer(my_news, many=True)
    comment_serializer = CommentSerializer(my_comments, many=True)

    # response_data에 뉴스, 댓글 정보를 한번에 담아 JSON 데이터로 전송.
    response_data = {
        'my_news': news_serializer.data,
        'my_comments': comment_serializer.data
    }

    return JsonResponse(response_data)


# 좋아요 누른 뉴스,댓글 조회
def like(request, username):
    user = get_object_or_404(User, username=username)

    # 좋아요 누른 뉴스, 댓글 가져옴.
    liked_news = News.objects.filter(like_users=user)
    liked_comments = Comment.objects.filter(like_users=user)

    news_serializer = NewsSerializer(liked_news, many=True)
    comment_serializer = CommentSerializer(liked_comments, many=True)

    # response_data에 뉴스, 댓글 정보를 한번에 담아 JSON 데이터로 전송.
    response_data = {
        'like_news': news_serializer.data,
        'like_comments': comment_serializer.data
    }

    return JsonResponse(response_data)