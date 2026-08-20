"""
Tests for the smart unseen-first feed (PostFeedView).

Covers the 12 required scenarios from the implementation spec:
  1.  New user receives newest posts (all unseen)
  2.  Previously delivered posts are not prioritized when unseen posts exist
  3.  Second page returns different posts
  4.  PostView records are created for delivered posts
  5.  Duplicate PostView records cannot be created
  6.  3 unseen + limit 10  →  3 unseen + 7 seen fallback
  7.  All posts seen       →  seen fallback returned (not empty)
  8.  Newly created posts are prioritized for existing users
  9.  Pagination does not return duplicate posts across pages
  10. Excluded/deleted posts are not returned
  11. Two users have independent read histories
  12. Concurrent requests do not create duplicate PostView rows
"""

import uuid
import threading
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from post.models import PostModel, PostView, PostNotInterested
from administration.models import MathLevels

User = get_user_model()

FEED_URL = "/api/post/feed/"


def _make_user(username, **kwargs):
    """Helper — create a user with the minimum required fields."""
    user = User.objects.create_user(
        username=username,
        password="test1234",
        email=f"{username}@test.com",
        **kwargs,
    )
    return user


def _make_level():
    """Return (or create) a shared MathLevels instance."""
    level, _ = MathLevels.objects.get_or_create(
        name="Algebra",
        defaults={"description": "Algebra level"},
    )
    return level


def _make_post(author, level, created_offset_days=0):
    """Create a PostModel for *author* at *level*, optionally backdated."""
    post = PostModel.objects.create(
        user=author,
        post_level=level,
        text=f"Post by {author.username} — {uuid.uuid4()}",
        language="en",
    )
    if created_offset_days:
        # Back-date using queryset update (auto_now_add bypass)
        PostModel.objects.filter(pk=post.pk).update(
            created_at=timezone.now() - timedelta(days=created_offset_days)
        )
        post.refresh_from_db()
    return post


class FeedBaseTestCase(TestCase):
    """Shared setup — two users (viewer + author) and a math level."""

    def setUp(self):
        self.level = _make_level()
        self.author = _make_user("author")
        self.author.math_levels.add(self.level)

        self.viewer = _make_user("viewer")
        self.viewer.math_levels.add(self.level)

        self.client = APIClient()
        self.client.force_authenticate(user=self.viewer)


