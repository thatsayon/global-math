"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreVertical, Eye, Edit3, Trash2 } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Challenge } from "@/types/challenge.type";
import { useDeleteDailyChallengeMutation, useGetDailyChallengesQuery, useGetSubjectsQuery, useUpdateDailyChallengeMutation } from "@/store/slices/api/challengeApi";
import { challengeUpdateSchema } from "@/schema/ChallengeSchema";

type FormValues = {
  name: string;
  description: string;
  points: number;
  publishing_date: string;
};

function Challenges() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedSubjectSlug, setSelectedSubjectSlug] = useState<string>("all");

  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(
    null
  );

  const { data: subjectsData } = useGetSubjectsQuery();

  const {
    data: challengesData,
    isLoading,
    isFetching,
  } = useGetDailyChallengesQuery({
    page: currentPage,
    subject: selectedSubjectSlug === "all" ? undefined : selectedSubjectSlug,
  });

  const [updateChallenge] = useUpdateDailyChallengeMutation();
  const [deleteChallenge] = useDeleteDailyChallengeMutation();

  const challenges = challengesData?.results || [];
  const totalCount = challengesData?.count || 0;
  const itemsPerPage = 8;
  const totalPages = Math.ceil(totalCount / itemsPerPage);

  const form = useForm<FormValues>({
    resolver: zodResolver(challengeUpdateSchema),
    defaultValues: {
      name: "",
      description: "",
      points: 0,
      publishing_date: "",
    },
  });

  const openEdit = (challenge: Challenge) => {
    setSelectedChallenge(challenge);
    form.reset({
      name: challenge.name,
      description: challenge.description,
      points: challenge.points,
      publishing_date: challenge.publishing_date,
    });
    setEditOpen(true);
  };

  const openDelete = (challenge: Challenge) => {
    setSelectedChallenge(challenge);
    setDeleteOpen(true);
  };

  const handleUpdate = async (values: FormValues) => {
    if (!selectedChallenge) return;
    try {
      await updateChallenge({
        id: selectedChallenge.id,
        body: values,
      }).unwrap();
      toast.success("Challenge updated successfully");
      setEditOpen(false);
    } catch {
      toast.error("Failed to update challenge");
    }
  };

  const handleDelete = async () => {
    if (!selectedChallenge) return;
    try {
      await deleteChallenge(selectedChallenge.id).unwrap();
      toast.success("Challenge deleted successfully");
      setDeleteOpen(false);
    } catch {
      toast.error("Failed to delete challenge");
    }
  };

  return (
    <div>
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">Challenge Management</h2>
            <Select
              value={selectedSubjectSlug}
              onValueChange={(value) => {
                setSelectedSubjectSlug(value);
                setCurrentPage(1);
              }}
            >
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder="All Subjects" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Subjects</SelectItem>
                {subjectsData?.map((sub) => (
                  <SelectItem key={sub.id} value={sub.slug}>
                    {sub.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50">
                    <TableHead className="w-12">No</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead className="text-center">Questions</TableHead>
                    <TableHead className="text-center">Points</TableHead>
                    <TableHead>Publish Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading || isFetching ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">
                        Loading challenges...
                      </TableCell>
                    </TableRow>
                  ) : challenges.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">
                        No challenges found
                      </TableCell>
                    </TableRow>
                  ) : (
                    challenges.map((challenge, index) => {
                      const rowNumber =
                        (currentPage - 1) * itemsPerPage + index + 1;
                      return (
                        <TableRow key={challenge.id}>
                          <TableCell className="font-medium">
                            {rowNumber}
                          </TableCell>
                          <TableCell className="font-medium">
                            {challenge.name}
                          </TableCell>
                          <TableCell className="max-w-xs truncate">
                            {challenge.description}
                          </TableCell>
                          <TableCell>{challenge.subject}</TableCell>
                          <TableCell className="text-center">
                            {challenge.number_of_questions}
                          </TableCell>
                          <TableCell className="text-center">
                            {challenge.points}
                          </TableCell>
                          <TableCell>
                            {format(
                              new Date(challenge.publishing_date),
                              "yyyy-MM-dd"
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                  onClick={() =>
                                    router.push(
                                      `/dashboard/ai-question-generator/${challenge.id}`
                                    )
                                  }
                                >
                                  <Eye className="mr-2 h-4 w-4" /> View
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => openEdit(challenge)}
                                >
                                  <Edit3 className="mr-2 h-4 w-4" /> Edit
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  className="text-destructive"
                                  onClick={() => openDelete(challenge)}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" /> Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      className={
                        currentPage === 1
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>

                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <PaginationItem key={page}>
                        <PaginationLink
                          onClick={() => setCurrentPage(page)}
                          isActive={currentPage === page}
                          className="cursor-pointer"
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    )
                  )}

                  <PaginationItem>
                    <PaginationNext
                      onClick={() =>
                        setCurrentPage((p) => Math.min(totalPages, p + 1))
                      }
                      className={
                        currentPage === totalPages
                          ? "pointer-events-none opacity-50"
                          : "cursor-pointer"
                      }
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Challenge</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={form.handleSubmit(handleUpdate)}
            className="space-y-4"
          >
            <div>
              <Label htmlFor="name">Name</Label>
              <Input id="name" {...form.register("name")} />
              {form.formState.errors.name && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.name.message}
                </p>
              )}
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                rows={3}
                {...form.register("description")}
              />
              {form.formState.errors.description && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.description.message}
                </p>
              )}
            </div>
            <div>
              <Label htmlFor="points">Points</Label>
              <Input
                id="points"
                type="number"
                {...form.register("points", { valueAsNumber: true })}
              />
              {form.formState.errors.points && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.points.message}
                </p>
              )}
            </div>
            <div>
              <Label htmlFor="publishing_date">Publishing Date</Label>
              <Input
                id="publishing_date"
                type="date"
                {...form.register("publishing_date")}
              />
              {form.formState.errors.publishing_date && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.publishing_date.message}
                </p>
              )}
            </div>
            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setEditOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                Save Changes
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Alert */}
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Challenge?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete "{selectedChallenge?.name}". This
              action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-white"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default Challenges;
