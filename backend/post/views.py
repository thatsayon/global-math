from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from django.db.models import Count, Case, When, IntegerField, Value, F, Q
from django.db.models.functions import Coalesce, Random
from django.utils import timezone

from datetime import timedelta

from core.pagination import (
    PostFeedPagination,
    CommentPagination,
)

from .serializers import (
    PostSerializer,
    PostFeedSerializer,
    CommentSerializer
)
from .models import (
    PostModel,
    PostReaction,
    CommentModel,
    CommentReaction,
    PostView,
)

class PostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"msg": "post saved successfully"},
            status=status.HTTP_200_OK
        )

class PostDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        # Limit queryset to authenticated user's posts only
        return PostModel.objects.filter(user=self.request.user)

    def get_object(self):
        obj = super().get_object()

        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")

        return obj


class PostFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_levels = user.math_levels.values_list("id", flat=True)

        recent_cutoff = timezone.now() - timedelta(hours=6)
        recently_seen = PostView.objects.filter(
            user=user,
            viewed_at__gte=recent_cutoff
        ).values_list("post_id", flat=True)

        def base_queryset(exclude_seen=True):
            qs = (
                PostModel.objects
                .filter(classroom__isnull=True)
                .select_related("user", "post_level")
                .annotate(
                    like_count=Count("reactions", filter=Q(reactions__reaction="like")),
                    comment_count=Count("comments"),
                )
                .annotate(
                    engagement_score=F("like_count") * 2 + F("comment_count") * 3,
                    topic_score=Case(
                        When(post_level_id__in=user_levels, then=Value(30)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                    verified_score=Case(
                        When(is_verified=True, then=Value(10)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                    media_score=Case(
                        When(image__isnull=False, then=Value(5)),
                        When(video__isnull=False, then=Value(5)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                    random_jitter=Random() * 3,
                )
                .annotate(
                    rank_score=(
                        F("topic_score")
                        + F("verified_score")
                        + F("media_score")
                        + F("engagement_score")
                        + F("random_jitter")
                    )
                )
                .order_by("-rank_score", "-created_at")
            )

            if exclude_seen:
                qs = qs.exclude(id__in=recently_seen)

            return qs

        # -----------------------------
        # Primary attempt (exclude seen)
        # -----------------------------
        queryset = base_queryset(exclude_seen=True)

        # -----------------------------
        # FALLBACK: nothing left → relax exclusion
        # -----------------------------
        if not queryset.exists():
            queryset = base_queryset(exclude_seen=False)

        paginator = PostFeedPagination()
        page = paginator.paginate_queryset(queryset, request)

        # Track views AFTER pagination
        PostView.objects.bulk_create(
            [PostView(user=user, post=post) for post in page],
            ignore_conflicts=True
        )

        serializer = PostFeedSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)

#
# class PostFeedView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get(self, request):
#         posts = (
#             PostModel.objects
#             .filter(classroom__isnull=True)   
#             .select_related("user", "post_level")
#             .order_by("-created_at")
#         )
#
#         paginator = PostFeedPagination()
#         result_page = paginator.paginate_queryset(posts, request)
#
#         serializer = PostFeedSerializer(
#             result_page,
#             many=True,
#             context={"request": request}
#         )
#
#         return paginator.get_paginated_response(serializer.data)
#
class PostLikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        reaction_type = request.data.get('reaction')  

        if reaction_type not in ['like', 'dislike']:
            return Response(
                {"error": "Invalid reaction type"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        reaction, created = PostReaction.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'reaction': reaction_type}
        )

        if not created:
            if reaction.reaction == reaction_type:
                reaction.delete()
                message = f"{reaction_type} removed"
            else:
                reaction.reaction = reaction_type
                reaction.save()
                message = f"Changed reaction to {reaction_type}"
        else:
            message = f"{reaction_type} added"

        return Response(
            {"message": message},
            status=status.HTTP_200_OK
        )


class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        comments = post.comments.all().order_by('-created_at')
        paginator = CommentPagination()
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

class CommentReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            comment = CommentModel.objects.get(id=comment_id)
        except CommentModel.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        reaction_type = request.data.get("reaction")
        if reaction_type not in ["like", "dislike"]:
            return Response({"error": "Invalid reaction type"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        existing_reaction = CommentReaction.objects.filter(comment=comment, user=user).first()

        if existing_reaction:
            if existing_reaction.reaction == reaction_type:
                existing_reaction.delete()
                message = f"{reaction_type} removed"
            else:
                existing_reaction.reaction = reaction_type
                existing_reaction.save()
                message = f"Changed to {reaction_type}"
        else:
            CommentReaction.objects.create(comment=comment, user=user, reaction=reaction_type)
            message = f"{reaction_type} added"

        like_count = comment.reactions.filter(reaction="like").count()
        dislike_count = comment.reactions.filter(reaction="dislike").count()

        return Response({
            "message": message,
            "comment_id": str(comment.id),
            "like_count": like_count,
            "dislike_count": dislike_count,
            "user_reaction": reaction_type if "added" in message or "Changed" in message else None
        }, status=status.HTTP_200_OK)

