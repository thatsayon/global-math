export interface ModerationDataType {
  id: number;
  name: string;
  role: "Student" | "Teacher";
  date: string;
  actionTaken: "UnBanned" | "Banned" | "Warned" | "Muted";
  warnings: number;
}

export const moderationData: ModerationDataType[] = [
  {
    id: 1,
    name: "Christine Brooks",
    role: "Student",
    date: "2025-01-15",
    actionTaken: "Muted",
    warnings: 2,
  },
  {
    id: 2,
    name: "Sarah Johnson",
    role: "Student",
    date: "2025-02-10",
    actionTaken: "UnBanned",
    warnings: 4,
  },
  {
    id: 3,
    name: "Lisa Devis",
    role: "Student",
    date: "2025-03-15",
    actionTaken: "Banned",
    warnings: 8,
  },
  {
    id: 4,
    name: "Stephanie Nicol",
    role: "Student",
    date: "2025-04-05",
    actionTaken: "UnBanned",
    warnings: 2,
  },
  {
    id: 5,
    name: "Stephanie Nicol",
    role: "Student",
    date: "2025-04-15",
    actionTaken: "Warned",
    warnings: 5,
  },
  {
    id: 6,
    name: "Kurt Bates",
    role: "Student",
    date: "2025-05-15",
    actionTaken: "Warned",
    warnings: 5,
  },
  {
    id: 7,
    name: "David Miller",
    role: "Teacher",
    date: "2025-05-20",
    actionTaken: "UnBanned",
    warnings: 3,
  },
  {
    id: 8,
    name: "Sophia Turner",
    role: "Teacher",
    date: "2025-06-05",
    actionTaken: "UnBanned",
    warnings: 1,
  },
  {
    id: 9,
    name: "Michael Brown",
    role: "Student",
    date: "2025-06-15",
    actionTaken: "Warned",
    warnings: 7,
  },
  {
    id: 10,
    name: "Emma Wilson",
    role: "Teacher",
    date: "2025-07-01",
    actionTaken: "Banned",
    warnings: 2,
  },
  {
    id: 11,
    name: "Daniel Clark",
    role: "Student",
    date: "2025-07-12",
    actionTaken: "Muted",
    warnings: 6,
  },
  {
    id: 12,
    name: "Olivia Harris",
    role: "Teacher",
    date: "2025-07-25",
    actionTaken: "UnBanned",
    warnings: 3,
  },
  {
    id: 13,
    name: "James Carter",
    role: "Student",
    date: "2025-08-10",
    actionTaken: "Banned",
    warnings: 9,
  },
  {
    id: 14,
    name: "Mia Lewis",
    role: "Teacher",
    date: "2025-08-25",
    actionTaken: "Muted",
    warnings: 4,
  },
];
