"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
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
import { Edit3, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  useGetQuestionsByChallengeQuery,
  useUpdateQuestionMutation,
  useDeleteQuestionMutation,
} from "@/store/slices/api/questionApiSlice";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { questionUpdateSchema } from "@/schema/question.schema";
import { Question } from "@/types/question.type";
import { LoadingState } from "../elements/Loading";
import { NoDataState } from "../elements/NoData";
import { ErrorState } from "../elements/ErrorFetch";

type FormValues = {
  order: number;
  question_text: string;
  answer: string;
};

interface QuestionListProps {
  id: string; // challenge ID
}

function QuestionList({ id }: QuestionListProps) {
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);

  const {
    data: questionsData,
    isLoading,
    isFetching,
    isError
  } = useGetQuestionsByChallengeQuery(id);

  const [updateQuestion] = useUpdateQuestionMutation();
  const [deleteQuestion] = useDeleteQuestionMutation();

  const questions = questionsData?.results || [];

  const form = useForm<FormValues>({
    resolver: zodResolver(questionUpdateSchema),
    defaultValues: {
      order: 1,
      question_text: "",
      answer: "",
    },
  });

  const openEdit = (question: Question) => {
    setSelectedQuestion(question);
    form.reset({
      order: question.order,
      question_text: question.question_text,
      answer: question.answer,
    });
    setEditOpen(true);
  };

  const openDelete = (question: Question) => {
    setSelectedQuestion(question);
    setDeleteOpen(true);
  };

  const handleUpdate = async (values: FormValues) => {
    if (!selectedQuestion) return;
    try {
      await updateQuestion({
        id: selectedQuestion.id,
        body: values,
      }).unwrap();
      toast.success("Question updated successfully");
      setEditOpen(false);
    } catch {
      toast.error("Failed to update question");
    }
  };

  const handleDelete = async () => {
    if (!selectedQuestion) return;
    try {
      await deleteQuestion(selectedQuestion.id).unwrap();
      toast.success("Question deleted successfully");
      setDeleteOpen(false);
    } catch {
      toast.error("Failed to delete question");
    }
  };

  if (isLoading || isFetching) {
    return (
      <LoadingState/>
    );
  }

  if (questions.length === 0) {
    return (
      <NoDataState/>
    );
  }

  if(isError) {
    return(
        <ErrorState/>
    )
  }

  return (
    <div className="p-4 md:p-6 space-y-6">
      <h2 className="text-2xl font-semibold">Questions</h2>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {questions.map((question) => (
          <Card key={question.id} className="relative">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  Question #{question.order}
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => openEdit(question)}
                  >
                    <Edit3 className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => openDelete(question)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Question</p>
                <p className="mt-1 text-sm">{question.question_text}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Answer</p>
                <p className="mt-1 text-sm font-semibold text-green-600">
                  {question.answer}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Question</DialogTitle>
          </DialogHeader>
          <form onSubmit={form.handleSubmit(handleUpdate)} className="space-y-4">
            <div>
              <Label htmlFor="order">Order</Label>
              <Input
                id="order"
                type="number"
                {...form.register("order", { valueAsNumber: true })}
              />
              {form.formState.errors.order && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.order.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="question_text">Question Text</Label>
              <Textarea
                id="question_text"
                rows={4}
                {...form.register("question_text")}
              />
              {form.formState.errors.question_text && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.question_text.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="answer">Answer</Label>
              <Input id="answer" {...form.register("answer")} />
              {form.formState.errors.answer && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.answer.message}
                </p>
              )}
            </div>

            <div className="flex justify-end gap-3">
              <Button type="button" variant="secondary" onClick={() => setEditOpen(false)}>
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
            <AlertDialogTitle>Delete Question?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the question. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default QuestionList;