export interface User {
  id: number;
  name: string;
  email: string;
  role: "Student" | "Teacher";
  status: "Active" | "Banned";
  startDate: string;
  endDate: string;
}

export const users: User[] = [
  {
    id: 1,
    name: "Sarah Johnson",
    email: "sarah.johnson@school.edu",
    role: "Student",
    status: "Active",
    startDate: "2025-09-15",
    endDate: "2025-09-15",
  },
  {
    id: 2,
    name: "Michael Chen",
    email: "michael.chen@school.edu",
    role: "Teacher",
    status: "Active",
    startDate: "2025-09-16",
    endDate: "2025-02-10",
  },
  {
    id: 3,
    name: "Emma Wilson",
    email: "cristian.brook@school.com",
    role: "Student",
    status: "Active",
    startDate: "2025-09-17",
    endDate: "2025-03-15",
  },
  {
    id: 4,
    name: "Alex Smith",
    email: "alex.smith@school.edu",
    role: "Teacher",
    status: "Active",
    startDate: "2025-09-18",
    endDate: "2025-04-05",
  },
  {
    id: 5,
    name: "Lisa Devis",
    email: "lisa.devis@school.edu",
    role: "Student",
    status: "Active",
    startDate: "2025-09-18",
    endDate: "2025-04-15",
  },
  {
    id: 6,
    name: "Corina McCoy",
    email: "corina.mccoy@school.edu",
    role: "Student",
    status: "Banned",
    startDate: "2025-09-20",
    endDate: "2025-05-15",
  },
  {
    id: 7,
    name: "Bradley Lawlor",
    email: "bradley.lawlor@school.edu",
    role: "Teacher",
    status: "Active",
    startDate: "2025-09-21",
    endDate: "2025-05-05",
  },
  {
    id: 8,
    name: "Mary Freund",
    email: "mary.freund@school.edu",
    role: "Student",
    status: "Active",
    startDate: "2025-09-21",
    endDate: "2025-05-20",
  },
];