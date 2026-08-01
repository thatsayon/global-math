"use client";

import { useState, useMemo } from "react";
import { useGetAdminBadgesQuery, useAwardLeaderboardBadgesMutation } from "@/store/slices/api/badgeApiSlice";
import { Badge, BadgeCategory } from "@/types/badge.type";
import { LoadingState } from "@/components/elements/Loading";
import { ErrorState } from "@/components/elements/ErrorFetch";
import {
  Trophy,
  Search,
  Filter,
  Award,
  Users,
  ChevronRight,
  X,
  Sparkles,
  CheckCircle2,
  Clock,
  Zap,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

/* ======================================================
   Category config
====================================================== */
const CATEGORIES: { label: string; value: BadgeCategory | "All" }[] = [
  { label: "All", value: "All" },
  { label: "🔥 Streak", value: "Streak" },
  { label: "👍 Engagement", value: "Engagement" },
  { label: "⚡ Challenge", value: "Challenge" },
  { label: "💬 Social", value: "Social" },
  { label: "📚 Academic", value: "Academic" },
  { label: "🌱 Special", value: "Special" },
];

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string; glow: string; iconBg: string; gradient: string }> = {
  Streak:     { bg: "bg-orange-50/50", text: "text-orange-700", border: "border-orange-200/50", glow: "shadow-orange-500/20", iconBg: "bg-orange-100", gradient: "from-orange-50 to-amber-50/20" },
  Engagement: { bg: "bg-blue-50/50",   text: "text-blue-700",   border: "border-blue-200/50",   glow: "shadow-blue-500/20",  iconBg: "bg-blue-100", gradient: "from-blue-50 to-indigo-50/20" },
  Challenge:  { bg: "bg-purple-50/50", text: "text-purple-700", border: "border-purple-200/50", glow: "shadow-purple-500/20", iconBg: "bg-purple-100", gradient: "from-purple-50 to-fuchsia-50/20" },
  Social:     { bg: "bg-pink-50/50",   text: "text-pink-700",   border: "border-pink-200/50",   glow: "shadow-pink-500/20",  iconBg: "bg-pink-100", gradient: "from-pink-50 to-rose-50/20" },
  Academic:   { bg: "bg-green-50/50",  text: "text-green-700",  border: "border-green-200/50",  glow: "shadow-green-500/20", iconBg: "bg-green-100", gradient: "from-green-50 to-emerald-50/20" },
  Special:    { bg: "bg-amber-50/50",  text: "text-amber-700",  border: "border-amber-200/50",  glow: "shadow-amber-500/20", iconBg: "bg-amber-100", gradient: "from-amber-50 to-yellow-50/20" },
};

