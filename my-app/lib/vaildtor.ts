import { z } from "zod";

export const QuestionZodSchema = z.object({
  questionNumber: z.number().describe("The sequential question number as listed in the exam paper."),
  
  type: z.enum(["MCQ", "MSQ", "NAT"]).describe(
    "The category of the question: 'MCQ' for Multiple Choice (single correct), " +
    "'MSQ' for Multiple Select (one or more correct), and 'NAT' for Numerical Answer Type."
  ),

  questionText: z.string().describe(
    "The full text of the question. Include any LaTeX formatting for mathematical expressions " +
    "using $inline$ or $$display$$ syntax. Do not include the question number here."
  ),

  options: z.record(z.string()).describe(
    "For MCQ and MSQ, provide a map of options where keys are uppercase letters (A, B, C, D). " +
    "Example: { 'A': '20', 'B': '40' }. For NAT, return an empty object {}."
  ),

  answer: z.string().describe(
    "For MCQ, the single letter (e.g., 'A'). For MSQ, a comma-separated list of letters (e.g., 'A,C'). " +
    "For NAT, the numerical value or range (e.g., '45' or '10.5:10.7')."
  ),

  marks: z.number().describe("The marks assigned to this question (usually 1 or 2)."),

  difficulty: z.enum(["easy", "medium", "hard"]).describe(
    "An assessment of the question's complexity based on the depth of concepts required."
  ),

  subject: z.string().describe(
    "The broad GATE subject name (e.g., 'Computer Science', 'Mathematics', 'General Aptitude')."
  ),

  topic: z.string().describe(
    "The specific sub-topic from the GATE syllabus (e.g., 'Eigenvalues', 'TCP/IP', 'Time and Work')."
  ),

  tags: z.array(z.string()).describe(
    "A list of relevant keywords for searching, such as specific theorems, formulas, or exam-specific labels."
  ),
explaination:z.string().describe("The full explaination about how other option are wrong from the answer which correct one is the answer"),
  year: z.number().describe("The 4-digit year the GATE exam was conducted (e.g., 2024)."),
});

export type Question = z.infer<typeof QuestionZodSchema>;