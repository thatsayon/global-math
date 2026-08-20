from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied

from django.db.models import Q
from django.utils import timezone

from core.pagination import CommentPagination

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
    PostNotInterested,
    Notification,
    FCMDevice,
)
from asgiref.sync import async_to_sync
from core.utils import send_push_notification

def emit_notification_to_socket(notif_instance):
    try:
        from messaging.socket import sio, user_sid_map
        user_id = str(notif_instance.user.id)
        recipient_sid = user_sid_map.get(user_id)
        if recipient_sid:
            payload = {
                "id": notif_instance.id,
                "title": notif_instance.title,
                "description": notif_instance.description,
                "date_time": notif_instance.created_at.isoformat(),
                "isRead": notif_instance.is_read,
            }
            async_to_sync(sio.emit)("new_notification", payload, to=recipient_sid)
    except Exception as e:
        print("Failed to emit notification:", e)




class PostDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostModel.objects.all()
    serializer_class = PostFeedSerializer
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        user = self.request.user
        user_levels = user.math_levels.values_list("id", flat=True)
        from messaging.models import BlockUser
        from django.db.models import Q
        blocked_users = BlockUser.objects.filter(blocker=user).values_list('blocked_user_id', flat=True)
        blocking_users = BlockUser.objects.filter(blocked_user=user).values_list('blocker_id', flat=True)
        return PostModel.objects.exclude(user_id__in=blocked_users).exclude(user_id__in=blocking_users).filter(
            Q(classroom__isnull=False) | Q(post_level_id__in=user_levels) | Q(user=user)
        )

class PostUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        return PostModel.objects.filter(user=self.request.user)

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
        return PostModel.objects.all()

    def get_object(self):
        obj = super().get_object()

        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")

        return obj


class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return CommentModel.objects.all()

    def get_object(self):
        obj = super().get_object()

        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")

        return obj



