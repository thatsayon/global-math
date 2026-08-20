from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied

from django.db.models import Count, Case, When, IntegerField, FloatField, Value, F, Q, ExpressionWrapper
from django.db.models.functions import Coalesce, Random, Now, Extract
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from datetime import timedelta
import random as _random
import math
import hashlib
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from core.pagination import (
    PostFeedPagination,
    CommentPagination,
)

from .serializers import (
    PostSerializer,
    PostFeedSerializer,
    CommentSerializer,
    ReactionSerializer,
    CommentReactionSerializer,
)
from .models import (
    PostModel,
    PostComment,
    PostReaction,
    PostCommentReaction,
    PostView,
    PostNotInterested
)

class PostLikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        action = request.data.get("action")

        if not action:
            return Response(
                {"error": "Action is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if action not in ["like", "dislike"]:
            return Response(
                {"error": "Invalid action. Choose 'like' or 'dislike'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        existing_reaction = PostReaction.objects.filter(post=post, user=user).first()

        if existing_reaction:
            if existing_reaction.reaction == action:
                existing_reaction.delete()
                return Response(
                    {"message": f"Post {action} removed."}, status=status.HTTP_200_OK
                )
            else:
                existing_reaction.reaction = action
                existing_reaction.save()
                return Response(
                    {"message": f"Post {action}d successfully."},
                    status=status.HTTP_200_OK,
                )
        else:
            PostReaction.objects.create(post=post, user=user, reaction=action)
            return Response(
                {"message": f"Post {action}d successfully."},
                status=status.HTTP_201_CREATED,
            )

class PostCommentLikeDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        user = request.user
        action = request.data.get("action")

        if not action:
            return Response(
                {"error": "Action is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if action not in ["like", "dislike"]:
            return Response(
                {"error": "Invalid action. Choose 'like' or 'dislike'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = PostComment.objects.get(id=comment_id)
        except PostComment.DoesNotExist:
            return Response(
                {"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        existing_reaction = PostCommentReaction.objects.filter(
            comment=comment, user=user
        ).first()

        if existing_reaction:
            if existing_reaction.reaction == action:
                existing_reaction.delete()
                return Response(
                    {"message": f"Comment {action} removed."}, status=status.HTTP_200_OK
                )
            else:
                existing_reaction.reaction = action
                existing_reaction.save()
                return Response(
                    {"message": f"Comment {action}d successfully."},
                    status=status.HTTP_200_OK,
                )
        else:
            PostCommentReaction.objects.create(
                comment=comment, user=user, reaction=action
            )
            return Response(
                {"message": f"Comment {action}d successfully."},
                status=status.HTTP_201_CREATED,
            )


class SessionFeedPagination(PostFeedPagination):
    """
    Overrides get_next_link to append the session_start and seed to the next URL,
    ensuring that the frozen session state is maintained across pagination requests.
    """
    def __init__(self, session_start_str, seed_str):
        super().__init__()
        self.session_start_str = session_start_str
        self.seed_str = seed_str

    def get_next_link(self):
        url = super().get_next_link()
        if url:
            from rest_framework.utils.urls import replace_query_param
            url = replace_query_param(url, "session_start", self.session_start_str)
            url = replace_query_param(url, "seed", self.seed_str)
        return url


class PostFeedView(APIView):
    """
    Feed algorithm — freshness-biased weighted random order with stable pagination.

    Goals:
      1. Every refresh shows a *different* mix (randomness/reshuffle).
      2. Newer posts appear near the top more often than older ones (freshness).
      3. Older posts still have a realistic chance of appearing (variety).
      4. Unseen posts always precede seen ones.
      5. No duplicate posts appear across pages during a single scroll session.

    To achieve this:
      - `session_start` freezes the `seen_post_ids` pool to the start of the session,
        preventing offset-shifting when delivered posts are marked as seen.
      - A random `seed` is used to generate a deterministic `jitter` per post. This
        guarantees the random reshuffle is completely stable while scrolling.
      - Both parameters are passed via the `next` URL to maintain the session.
    """
    permission_classes = [permissions.IsAuthenticated]

    _HALF_LIFE  = 5.0    # days — freshness halves every 5 days
    _MAX_RANK   = 150.0  # approximate ceiling for engagement normalisation

    def get(self, request):
        user        = request.user
        user_levels = list(user.math_levels.values_list("id", flat=True))

        # ------------------------------------------------------------------
        # Parse or initialize session parameters for pagination stability
        # ------------------------------------------------------------------
        session_start_str = request.query_params.get("session_start")
        if session_start_str:
            session_start = parse_datetime(session_start_str)
            if not session_start:
                session_start = timezone.now()
                session_start_str = session_start.isoformat()
        else:
            session_start = timezone.now()
            session_start_str = session_start.isoformat()

        seed_str = request.query_params.get("seed")
        if seed_str:
            try:
                seed = float(seed_str)
            except ValueError:
                seed = _random.random()
                seed_str = str(seed)
        else:
            seed = _random.random()
            seed_str = str(seed)

        # Freeze 'seen' tracking to before the session started
        seen_post_ids = set(
            PostView.objects.filter(
                user=user,
                viewed_at__lt=session_start
            ).values_list("post_id", flat=True)
        )

        from messaging.models import BlockUser
        blocked_users  = BlockUser.objects.filter(blocker=user).values_list("blocked_user_id", flat=True)
        blocking_users = BlockUser.objects.filter(blocked_user=user).values_list("blocker_id", flat=True)
        not_interested = PostNotInterested.objects.filter(user=user).values_list("post_id", flat=True)

        # ------------------------------------------------------------------
        # Base queryset — annotate engagement & relevance
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
            .annotate(
                like_count    = Count("reactions", filter=Q(reactions__reaction="like")),
                comment_count = Count("comments"),
            )
            .annotate(
                engagement_score = F("like_count") * 2 + F("comment_count") * 3,
                topic_score = Case(
                    When(post_level_id__in=user_levels, then=Value(30)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                verified_score = Case(
                    When(is_verified=True, then=Value(10)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                media_score = Case(
                    When(image__isnull=False, then=Value(5)),
                    When(video__isnull=False, then=Value(5)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
            .annotate(
                rank_score = (
                    F("topic_score")
                    + F("verified_score")
                    + F("media_score")
                    + F("engagement_score")
                )
            )
        )

        unseen_qs = base_qs.exclude(id__in=seen_post_ids)
        seen_qs   = base_qs.filter(id__in=seen_post_ids)

        # ------------------------------------------------------------------
        # Weighted deterministic random scorer
        # ------------------------------------------------------------------
        now = timezone.now()

        def _score(post):
            age_days = max((now - post.created_at).total_seconds() / 86400, 0)

            # Freshness: 1.0 for brand-new, ~0.5 at 5 days, ~0.01 at 30 days
            freshness = math.exp(-age_days / self._HALF_LIFE)

            # Engagement: logarithmic so viral posts don't dominate completely
            engagement = math.log1p(post.rank_score or 0) / math.log1p(self._MAX_RANK)

            # 70 % freshness, 30 % engagement — newer posts win more often
            base = freshness * 0.70 + engagement * 0.30

            # Deterministic jitter [0.5, 1.5] based on the session seed and post ID
            hash_input = f"{seed}_{post.id}".encode('utf-8')
            post_hash = int(hashlib.md5(hash_input).hexdigest()[:8], 16)
            jitter = 0.5 + (post_hash / 0xffffffff)

            return base * jitter

        def _rank(queryset):
            posts = list(queryset)
            if not posts:
                return []
            return sorted(posts, key=_score, reverse=True)

        # Unseen posts ALWAYS appear before already-seen ones
        ordered_posts = _rank(unseen_qs) + _rank(seen_qs)

        # ------------------------------------------------------------------
        # Paginate (maintaining the session parameters in the next URL)
        # ------------------------------------------------------------------
        paginator = SessionFeedPagination(session_start_str, seed_str)
        page = paginator.paginate_queryset(ordered_posts, request)

        # Record which posts were seen for the first time (race condition safe)
        all_time_seen = set(
            PostView.objects.filter(user=user).values_list("post_id", flat=True)
        )
        new_views = [p for p in page if p.id not in all_time_seen]
        if new_views:
            PostView.objects.bulk_create(
                [PostView(user=user, post=p) for p in new_views],
                ignore_conflicts=True,
            )

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

        return paginator.get_paginated_response(feed_data)
