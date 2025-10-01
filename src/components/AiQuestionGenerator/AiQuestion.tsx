"use client";
import React, { useState, useMemo } from "react";
import { Card, CardContent, CardFooter, CardHeader } from "../ui/card";
import { Trophy } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Checkbox } from "../ui/checkbox";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";

const AiQuestionSchema = z.object({
  grade: z.number().min(1, "Must select a grade"),
  subject: z.string().min(2, "Subject must be at least 2 characters"),
  value: z.number().min(1, "Value must be at least 1"),
});

type AiQuestionFormData = z.infer<typeof AiQuestionSchema>;

type GeneratedQuestion = {
  id: string;
  question: string;
  answer: string;
  subject: string;
};

// Extended dummy data for pagination demonstration
const createDummyQuestions = (
  count: number,
  subject: string
): GeneratedQuestion[] => {
  const questions = [
    { q: "What is the quadratic formula?", a: "x = (-b ± √(b² - 4ac)) / 2a" },
    { q: "Solve for x: 2x + 5 = 15", a: "x = 5" },
    { q: "What is the derivative of x²?", a: "2x" },
    { q: "Factor: x² - 9", a: "(x + 3)(x - 3)" },
    { q: "What is the integral of 2x?", a: "x² + C" },
    { q: "Simplify: 3x + 2x - 5x", a: "0" },
    { q: "What is the slope-intercept form?", a: "y = mx + b" },
    { q: "Solve: x² = 16", a: "x = ±4" },
    { q: "What is the Pythagorean theorem?", a: "a² + b² = c²" },
    { q: "Find the limit as x approaches 0 of sin(x)/x", a: "1" },
    { q: "What is Euler's formula?", a: "e^(ix) = cos(x) + i·sin(x)" },
    { q: "Solve: log₂(8)", a: "3" },
    { q: "What is the chain rule?", a: "dy/dx = (dy/du)(du/dx)" },
    { q: "Factor: x² + 5x + 6", a: "(x + 2)(x + 3)" },
    { q: "What is the discriminant of ax² + bx + c?", a: "b² - 4ac" },
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: `${i + 1}`,
    question: questions[i % questions.length].q,
    answer: questions[i % questions.length].a,
    subject: subject || "Math",
  }));
};