class PostFeedView(APIView):
    """
    Smart unseen-first feed.

    Priority:
      1. Posts the current user has NOT yet seen — newest first.
      2. Once unseen posts run out (or don't fill the page), fill remaining
         slots with the most-recent seen/older posts.

    Pagination uses two independent offsets carried in the query string:
      unseen_offset  — how many unseen posts to skip (default 0)
      seen_offset    — how many seen posts to skip  (default 0)

    The `next` URL in the response encodes the correct next offsets so the
    client never needs to calculate them manually.  The Flutter FeedProvider
    follows the `next` URL directly.

    Read tracking:
      A PostView row is created (idempotently via ignore_conflicts) for every
      post delivered on a page.  Subsequent requests therefore exclude those
      posts from Pool A and move them to Pool B fallback.

    Race safety:
      bulk_create(ignore_conflicts=True) + the DB UNIQUE constraint on
      (user, post) guarantee that concurrent requests cannot produce duplicate
      PostView rows.

    Existing feed rules preserved:
      - classroom posts excluded
      - math-level / "Other" / null-level filtering
      - blocked / blocking user exclusion
      - "not interested" post exclusion
      - daily challenge card injection
      - teacher role exclusion from challenges
    """
    permission_classes = [permissions.IsAuthenticated]

    PAGE_SIZE = 10

    def get(self, request):
        user        = request.user
        user_levels = list(user.math_levels.values_list("id", flat=True))

        # ------------------------------------------------------------------
        # Parse dual-offset cursor from query string
        # ------------------------------------------------------------------
        try:
            unseen_offset = max(0, int(request.query_params.get("unseen_offset", 0)))
        except (TypeError, ValueError):
            unseen_offset = 0

        try:
            seen_offset = max(0, int(request.query_params.get("seen_offset", 0)))
        except (TypeError, ValueError):
            seen_offset = 0

        page_size = self.PAGE_SIZE

        # ------------------------------------------------------------------
        # Block / mute / not-interested lists
        # ------------------------------------------------------------------
        from messaging.models import BlockUser
        blocked_users  = BlockUser.objects.filter(blocker=user).values_list("blocked_user_id", flat=True)
        blocking_users = BlockUser.objects.filter(blocked_user=user).values_list("blocker_id", flat=True)
        not_interested = PostNotInterested.objects.filter(user=user).values_list("post_id", flat=True)

        # ------------------------------------------------------------------
        # Base queryset — all visibility / level / block rules applied once
        # ------------------------------------------------------------------
        base_qs = (
            PostModel.objects
            .filter(classroom__isnull=True)
            .filter(
                Q(post_level_id__in=user_levels)
                | Q(post_level__name__iexact="Other")
                | Q(post_level__isnull=True)
            )
            .exclude(user__isnull=True)
            .exclude(user=user)
            .exclude(user_id__in=blocked_users)
            .exclude(user_id__in=blocking_users)
            .exclude(id__in=not_interested)
            .select_related("user", "post_level")
            .prefetch_related("reactions", "comments", "translations")
        )

        # ------------------------------------------------------------------
        # Pool A — unseen posts (LEFT JOIN, no PostView row for this user)
        # Pool B — seen fallback (INNER JOIN, PostView row exists)
        # Both ordered newest-first for stable, predictable pagination.
        # ------------------------------------------------------------------
        unseen_qs = (
            base_qs
            .exclude(
                id__in=PostView.objects.filter(user=user).values("post_id")
            )
            .order_by("-created_at")
        )

        seen_qs = (
            base_qs
            .filter(
                id__in=PostView.objects.filter(user=user).values("post_id")
            )
            .order_by("-created_at")
        )

        # ------------------------------------------------------------------
        # Assemble page from the two pools
        # ------------------------------------------------------------------
        unseen_slice = list(unseen_qs[unseen_offset: unseen_offset + page_size])
        unseen_count = len(unseen_slice)

        if unseen_count >= page_size:
            page = unseen_slice
            next_unseen_offset = unseen_offset + page_size
            next_seen_offset   = seen_offset
            has_more = True  # conservatively assume more unseen exist
        else:
            remaining  = page_size - unseen_count
            seen_slice = list(seen_qs[seen_offset: seen_offset + remaining])
            page = unseen_slice + seen_slice

            next_unseen_offset = unseen_offset + unseen_count
            next_seen_offset   = seen_offset + len(seen_slice)

            # No more data when both pools are exhausted
            has_more = len(seen_slice) == remaining

        # ------------------------------------------------------------------
        # Mark delivered posts as read (idempotent, race-safe)
        # ------------------------------------------------------------------
        already_seen_ids = set(
            PostView.objects.filter(user=user).values_list("post_id", flat=True)
        )
        new_views = [p for p in page if p.id not in already_seen_ids]
        if new_views:
            PostView.objects.bulk_create(
                [PostView(user=user, post=p) for p in new_views],
                ignore_conflicts=True,
            )

        # ------------------------------------------------------------------
        # Serialize
        # ------------------------------------------------------------------
        serializer = PostFeedSerializer(
            page,
            many=True,
            context={"request": request},
        )
        feed_data = list(serializer.data)

        # ------------------------------------------------------------------
        # Inject an active challenge card at a random position
        # ------------------------------------------------------------------
        if getattr(user, "role", "").lower() != "teacher":
            from administration.models import DailyChallenge
            from challenge.models import ChallengeAttempt

            completed_challenge_ids = ChallengeAttempt.objects.filter(
                student__account__user=user,
                completed=True,
            ).values_list("challenge_id", flat=True)

            active_challenges = list(
                DailyChallenge.objects.filter(subject_id__in=user_levels)
                .exclude(id__in=completed_challenge_ids)
                .select_related("subject")
                .order_by("-publishing_date")[:5]
            )

            if active_challenges and feed_data:
                import random as _random
                challenge = _random.choice(active_challenges)
                user_lang = getattr(request.user, "language", "en")
                challenge_dict = {
                    "item_type": "challenge",
                    "id": str(challenge.id),
                    "name": challenge.get_translated_name(user_lang),
                    "subject": challenge.subject.get_translated_name(user_lang) if challenge.subject else "General",
                    "grade": challenge.grade,
                    "points": challenge.points,
                    "publishing_date": str(challenge.publishing_date),
                }
                insert_idx = (
                    _random.randint(1, len(feed_data) - 1)
                    if len(feed_data) > 2
                    else len(feed_data)
                )
                feed_data.insert(insert_idx, challenge_dict)

        # ------------------------------------------------------------------
        # Build next URL (dual-offset cursor)
        # ------------------------------------------------------------------
        if has_more:
            base_url = request.build_absolute_uri(request.path)
            next_url = (
                f"{base_url}"
                f"?unseen_offset={next_unseen_offset}"
                f"&seen_offset={next_seen_offset}"
            )
        else:
            next_url = None

        return Response({
            "count": len(feed_data),
            "next": next_url,
            "previous": None,
            "results": feed_data,
        })

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

        if post.user == request.user:
            return Response(
                {"error": "You cannot react to your own post"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reaction, created = PostReaction.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'reaction': reaction_type}
        )

        from administration.models import PointAdjustment
        point_adj = PointAdjustment.objects.first()
        upvote_points = point_adj.upvote_point if point_adj else 0

        def adjust_points(target_user, amount):
            if not target_user: return
            if hasattr(target_user, 'account') and hasattr(target_user.account, 'student'):
                student = target_user.account.student
                if hasattr(student, 'progress'):
                    student.progress.add_points(amount)

        if not created:
            if reaction.reaction == reaction_type:
                reaction.delete()
                message = f"{reaction_type} removed"
                if reaction_type == 'like' and post.user and post.user.id != request.user.id:
                    adjust_points(post.user, -upvote_points)
            else:
                old_reaction = reaction.reaction
                reaction.reaction = reaction_type
                reaction.save()
                message = f"Changed reaction to {reaction_type}"
                if post.user and post.user.id != request.user.id:
                    if old_reaction == 'dislike' and reaction_type == 'like':
                        adjust_points(post.user, upvote_points)
                    elif old_reaction == 'like' and reaction_type == 'dislike':
                        adjust_points(post.user, -upvote_points)
        else:
            message = f"{reaction_type} added"
            if reaction_type == 'like' and post.user and post.user.id != request.user.id:
                adjust_points(post.user, upvote_points)
                notif = Notification.objects.create(
                    user=post.user,
                    title="New Like",
                    description=f"{request.user.first_name or request.user.username} liked your post.",
                    type="like",
                    post_id=str(post.id)
                )
                emit_notification_to_socket(notif)
                send_push_notification(
                    user=post.user,
                    title="New Like",
                    body=f"{request.user.first_name or request.user.username} liked your post.",
                    data={"type": "like", "post_id": str(post.id)}
                )

        # --- Badge checks for post author (like milestones) ---
        if reaction_type == 'like' and post.user:
            post_author = post.user
            if hasattr(post_author, 'account') and hasattr(post_author.account, 'student'):
                author_student = post_author.account.student
                total_likes = PostReaction.objects.filter(
                    post__user=post_author,
                    reaction='like'
                ).count()
                from student.utils import award_badge_by_code
                if total_likes >= 10:
                    award_badge_by_code(author_student, 'likes_10')
                if total_likes >= 50:
                    award_badge_by_code(author_student, 'likes_50')
                if total_likes >= 100:
                    award_badge_by_code(author_student, 'likes_100')
                if total_likes >= 200:
                    award_badge_by_code(author_student, 'likes_200')
                if total_likes >= 500:
                    award_badge_by_code(author_student, 'likes_500')

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
            
        user = request.user
        if not post.classroom and post.post_level:
            user_levels = user.math_levels.values_list("id", flat=True)
            if post.post_level_id not in user_levels:
                return Response({"error": "You do not have the required math level to respond to this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # Resolve parent comment from the request data (support multiple field names)
        parent_id = (
            request.data.get('parent')
            or request.data.get('parent_comment')
            or request.data.get('parent_id')
        )
        parent_comment = None
        if parent_id:
            try:
                parent_comment = CommentModel.objects.get(id=parent_id, post=post)
            except CommentModel.DoesNotExist:
                pass  # If parent not found, save as top-level comment

        comment = serializer.save(
            user=request.user,
            post=post,
            language=request.user.language or 'en',
            parent=parent_comment,
        )

        from .tasks import translate_comment_task
        translate_comment_task.delay(str(comment.id))

        if post.user and post.user.id != request.user.id and not parent_comment:
            notif1 = Notification.objects.create(
                user=post.user,
                title="New Comment",
                description=f"{request.user.first_name or request.user.username} commented on your post.",
                type="comment",
                post_id=str(post.id),
                comment_id=str(comment.id)
            )
            emit_notification_to_socket(notif1)
            send_push_notification(
                user=post.user,
                title="New Comment",
                body=f"{request.user.first_name or request.user.username} commented on your post.",
                data={"type": "comment", "post_id": str(post.id), "comment_id": str(comment.id)}
            )
        
        if parent_comment and parent_comment.user and parent_comment.user.id != request.user.id:
            notif2 = Notification.objects.create(
                user=parent_comment.user,
                title="New Reply",
                description=f"{request.user.first_name or request.user.username} replied to your comment.",
                type="reply",
                post_id=str(post.id),
                comment_id=str(comment.id)
            )
            emit_notification_to_socket(notif2)
            send_push_notification(
                user=parent_comment.user,
                title="New Reply",
                body=f"{request.user.first_name or request.user.username} replied to your comment.",
                data={"type": "reply", "post_id": str(post.id), "comment_id": str(comment.id)}
            )

        # --- Badge checks for commenter ---
        commenter = request.user
        if hasattr(commenter, 'account') and hasattr(commenter.account, 'student'):
            commenter_student = commenter.account.student
            comment_count = CommentModel.objects.filter(user=commenter).count()
            from student.utils import award_badge_by_code
            if comment_count >= 50:
                award_badge_by_code(commenter_student, 'top_commenter')
            if comment_count >= 200:
                award_badge_by_code(commenter_student, 'super_commenter')

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        from messaging.models import BlockUser
        user = request.user
        blocked_users = BlockUser.objects.filter(blocker=user).values_list('blocked_user_id', flat=True)
        blocking_users = BlockUser.objects.filter(blocked_user=user).values_list('blocker_id', flat=True)

        comments = post.comments.exclude(user_id__in=blocked_users).exclude(user_id__in=blocking_users).order_by('created_at')
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

        if comment.user == request.user:
            return Response({"error": "You cannot react to your own comment"}, status=status.HTTP_400_BAD_REQUEST)

        reaction_type = request.data.get("reaction")
        if reaction_type not in ["like", "dislike"]:
            return Response({"error": "Invalid reaction type"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        existing_reaction = CommentReaction.objects.filter(comment=comment, user=user).first()

        from administration.models import PointAdjustment
        point_adj = PointAdjustment.objects.first()
        upvote_points = point_adj.upvote_point if point_adj else 0

        def adjust_points(target_user, amount):
            if not target_user: return
            if hasattr(target_user, 'account') and hasattr(target_user.account, 'student'):
                student = target_user.account.student
                if hasattr(student, 'progress'):
                    student.progress.add_points(amount)

        if existing_reaction:
            if existing_reaction.reaction == reaction_type:
                existing_reaction.delete()
                message = f"{reaction_type} removed"
                if reaction_type == 'like' and comment.user and comment.user.id != request.user.id:
                    adjust_points(comment.user, -upvote_points)
            else:
                old_reaction = existing_reaction.reaction
                existing_reaction.reaction = reaction_type
                existing_reaction.save()
                message = f"Changed to {reaction_type}"
                if comment.user and comment.user.id != request.user.id:
                    if old_reaction == 'dislike' and reaction_type == 'like':
                        adjust_points(comment.user, upvote_points)
                    elif old_reaction == 'like' and reaction_type == 'dislike':
                        adjust_points(comment.user, -upvote_points)
        else:
            CommentReaction.objects.create(comment=comment, user=user, reaction=reaction_type)
            message = f"{reaction_type} added"
            if reaction_type == 'like' and comment.user and comment.user.id != request.user.id:
                adjust_points(comment.user, upvote_points)

        like_count = comment.reactions.filter(reaction="like").count()
        dislike_count = comment.reactions.filter(reaction="dislike").count()

        return Response(
            {
                "message": message,
                "like_count": like_count,
                "dislike_count": dislike_count,
                "user_reaction": reaction_type if "added" in message or "Changed" in message else None
            }, status=status.HTTP_200_OK)


class PostNotInterestedView(APIView):
    """Mark a post as 'Not Interested' – excludes it from the user's feed."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        obj, created = PostNotInterested.objects.get_or_create(
            user=request.user,
            post=post,
        )
        return Response(
            {"msg": "Marked as not interested" if created else "Already marked"},
            status=status.HTTP_200_OK,
        )


class NotificationCountView(APIView):
    """Returns the count of unread notifications."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"count": count, "likes": 0, "comments": 0})


class MarkNotificationsSeenView(APIView):
    """Mark all notifications or a single notification as seen."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notification_id = request.data.get('notification_id')
        if notification_id:
            Notification.objects.filter(user=request.user, id=notification_id, is_read=False).update(is_read=True)
            return Response({"msg": f"Notification {notification_id} marked as seen."}, status=status.HTTP_200_OK)

        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"msg": "Notifications marked as seen."}, status=status.HTTP_200_OK)


class NotificationListViewAPI(APIView):
    """Returns a list of notifications for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        data = []
        for notif in notifications:
            data.append({
                "id": notif.id,
                "title": notif.title,
                "description": notif.description,
                "type": notif.type,
                "postId": notif.post_id,
                "commentId": notif.comment_id,
                "date_time": notif.created_at.isoformat(),
                "isRead": notif.is_read,
            })
        return Response({"data": data}, status=status.HTTP_200_OK)


class FCMDeviceRegistrationView(APIView):
    """Register or update an FCM token for the user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        device, created = FCMDevice.objects.get_or_create(user=request.user, token=token)
        return Response({"msg": "Token registered successfully"}, status=status.HTTP_200_OK)
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

class PostShareRedirectView(TemplateView):
    template_name = "post_share.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(PostModel, id=post_id)
        
        # We can extract title/description from the post object for Open Graph tags
        context['post_id'] = post_id
        context['post_title'] = "Post on Coyoote"
        
        # Truncate content for meta description
        plain_text = post.text_content
        context['post_description'] = plain_text[:200] + "..." if len(plain_text) > 200 else plain_text
        return context
