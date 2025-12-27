export interface Question {
  id: string;
  order: number;
  question_text: string;
  answer: string;
}

export interface QuestionListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Question[];
}

export interface QuestionUpdateRequest {
  order: number;
  question_text: string;
  answer: string;
}

export type QuestionUpdateResponse = Question;