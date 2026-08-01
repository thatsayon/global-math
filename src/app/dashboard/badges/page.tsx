import BadgesPage from "@/components/badges/BadgesPage";

export const metadata = {
  title: "Badges | Mathos Admin",
  description:
    "View and manage all achievement badges on the Mathos platform. Track earner stats, filter by category, and award leaderboard badges.",
};

export default function BadgesRoute() {
  return <BadgesPage />;
}
