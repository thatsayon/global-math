from django.urls import path
from .views import (
    PostCreateView,
    PostDeleteView,
    PostFeedView,
    PostLikeDislikeView,
    CommentView,
    CommentReactionView,
)
    
urlpatterns = [
    path('create/', PostCreateView.as_view(), name='Post'),
    path('feed/', PostFeedView.as_view(), name='Post List'),
    path('delete/<uuid:post_id>/', PostDeleteView.as_view(), name='Post Delete'),
    path('react/<post_id>/', PostLikeDislikeView.as_view(), name='React'),
    path('comment/<post_id>/', CommentView.as_view(), name='React'),
    path('comment-react/<comment_id>/', CommentReactionView.as_view(), name='Comment React'),
]
