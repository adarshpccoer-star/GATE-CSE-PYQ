import { Schema, model, models } from "mongoose";
import { Question } from "./vaildtor";

const QuestionsSchema = new Schema<Question>(
  {
    year: { type: Number, required: true },
    Date: { type: String, required: true },
    session: {
      type: String,
      required: true,
      enum: ["morning", "evening", "afternoon"],
    },
    questionNumber: { type: Number, required: true },
    type: {
      type: String,
      required: true,
      enum: ["MCQ", "MSQ", "NAT"],
    },
    questionText: { type: String, required: true },
    options: {
      type: Schema.Types.Mixed, // Better for key-value pairs like { A: "..." }
      required: true,
      default: {},
    },
    answer: { type: String, required: true },
    marks: { type: Number, required: true },
    difficulty: {
      type: String,
      required: true,
      enum: ["easy", "medium", "hard"],
    },
    subject: { type: String, required: true, index: true }, // Index for fast filtering
    topic: { type: String, required: true },
    tags: { type: [String], required: true },
  },
  { timestamps: true },
);

// Prevent model overwrite during Next.js Hot Reloading
export const QuestionModel =
  models.Question || model<Question>("Question", QuestionsSchema);