# ---------------------------------------------------------------------------
# Test 1 — New user receives newest posts
# ---------------------------------------------------------------------------
class Test01NewUserGetsNewestPosts(FeedBaseTestCase):
    def test_new_user_sees_all_posts_as_unseen(self):
        for i in range(5):
            _make_post(self.author, self.level, created_offset_days=i)

        resp = self.client.get(FEED_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        post_results = [r for r in data["results"] if r.get("item_type") != "challenge"]
        self.assertEqual(len(post_results), 5)

        # All should have been freshly seen now
        self.assertEqual(
            PostView.objects.filter(user=self.viewer).count(), 5
        )


# ---------------------------------------------------------------------------
# Test 2 — Previously seen posts not prioritised when unseen exist
# ---------------------------------------------------------------------------
class Test02SeenPostsNotPrioritisedWhenUnseenExist(FeedBaseTestCase):
    def test_unseen_come_before_seen(self):
        # Create 4 old posts, mark them seen BEFORE session start
        old_posts = [_make_post(self.author, self.level, created_offset_days=10 + i) for i in range(4)]
        past_time = timezone.now() - timedelta(days=1)
        
        for p in old_posts:
            pv = PostView.objects.create(user=self.viewer, post=p)
            PostView.objects.filter(pk=pv.pk).update(viewed_at=past_time)

        # Create 2 new unseen posts
        new_posts = [_make_post(self.author, self.level) for _ in range(2)]
        new_ids = {str(p.id) for p in new_posts}

        resp = self.client.get(FEED_URL)
        data = resp.json()
        post_results = [r for r in data["results"] if r.get("item_type") != "challenge"]

        # The first two results must be the unseen ones
        returned_ids = [r["id"] for r in post_results]
        self.assertTrue(
            new_ids.issubset(set(returned_ids[:2])),
            f"Expected unseen posts at top. Got: {returned_ids}",
        )


# ---------------------------------------------------------------------------
# Test 3 — Second page returns different posts
# ---------------------------------------------------------------------------
class Test03SecondPageReturnsDifferentPosts(FeedBaseTestCase):
    def test_no_duplicate_posts_across_pages(self):
        # 25 posts → should span at least 3 pages of 10
        posts = [_make_post(self.author, self.level, created_offset_days=i) for i in range(25)]

        resp1 = self.client.get(FEED_URL)
        data1 = resp1.json()
        ids1 = {r["id"] for r in data1["results"] if r.get("item_type") != "challenge"}

        next_url = data1.get("next")
        self.assertIsNotNone(next_url, "Expected a next URL for page 2")
        self.assertIn("session_start=", next_url)
        self.assertIn("seed=", next_url)

        # Follow the next URL
        resp2 = self.client.get(next_url)
        data2 = resp2.json()
        ids2 = {r["id"] for r in data2["results"] if r.get("item_type") != "challenge"}

        overlap = ids1 & ids2
        self.assertEqual(len(overlap), 0, f"Duplicate posts found across pages: {overlap}")


# ---------------------------------------------------------------------------
# Test 4 — PostView records created for delivered posts
# ---------------------------------------------------------------------------
class Test04PostViewRecordsCreated(FeedBaseTestCase):
    def test_postview_rows_created(self):
        posts = [_make_post(self.author, self.level) for _ in range(3)]

        self.assertEqual(PostView.objects.filter(user=self.viewer).count(), 0)

        self.client.get(FEED_URL)

        self.assertEqual(PostView.objects.filter(user=self.viewer).count(), 3)


# ---------------------------------------------------------------------------
# Test 5 — Duplicate PostView records cannot be created
# ---------------------------------------------------------------------------
class Test05NoDuplicatePostViewRows(FeedBaseTestCase):
    def test_duplicate_postview_rejected_by_constraint(self):
        post = _make_post(self.author, self.level)
        PostView.objects.create(user=self.viewer, post=post)

        # Attempting a second create with ignore_conflicts must not raise
        PostView.objects.bulk_create(
            [PostView(user=self.viewer, post=post)],
            ignore_conflicts=True,
        )
        self.assertEqual(
            PostView.objects.filter(user=self.viewer, post=post).count(), 1
        )


# ---------------------------------------------------------------------------
# Test 6 — 3 unseen + limit 10 → 3 unseen + 7 seen fallback
# ---------------------------------------------------------------------------
class Test06MixedPageUnseenAndSeen(FeedBaseTestCase):
    def test_partial_unseen_fills_with_seen(self):
        # 10 seen posts
        seen_posts = [_make_post(self.author, self.level, created_offset_days=10 + i) for i in range(10)]
        past_time = timezone.now() - timedelta(days=1)
        for p in seen_posts:
            pv = PostView.objects.create(user=self.viewer, post=p)
            PostView.objects.filter(pk=pv.pk).update(viewed_at=past_time)

        # 3 unseen posts
        unseen_posts = [_make_post(self.author, self.level) for _ in range(3)]
        unseen_ids = {str(p.id) for p in unseen_posts}

        resp = self.client.get(FEED_URL)
        data = resp.json()
        post_results = [r for r in data["results"] if r.get("item_type") != "challenge"]
        returned_ids = [r["id"] for r in post_results]

        # Total should be 10 (3 unseen + 7 seen)
        self.assertEqual(len(post_results), 10)

        # First 3 must be the unseen ones
        first_three = set(returned_ids[:3])
        self.assertEqual(first_three, unseen_ids)


# ---------------------------------------------------------------------------
# Test 7 — All seen → fallback, feed not empty
# ---------------------------------------------------------------------------
class Test07AllSeenReturnsFallback(FeedBaseTestCase):
    def test_all_seen_returns_seen_fallback(self):
        posts = [_make_post(self.author, self.level) for _ in range(5)]
        past_time = timezone.now() - timedelta(days=1)
        for p in posts:
            pv = PostView.objects.create(user=self.viewer, post=p)
            PostView.objects.filter(pk=pv.pk).update(viewed_at=past_time)

        resp = self.client.get(FEED_URL)
        data = resp.json()
        post_results = [r for r in data["results"] if r.get("item_type") != "challenge"]

        self.assertGreater(len(post_results), 0, "Feed must not be empty even when all posts are seen")


# ---------------------------------------------------------------------------
# Test 8 — Newly created posts are prioritised for existing users
# ---------------------------------------------------------------------------
class Test08NewPostsPrioritisedForExistingUsers(FeedBaseTestCase):
    def test_new_posts_appear_before_old_seen(self):
        old_posts = [_make_post(self.author, self.level, created_offset_days=20 + i) for i in range(5)]
        past_time = timezone.now() - timedelta(days=1)
        for p in old_posts:
            pv = PostView.objects.create(user=self.viewer, post=p)
            PostView.objects.filter(pk=pv.pk).update(viewed_at=past_time)

        new_posts = [_make_post(self.author, self.level) for _ in range(2)]
        new_ids = {str(p.id) for p in new_posts}

        resp = self.client.get(FEED_URL)
        data = resp.json()
        post_results = [r for r in data["results"] if r.get("item_type") != "challenge"]
        first_two_ids = {post_results[0]["id"], post_results[1]["id"]}

        self.assertEqual(first_two_ids, new_ids, "New unseen posts must appear first")


# ---------------------------------------------------------------------------
# Test 9 — Pagination is stable (no duplicates across pages)
# ---------------------------------------------------------------------------
class Test09PaginationIsStable(FeedBaseTestCase):
    def test_three_pages_no_duplicates(self):
        [_make_post(self.author, self.level, created_offset_days=i) for i in range(25)]

        all_ids = []
        url = FEED_URL
        for _ in range(3):
            resp = self.client.get(url)
            data = resp.json()
            page_ids = [r["id"] for r in data["results"] if r.get("item_type") != "challenge"]
            all_ids.extend(page_ids)
            url = data.get("next")
            if not url:
                break

        self.assertEqual(
            len(all_ids),
            len(set(all_ids)),
            f"Duplicate post IDs found across pages: {[x for x in all_ids if all_ids.count(x) > 1]}",
        )


# ---------------------------------------------------------------------------
# Test 10 — Excluded posts (not interested) are not returned
# ---------------------------------------------------------------------------
class Test10ExcludedPostsNotReturned(FeedBaseTestCase):
    def test_not_interested_posts_excluded(self):
        hidden_post = _make_post(self.author, self.level)
        PostNotInterested.objects.create(user=self.viewer, post=hidden_post)

        visible_post = _make_post(self.author, self.level)

        resp = self.client.get(FEED_URL)
        data = resp.json()
        returned_ids = {r["id"] for r in data["results"] if r.get("item_type") != "challenge"}

        self.assertNotIn(str(hidden_post.id), returned_ids)
        self.assertIn(str(visible_post.id), returned_ids)


# ---------------------------------------------------------------------------
# Test 11 — Two users have independent read histories
# ---------------------------------------------------------------------------
class Test11IndependentReadHistories(FeedBaseTestCase):
    def test_users_have_independent_histories(self):
        viewer_b = _make_user("viewer_b")
        viewer_b.math_levels.add(self.level)

        post = _make_post(self.author, self.level)

        PostView.objects.create(user=self.viewer, post=post)

        self.assertEqual(
            PostView.objects.filter(user=self.viewer, post=post).count(), 1
        )
        self.assertEqual(
            PostView.objects.filter(user=viewer_b, post=post).count(), 0
        )

        client_b = APIClient()
        client_b.force_authenticate(user=viewer_b)
        client_b.get(FEED_URL)

        self.assertEqual(PostView.objects.filter(user=viewer_b, post=post).count(), 1)
        self.assertEqual(PostView.objects.filter(user=self.viewer, post=post).count(), 1)


# ---------------------------------------------------------------------------
# Test 12 — Concurrent requests do not create duplicate PostView rows
# ---------------------------------------------------------------------------
class Test12ConcurrentRequestsNoDuplicates(FeedBaseTestCase):
    def test_concurrent_feed_requests_idempotent(self):
        [_make_post(self.author, self.level) for _ in range(5)]

        errors = []

        def fetch():
            try:
                c = APIClient()
                c.force_authenticate(user=self.viewer)
                c.get(FEED_URL)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=fetch) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [], f"Errors during concurrent requests: {errors}")

        from django.db.models import Count
        dupes = (
            PostView.objects
            .filter(user=self.viewer)
            .values("post_id")
            .annotate(cnt=Count("id"))
            .filter(cnt__gt=1)
        )
        self.assertEqual(list(dupes), [], f"Duplicate PostView rows found: {list(dupes)}")
