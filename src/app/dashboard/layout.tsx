import { AdminLayout } from "@/components/dashboard/AdminLayout";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section>
      <AdminLayout>{children}</AdminLayout>
    </section>
  );
}