/* ======================================================
   Badge Detail Modal
====================================================== */
function BadgeDetailModal({
  badge,
  onClose,
}: {
  badge: Badge;
  onClose: () => void;
}) {
  const colors = CATEGORY_COLORS[badge.category] || CATEGORY_COLORS.Social;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`${colors.bg} px-6 pt-6 pb-4 border-b ${colors.border}`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div
                className={`w-16 h-16 rounded-2xl flex items-center justify-center text-4xl border-2 ${colors.border} bg-white shadow-lg`}
              >
                {badge.icon}
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{badge.name}</h2>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
                  {badge.category}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-white/60"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-gray-600 text-sm leading-relaxed mb-6">
            {badge.description}
          </p>

          {/* Stats */}
          <div className="flex items-center gap-2 mb-6 p-3 bg-gray-50 rounded-xl">
            <Users className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">
              <span className="font-bold text-gray-900">{badge.earner_count.toLocaleString()}</span>{" "}
              {badge.earner_count === 1 ? "student has" : "students have"} earned this badge
            </span>
          </div>

          {/* Recent Earners */}
          {badge.recent_earners.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4" /> Recent Earners
              </h3>
              <ul className="space-y-2">
                {badge.recent_earners.map((earner, i) => (
                  <li
                    key={i}
                    className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                        {earner.name[0]?.toUpperCase()}
                      </div>
                      <span className="font-medium text-gray-800">{earner.name}</span>
                    </div>
                    <span className="text-gray-400 text-xs">
                      {formatDistanceToNow(new Date(earner.earned_at), { addSuffix: true })}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {badge.earner_count === 0 && (
            <div className="text-center py-4 text-gray-400 text-sm">
              <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-40" />
              No one has earned this badge yet. Be the first!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ======================================================
   Badge Card
====================================================== */
function BadgeCard({ badge, onClick }: { badge: Badge; onClick: () => void }) {
  const colors = CATEGORY_COLORS[badge.category] || CATEGORY_COLORS.Social;
  const isRare = badge.earner_count < 5;

  return (
    <button
      onClick={onClick}
      className={`
        group relative text-left w-full rounded-2xl p-6
        bg-gradient-to-br ${colors.gradient} bg-white
        border border-gray-100 hover:border-transparent
        transition-all duration-300 ease-out
        hover:shadow-xl hover:-translate-y-1 hover:${colors.glow}
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        overflow-hidden isolate
      `}
    >
      {/* Background decoration */}
      <div className={`absolute -right-8 -top-8 w-32 h-32 rounded-full blur-3xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 ${colors.iconBg} -z-10`} />

      {/* Rare badge indicator */}
      {isRare && badge.earner_count > 0 && (
        <div className="absolute top-4 right-4">
          <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider bg-gradient-to-r from-amber-200 to-yellow-400 text-amber-900 border border-amber-300 px-2 py-1 rounded-full font-bold shadow-sm shadow-amber-200/50">
            <Sparkles className="w-3 h-3" /> Rare
          </span>
        </div>
      )}
      {badge.earner_count === 0 && (
        <div className="absolute top-4 right-4">
          <span className="text-[10px] uppercase tracking-wider bg-gray-100 text-gray-500 border border-gray-200 px-2 py-1 rounded-full font-bold">
            Undiscovered
          </span>
        </div>
      )}

      {/* Icon */}
      <div
        className={`w-16 h-16 rounded-2xl flex items-center justify-center text-4xl mb-5 shadow-sm
          ${colors.iconBg} border border-white/50 backdrop-blur-sm
          group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}
      >
        {badge.icon}
      </div>

      {/* Content */}
      <h3 className="font-bold text-gray-900 text-base mb-1.5 leading-snug pr-8 group-hover:text-gray-800 transition-colors">
        {badge.name}
      </h3>
      <p className="text-gray-500 text-xs leading-relaxed mb-5 line-clamp-2 h-10">
        {badge.description}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100/60 mt-auto">
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
          {badge.category}
        </span>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500">
          <Users className="w-3.5 h-3.5 text-gray-400" />
          <span>{badge.earner_count.toLocaleString()}</span>
        </div>
      </div>
    </button>
  );
}

/* ======================================================
   Stat Card
====================================================== */
function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 flex items-center gap-4 shadow-sm">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{typeof value === "number" ? value.toLocaleString() : value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  );
}

/* ======================================================
   Main Page Component
====================================================== */
export default function BadgesPage() {
  const { data, isLoading, isError } = useGetAdminBadgesQuery();
  const [awardLeaderboard, { isLoading: isAwarding }] = useAwardLeaderboardBadgesMutation();

  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<BadgeCategory | "All">("All");
  const [selectedBadge, setSelectedBadge] = useState<Badge | null>(null);
  const [awardResult, setAwardResult] = useState<string | null>(null);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.badges.filter((badge) => {
      const matchesCategory =
        selectedCategory === "All" || badge.category === selectedCategory;
      const matchesSearch =
        search === "" ||
        badge.name.toLowerCase().includes(search.toLowerCase()) ||
        badge.description.toLowerCase().includes(search.toLowerCase()) ||
        badge.code.toLowerCase().includes(search.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [data, search, selectedCategory]);

  const handleAwardLeaderboard = async () => {
    try {
      const result = await awardLeaderboard().unwrap();
      setAwardResult(
        `✅ ${result.message} (${result.newly_awarded.length} newly awarded)`
      );
      setTimeout(() => setAwardResult(null), 5000);
    } catch {
      setAwardResult("❌ Failed to award leaderboard badges. Please try again.");
      setTimeout(() => setAwardResult(null), 5000);
    }
  };

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState />;

  const categoryStats = data
    ? Object.entries(
        data.badges.reduce<Record<string, number>>((acc, b) => {
          acc[b.category] = (acc[b.category] || 0) + b.earner_count;
          return acc;
        }, {})
      )
    : [];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-9 h-9 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Badges</h1>
          </div>
          <p className="text-sm text-gray-500">
            Manage and monitor all {data?.total_badges ?? 0} achievement badges
          </p>
        </div>

        <button
          onClick={handleAwardLeaderboard}
          disabled={isAwarding}
          className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold text-sm shadow-md hover:shadow-lg hover:from-amber-600 hover:to-orange-600 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
          id="award-leaderboard-btn"
        >
          <Zap className="w-4 h-4" />
          {isAwarding ? "Awarding..." : "Award Leaderboard Badges"}
        </button>
      </div>

      {/* Award result message */}
      {awardResult && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 text-sm text-gray-700 shadow-sm">
          {awardResult}
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total Badges"
          value={data?.total_badges ?? 0}
          icon={Award}
          color="bg-gradient-to-br from-blue-500 to-blue-600"
        />
        <StatCard
          label="Total Badges Earned"
          value={data?.total_earned ?? 0}
          icon={CheckCircle2}
          color="bg-gradient-to-br from-green-500 to-emerald-600"
        />
        <StatCard
          label="Showing Results"
          value={`${filtered.length} / ${data?.total_badges ?? 0}`}
          icon={Filter}
          color="bg-gradient-to-br from-purple-500 to-purple-600"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            id="badge-search"
            type="text"
            placeholder="Search badges by name, description, or code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category filter tabs */}
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 border ${
                selectedCategory === cat.value
                  ? "bg-blue-600 text-white border-blue-600 shadow-md"
                  : "bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Badge Grid */}
      {filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center shadow-sm">
          <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No badges match your search</p>
          <p className="text-gray-400 text-sm mt-1">Try adjusting your filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((badge) => (
            <BadgeCard
              key={badge.code}
              badge={badge}
              onClick={() => setSelectedBadge(badge)}
            />
          ))}
        </div>
      )}

      {/* Category breakdown */}
      {data && categoryStats.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
          <h3 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            Category Breakdown
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {categoryStats.sort((a, b) => b[1] - a[1]).map(([cat, total]) => {
              const colors = CATEGORY_COLORS[cat] || CATEGORY_COLORS.Social;
              const countInCat = data.badges.filter((b) => b.category === cat).length;
              return (
                <div
                  key={cat}
                  className={`p-3 rounded-xl border ${colors.border} ${colors.bg} text-center cursor-pointer hover:shadow-sm transition-all`}
                  onClick={() => setSelectedCategory(cat as BadgeCategory)}
                >
                  <p className={`text-lg font-bold ${colors.text}`}>{total.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">earned</p>
                  <p className={`text-xs font-semibold mt-1 ${colors.text}`}>{cat}</p>
                  <p className="text-xs text-gray-400">{countInCat} badges</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedBadge && (
        <BadgeDetailModal
          badge={selectedBadge}
          onClose={() => setSelectedBadge(null)}
        />
      )}
    </div>
  );
}
