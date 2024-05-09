from django.urls import path
from . import views

app_name = 'news'
urlpatterns=[
    path("", views.NewsListAPIView.as_view(), name="news_list"),
    path("search/<str:search>/", views.search, name="search"),

    path("latest/", views.latest, name="latest"),
    path("liked/", views.liked, name="liked"),
    path("comment/", views.comment, name="comment"),
    
    path("<int:newsId>/", views.NewsDetailAPIView.as_view(), name="news_detail"),
    path("<int:newsId>/like/", views.NewsLikeAPIView.as_view(), name="news_like"),
    path("<int:newsId>/comment/", views.CommentListAPIView.as_view(), name="comment_list"),

    path("comment/<int:commentId>/", views.CommentDetailAPIView.as_view(), name="comment_detail"),
    path("comment/<int:commentId>/like/", views.CommentLikeAPIView.as_view(), name="comment_like"),
    path("comment/search/<str:search>/",views.comment_search, name="comment_search"),
]