"use client"
import QuestionList from "@/components/AiQuestionGenerator/QuestionList";
import { useParams } from "next/navigation";

export default function QuestionGeneratorPage() {
  const { id } = useParams(); // id is string

  return (
    <QuestionList id={id as string} />
  )
}