function AiQuestion() {
  const [toggle, setToggle] = useState<boolean>(false);
  const [showQuestions, setShowQuestions] = useState<boolean>(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<
    GeneratedQuestion[]
  >([]);
  const [selectedQuestions, setSelectedQuestions] = useState<Set<string>>(
    new Set()
  );
  const [isPublishing, setIsPublishing] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 5; // Fixed page limit

  const questionForm = useForm<AiQuestionFormData>({
    resolver: zodResolver(AiQuestionSchema),
    defaultValues: {
      grade: 1,
      subject: "",
      value: 1,
    },
  });

  // Calculate pagination
  const totalPages = Math.ceil(generatedQuestions.length / itemsPerPage);
  const paginatedQuestions = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return generatedQuestions.slice(startIndex, endIndex);
  }, [generatedQuestions, currentPage]);

  const showPagination = generatedQuestions.length > 5;

  const onQuestionSubmit = async (data: AiQuestionFormData) => {
    console.log("Question data:", data);
    setToggle(true);
    setCurrentPage(1); // Reset to first page

    const myPromise = new Promise<{ name: string }>((resolve) => {
      setTimeout(() => {
        // Generate questions based on the requested count
        const questions = createDummyQuestions(data.value, data.subject);
        setGeneratedQuestions(questions);
        setShowQuestions(true);
        resolve({ name: "Questions" });
      }, 3000);
    });

    toast.promise(myPromise, {
      loading: "Generating questions...",
      success: (data: { name: string }) => {
        setToggle(false);
        return `${data.name} generated successfully`;
      },
      error: "Error generating questions",
    });
  };

  const handleSelectQuestion = (id: string) => {
    const newSelected = new Set(selectedQuestions);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedQuestions(newSelected);
  };

  const handleSelectAllOnPage = () => {
    const pageQuestionIds = paginatedQuestions.map((q) => q.id);
    const newSelected = new Set(selectedQuestions);

    const allPageSelected = pageQuestionIds.every((id) => newSelected.has(id));

    if (allPageSelected) {
      pageQuestionIds.forEach((id) => newSelected.delete(id));
    } else {
      pageQuestionIds.forEach((id) => newSelected.add(id));
    }

    setSelectedQuestions(newSelected);
  };

  const isAllPageSelected = () => {
    return paginatedQuestions.every((q) => selectedQuestions.has(q.id));
  };

  const handlePublish = async () => {
    if (selectedQuestions.size === 0) {
      toast.error("Please select at least one question to publish");
      return;
    }

    setIsPublishing(true);

    const publishPromise = new Promise<{ count: number }>((resolve) => {
      setTimeout(() => {
        const questionsToPublish = generatedQuestions.filter((q) =>
          selectedQuestions.has(q.id)
        );
        console.log("Publishing questions:", questionsToPublish);
        resolve({ count: questionsToPublish.length });
      }, 2000);
    });

    toast.promise(publishPromise, {
      loading: "Publishing questions...",
      success: (data: { count: number }) => {
        setIsPublishing(false);
        setShowQuestions(false);
        setGeneratedQuestions([]);
        setSelectedQuestions(new Set());
        setCurrentPage(1);
        questionForm.reset();
        return `${data.count} question${
          data.count > 1 ? "s" : ""
        } published successfully`;
      },
      error: "Error publishing questions",
    });
  };

  const renderPaginationItems = () => {
    const items = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              onClick={() => setCurrentPage(i)}
              isActive={currentPage === i}
              className="cursor-pointer"
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
    } else {
      items.push(
        <PaginationItem key={1}>
          <PaginationLink
            onClick={() => setCurrentPage(1)}
            isActive={currentPage === 1}
            className="cursor-pointer"
          >
            1
          </PaginationLink>
        </PaginationItem>
      );

      if (currentPage > 3) {
        items.push(
          <PaginationItem key="ellipsis-start">
            <PaginationEllipsis />
          </PaginationItem>
        );
      }

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              onClick={() => setCurrentPage(i)}
              isActive={currentPage === i}
              className="cursor-pointer"
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }

      if (currentPage < totalPages - 2) {
        items.push(
          <PaginationItem key="ellipsis-end">
            <PaginationEllipsis />
          </PaginationItem>
        );
      }

      items.push(
        <PaginationItem key={totalPages}>
          <PaginationLink
            onClick={() => setCurrentPage(totalPages)}
            isActive={currentPage === totalPages}
            className="cursor-pointer"
          >
            {totalPages}
          </PaginationLink>
        </PaginationItem>
      );
    }

    return items;
  };

  return (
    <div className="mt-4 md:mt-6 lg:mt-8">
      <div>
        <h2 className="text-lg font-medium mb-4">AI Question Generator</h2>
        <div>
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
              <div className="flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6">

                {/* grage */}
                <div className="space-y-2 w-full">
                  <Label htmlFor="grade">Grade</Label>
                  <Input
                    type="number"
                    id="grade"
                    className="w-full"
                    {...questionForm.register("grade", { valueAsNumber: true })}
                  />
                  {questionForm.formState.errors.grade && (
                    <p className="text-sm text-red-500">
                      {questionForm.formState.errors.grade.message}
                    </p>
                  )}
                </div>

                {/* subject */}
                <div className="space-y-2 w-full">
                  <Label htmlFor="subject">Subject</Label>
                  <Input
                    placeholder="algebra, calculus etc...."
                    id="subject"
                    {...questionForm.register("subject")}
                  />
                  {questionForm.formState.errors.subject && (
                    <p className="text-sm text-red-500">
                      {questionForm.formState.errors.subject.message}
                    </p>
                  )}
                </div>

                {/* number of questions */}
                <div className="space-y-2 w-full">
                  <Label htmlFor="value">Number of Questions</Label>
                  <Input
                    id="value"
                    type="number"
                    className="w-full"
                    {...questionForm.register("value", { valueAsNumber: true })}
                  />
                  {questionForm.formState.errors.value && (
                    <p className="text-sm text-red-500">
                      {questionForm.formState.errors.value.message}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <div>
                <Button
                  size="lg"
                  disabled={toggle}
                  onClick={questionForm.handleSubmit(onQuestionSubmit)}
                >
                  Generate
                </Button>
              </div>
            </CardFooter>

            {showQuestions && generatedQuestions.length > 0 && (
              <>
                <CardContent className="pt-0">
                  <div className="border rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-20">
                              <div className="flex items-center gap-2">
                                <Checkbox
                                  checked={
                                    isAllPageSelected() &&
                                    paginatedQuestions.length > 0
                                  }
                                  onCheckedChange={handleSelectAllOnPage}
                                />
                                <span>No.</span>
                              </div>
                            </TableHead>
                            <TableHead className="min-w-[250px]">
                              Question
                            </TableHead>
                            <TableHead className="min-w-[200px]">
                              Answer
                            </TableHead>
                            <TableHead className="w-32">Subject</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {paginatedQuestions.map((question, index) => {
                            const globalIndex =
                              (currentPage - 1) * itemsPerPage + index;
                            return (
                              <TableRow key={question.id}>
                                <TableCell>
                                  <div className="flex items-center gap-2">
                                    <Checkbox
                                      checked={selectedQuestions.has(
                                        question.id
                                      )}
                                      onCheckedChange={() =>
                                        handleSelectQuestion(question.id)
                                      }
                                    />
                                    <span>{globalIndex + 1}</span>
                                  </div>
                                </TableCell>
                                <TableCell className="font-medium">
                                  {question.question}
                                </TableCell>
                                <TableCell>{question.answer}</TableCell>
                                <TableCell>
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    {question.subject}
                                  </span>
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                  <p className="text-sm text-gray-600">
                    {selectedQuestions.size} of {generatedQuestions.length}{" "}
                    selected
                    {showPagination && (
                      <span className="ml-2">
                        (Page {currentPage} of {totalPages})
                      </span>
                    )}
                  </p>
                  {/* Pagination - only show if more than 5 questions */}
                  {showPagination && (
                    <div className="mt-4">
                      <Pagination>
                        <PaginationContent>
                          <PaginationItem>
                            <PaginationPrevious
                              onClick={() =>
                                setCurrentPage((prev) => Math.max(1, prev - 1))
                              }
                              className={
                                currentPage === 1
                                  ? "pointer-events-none opacity-50"
                                  : "cursor-pointer"
                              }
                            />
                          </PaginationItem>

                          {renderPaginationItems()}

                          <PaginationItem>
                            <PaginationNext
                              onClick={() =>
                                setCurrentPage((prev) =>
                                  Math.min(totalPages, prev + 1)
                                )
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
                  <Button
                    size="lg"
                    disabled={isPublishing || selectedQuestions.size === 0}
                    onClick={handlePublish}
                  >
                    Publish Selected
                  </Button>
                </CardFooter>
              </>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default AiQuestion;
