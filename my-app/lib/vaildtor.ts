import { z } from "zod";

export const QuestionZodSchema = z.object({
  questionNumber: z.number().describe("The sequential question number."),
  year: z.number().describe("The 4-digit year of the exam."),
  session: z.enum(["morning", "evening", "afternoon"]),
  Date: z.string().describe("The date of the exam."),
  type: z.enum(["MCQ", "MSQ", "NAT"]),

  questionText: z.string().describe("The full text of the question using LaTeX for math."),
  
  // Image Extraction for Question
  hasImage: z.boolean().describe("True if the question contains a diagram."),
  // FIX: Removed .optional(), added .nullable()
  questionImage: z.string().nullable().describe("The extracted base64 image or description of the diagram if present."),

  options: z.record(z.string()).describe("Map of options. Example: { 'A': 'text' }."),
  
  // Image Extraction for Options
  optionsHaveImages: z.boolean().describe("True if options (A-D) contain diagrams."),
  // FIX: This was already .nullable(), but ensure .optional() is removed if it was there
  optionImages: z.record(z.string()).nullable().describe("A map of extracted images for each option key."),

  answer: z.string().describe("The correct choice(s) or NAT value."),
  marks: z.number(),
  difficulty: z.enum(["easy", "medium", "hard"]),
  subject: z.string(),
  topic: z.string(),
  tags: z.array(z.string()),
  explanation: z.string().describe("Full step-by-step reasoning.")
});

export type Question = z.infer<typeof QuestionZodSchema>;