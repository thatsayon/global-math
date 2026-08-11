from django.core.management.base import BaseCommand
from account.models import Badge


BADGES = [
    # --- First / Milestones ---
    {
        "code": "first_question",
        "name": "Asked First Question",
        "description": "Posted your very first question or discussion on the platform.",
        "icon": "🧠",
        "category": "Social",
    },
    # --- Streaks ---
    {
        "code": "streak_7",
        "name": "Week Warrior",
        "description": "Maintained a 7-day challenge streak without missing a day.",
        "icon": "🔥",
        "category": "Streak",
    },
    {
        "code": "streak_10",
        "name": "10-Day Hustler",
        "description": "Kept the momentum going with a 10-day challenge streak.",
        "icon": "❤️",
        "category": "Streak",
    },
    {
        "code": "streak_30",
        "name": "Monthly Legend",
        "description": "Incredible! You maintained a 30-day unbroken challenge streak.",
        "icon": "🏅",
        "category": "Streak",
    },
    {
        "code": "streak_100",
        "name": "Century Streaker",
        "description": "An extraordinary 100-day streak. You are truly unstoppable.",
        "icon": "🌟",
        "category": "Streak",
    },
    # --- Likes Received ---
    {
        "code": "likes_10",
        "name": "Getting Noticed",
        "description": "Your posts have received a total of 10 likes from the community.",
        "icon": "👍",
        "category": "Engagement",
    },
    {
        "code": "likes_50",
        "name": "Popular Kid",
        "description": "Your posts have received 50 likes — people love your content!",
        "icon": "💫",
        "category": "Engagement",
    },
    {
        "code": "likes_100",
        "name": "Century of Likes",
        "description": "100 likes received on your posts. You're a community star!",
        "icon": "🏆",
        "category": "Engagement",
    },
    {
        "code": "likes_200",
        "name": "Fan Favorite",
        "description": "200 likes received. The community can't get enough of your work.",
        "icon": "💎",
        "category": "Engagement",
    },
    {
        "code": "likes_500",
        "name": "Viral Sensation",
        "description": "500 likes! Your posts are spreading across the platform like wildfire.",
        "icon": "🚀",
        "category": "Engagement",
    },
    # --- Leaderboard ---
    {
        "code": "leaderboard_top_10",
        "name": "Top 10 Climber",
        "description": "Achieved a spot in the top 10 on the leaderboard.",
        "icon": "🏅",
        "category": "Academic",
    },
    {
        "code": "leaderboard_top_3",
        "name": "Podium Finisher",
        "description": "Earned a place in the top 3 on the leaderboard. An elite performer!",
        "icon": "🥉",
        "category": "Academic",
    },
    {
        "code": "leaderboard_top_1",
        "name": "Champion",
        "description": "Reached #1 on the leaderboard. The undisputed best of the best!",
        "icon": "👑",
        "category": "Academic",
    },
    # --- Comments ---
    {
        "code": "top_commenter",
        "name": "Top Commenter",
        "description": "Posted 50 or more comments. You're always part of the conversation.",
        "icon": "💬",
        "category": "Social",
    },
    {
        "code": "super_commenter",
        "name": "Super Commenter",
        "description": "Over 200 comments posted. The heartbeat of every discussion!",
        "icon": "🗣️",
        "category": "Social",
    },
    # --- Challenges ---
    {
        "code": "first_challenge",
        "name": "Challenge Accepted",
        "description": "Completed your very first daily challenge. The journey begins!",
        "icon": "⚡",
        "category": "Challenge",
    },
    {
        "code": "challenges_10",
        "name": "Challenge Enthusiast",
        "description": "Completed 10 challenges. You're getting the hang of it!",
        "icon": "🎯",
        "category": "Challenge",
    },
    {
        "code": "challenges_50",
        "name": "Challenge Master",
        "description": "50 challenges done. Your problem-solving skills are unmatched.",
        "icon": "🏹",
        "category": "Challenge",
    },
    {
        "code": "challenges_100",
        "name": "Challenge Legend",
        "description": "100 challenges completed. A true legend of the arena!",
        "icon": "🎖️",
        "category": "Challenge",
    },
    {
        "code": "perfect_score",
        "name": "Perfectionist",
        "description": "Achieved a perfect 100% score on a challenge. Flawless!",
        "icon": "✨",
        "category": "Challenge",
    },
    # --- Academic / Level ---
    {
        "code": "scholar",
        "name": "Scholar",
        "description": "Reached Level 10. Your dedication to math is truly commendable.",
        "icon": "📚",
        "category": "Academic",
    },
    {
        "code": "grand_scholar",
        "name": "Grand Scholar",
        "description": "Reached Level 25. A master of mathematics and perseverance.",
        "icon": "🎓",
        "category": "Academic",
    },
    # --- Posts ---
    {
        "code": "post_10",
        "name": "Prolific Poster",
        "description": "Created 10 posts. You're actively shaping the community!",
        "icon": "📝",
        "category": "Social",
    },
    {
        "code": "post_50",
        "name": "Content Creator",
        "description": "50 posts created. A cornerstone of the Coyoote community.",
        "icon": "🎨",
        "category": "Social",
    },
    # --- Special ---
    {
        "code": "early_adopter",
        "name": "Early Adopter",
        "description": "Joined Coyoote in its earliest days. A true pioneer of the platform.",
        "icon": "🌱",
        "category": "Special",
    },
]


class Command(BaseCommand):
    help = "Seed the database with all badge definitions (idempotent)."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for badge_data in BADGES:
            badge, created = Badge.objects.get_or_create(
                code=badge_data["code"],
                defaults={
                    "name": badge_data["name"],
                    "description": badge_data["description"],
                    "icon": badge_data["icon"],
                    "category": badge_data["category"],
                }
            )

            if not created:
                # Update fields in case they changed
                badge.name = badge_data["name"]
                badge.description = badge_data["description"]
                badge.icon = badge_data["icon"]
                badge.category = badge_data["category"]
                badge.save(update_fields=["name", "description", "icon", "category"])
                updated_count += 1
                self.stdout.write(f"  Updated: {badge.name}")
            else:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {badge.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done! {created_count} badges created, {updated_count} updated."
            )
        )
