"use client";

import React, { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Trophy, CalendarIcon } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

import { GeneratedQuestion } from "@/types/challenge.type";
import { ChallengeFormData, ChallengeSchema } from "@/schema/ChallengeSchema";
import {
  useCreateChallengeMutation,
  useGenerateQuestionsMutation,
  useGetSubjectsQuery,
} from "@/store/slices/api/challengeApi";
import { Textarea } from "../ui/textarea";

export default function AiQuestion() {
  const [showDialog, setShowDialog] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<
    GeneratedQuestion[]
  >([]);
  const [selectedQuestions, setSelectedQuestions] = useState<Set<number>>(
    new Set()
  );
  const [formData, setFormData] = useState<ChallengeFormData | null>(null);

  // RTK Query hooks
  const { data: subjects = [], isLoading: subjectsLoading } =
    useGetSubjectsQuery();
  const [generateQuestions, { isLoading: isGenerating }] =
    useGenerateQuestionsMutation();
  const [createChallenge, { isLoading: isPublishing }] =
    useCreateChallengeMutation();

  const challengeForm = useForm<ChallengeFormData>({
    resolver: zodResolver(ChallengeSchema),
    defaultValues: {
      challengeName: "",
      description: "",
      difficultyLevel: 1,
      subject: "",
      numberOfQuestions: 1,
      adjustPoint: 0,
    },
  });

  const onSubmit = async (data: ChallengeFormData) => {
    try {
      setFormData(data);

      const response = await generateQuestions({
        dificulty_level: data.difficultyLevel,
        subject: data.subject,
        number_of_question: data.numberOfQuestions,
      }).unwrap();

      setGeneratedQuestions(response.questions);
      setShowDialog(true);
      toast.success(`${response.count} questions generated successfully`);
    } catch (error) {
      const err = error as { data?: { message?: string } };
      toast.error(err?.data?.message || "Failed to generate questions");
    }
  };

  const handleSelectQuestion = (number: number) => {
    const newSelected = new Set(selectedQuestions);
    if (newSelected.has(number)) {
      newSelected.delete(number);
    } else {
      newSelected.add(number);
    }
    setSelectedQuestions(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedQuestions.size === generatedQuestions.length) {
      setSelectedQuestions(new Set());
    } else {
      setSelectedQuestions(new Set(generatedQuestions.map((q) => q.number)));
    }
  };

  const handlePublish = async () => {
    if (!formData) return;

    if (selectedQuestions.size === 0) {
      toast.error("Please select at least one question to publish");
      return;
    }

    try {
      const selectedQuestionsData = generatedQuestions
        .filter((q) => selectedQuestions.has(q.number))
        .map((q) => ({
          order: q.number,
          question_text: q.question,
          answer: q.answer,
        }));

      const response = await createChallenge({
        name: formData.challengeName,
        description: formData.description,
        subject: formData.subject,
        grade: formData.difficultyLevel,
        points: formData.adjustPoint,
        publishing_date: format(formData.publishDate, "yyyy-MM-dd"),
        questions: selectedQuestionsData,
      }).unwrap();

      toast.success(response.message || "Challenge created successfully");

      // Reset form and close dialog
      setShowDialog(false);
      setGeneratedQuestions([]);
      setSelectedQuestions(new Set());
      setFormData(null);
      challengeForm.reset();
    } catch (error) {
      const err = error as { data?: { message?: string } };
      toast.error(err?.data?.message || "Failed to create challenge");
    }
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setSelectedQuestions(new Set());
  };

  return (
    <div className="mt-4 md:mt-6 lg:mt-8">
      <div>
        <h2 className="text-lg font-medium mb-4">AI Question Generator</h2>
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3 border-b-2 pb-3 border-b-gray-100">
              <div className="bg-orange-100 p-2 w-fit rounded-md">
                <Trophy stroke="#EA580C" size={24} className="size-6" />
              </div>
              <h4 className="text-lg font-medium">Daily Challenge</h4>
            </div>
          </CardHeader>

          <CardContent>
            <form
              onSubmit={challengeForm.handleSubmit(onSubmit)}
              className="space-y-6"
            >
              {/* First Row - Challenge Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="challengeName">Challenge Name</Label>
                  <Input
                    id="challengeName"
                    placeholder="Enter challenge name"
                    {...challengeForm.register("challengeName")}
                  />
                  {challengeForm.formState.errors.challengeName && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.challengeName.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="adjustPoint">Adjust Point</Label>
                  <Input
                    id="adjustPoint"
                    type="number"
                    placeholder="Enter points"
                    {...challengeForm.register("adjustPoint", {
                      valueAsNumber: true,
                    })}
                  />
                  {challengeForm.formState.errors.adjustPoint && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.adjustPoint.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Publish Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !challengeForm.watch("publishDate") &&
                            "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {challengeForm.watch("publishDate") ? (
                          format(challengeForm.watch("publishDate"), "PPP")
                        ) : (
                          <span>Pick a date</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={challengeForm.watch("publishDate")}
                        onSelect={(date) =>
                          challengeForm.setValue("publishDate", date!)
                        }
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                  {challengeForm.formState.errors.publishDate && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.publishDate.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Third Row - Question Configuration */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="difficultyLevel">Difficulty Level</Label>
                  <Select
                    onValueChange={(value) =>
                      challengeForm.setValue("difficultyLevel", parseInt(value))
                    }
                    defaultValue="1"
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select level" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => (
                        <SelectItem key={level} value={level.toString()}>
                          Level {level}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {challengeForm.formState.errors.difficultyLevel && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.difficultyLevel.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="subject">Subject</Label>
                  <Select
                    onValueChange={(value) =>
                      challengeForm.setValue("subject", value)
                    }
                    disabled={subjectsLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select subject" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects.map((subject) => (
                        <SelectItem key={subject.id} value={subject.id}>
                          {subject.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {challengeForm.formState.errors.subject && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.subject.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="numberOfQuestions">Number of Questions</Label>
                  <Input
                    id="numberOfQuestions"
                    type="number"
                    placeholder="Enter number"
                    {...challengeForm.register("numberOfQuestions", {
                      valueAsNumber: true,
                    })}
                  />
                  {challengeForm.formState.errors.numberOfQuestions && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.numberOfQuestions.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2 lg:col-span-3">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Enter description"
                    {...challengeForm.register("description")}
                  />
                  {challengeForm.formState.errors.description && (
                    <p className="text-sm text-red-500">
                      {challengeForm.formState.errors.description.message}
                    </p>
                  )}
                </div>
              </div>
            </form>
          </CardContent>

          <CardFooter>
            <Button
              size="lg"
              disabled={isGenerating}
              onClick={challengeForm.handleSubmit(onSubmit)}
            >
              {isGenerating ? "Generating..." : "Generate"}
            </Button>
          </CardFooter>
        </Card>
      </div>

      {/* Questions Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="sm:max-w-7xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Generated Questions</DialogTitle>
            <DialogDescription>
              Select the questions you want to include in the challenge
            </DialogDescription>
          </DialogHeader>

          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={
                          selectedQuestions.size === generatedQuestions.length
                        }
                        onCheckedChange={handleSelectAll}
                      />
                      <span>No.</span>
                    </div>
                  </TableHead>
                  <TableHead>Question</TableHead>
                  <TableHead>Answer</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {generatedQuestions.map((question) => (
                  <TableRow key={question.number}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Checkbox
                          checked={selectedQuestions.has(question.number)}
                          onCheckedChange={() =>
                            handleSelectQuestion(question.number)
                          }
                        />
                        <span>{question.number}</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">
                      {question.question}
                    </TableCell>
                    <TableCell>{question.answer}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <DialogFooter className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              {selectedQuestions.size} of {generatedQuestions.length} selected
            </p>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleCloseDialog}>
                Cancel
              </Button>
              <Button
                disabled={isPublishing || selectedQuestions.size === 0}
                onClick={handlePublish}
              >
                {isPublishing ? "Publishing..." : "Publish Selected"}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
