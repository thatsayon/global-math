// types/challenge.type.ts

export interface Subject {
  id: string
  name: string
  slug: string
}

export interface SubjectsResponse {
  subjects: Subject[]
}

export interface GeneratedQuestion {
  number: number
  question: string
  answer: string
}

export interface QuestionGenerationRequest {
  dificulty_level: number
  subject: string
  number_of_question: number
}

export interface QuestionGenerationResponse {
  grade: string
  subject: string
  count: number
  questions: GeneratedQuestion[]
}

export interface ChallengeQuestion {
  order: number
  question_text: string
  answer: string
}

export interface CreateChallengeRequest {
  name: string
  description: string
  subject: string
  grade: number
  points: number
  publishing_date: string
  questions: ChallengeQuestion[]
}

export interface CreateChallengeResponse {
  id: string
  message: string
}
export interface Challenge {
  id: string;
  name: string;
  description: string;
  subject: string;
  number_of_questions: number;
  points: number;
  publishing_date: string;
}
export interface ChallengeListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Challenge[];
}

export interface ChallengeUpdateRequest {
  question: string;
  answer: string;
  publish_date: string;
}

export type ChallengeUpdateResponse = ChallengeUpdateRequest;