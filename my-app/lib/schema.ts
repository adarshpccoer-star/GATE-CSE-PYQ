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
    
    // New Image Fields
    hasImage: { type: Boolean, default: false },
    questionImage: { type: String },
    
    options: {
      type: Schema.Types.Mixed,
      required: true,
      default: {},
    },
    
    // New Option Image Fields
    optionsHaveImages: { type: Boolean, default: false },
    optionImages: { type: Schema.Types.Mixed },

    answer: { type: String, required: true },
    marks: { type: Number, required: true },
    difficulty: {
      type: String,
      required: true,
      enum: ["easy", "medium", "hard"],
    },
    subject: { type: String, required: true, index: true },
    topic: { type: String, required: true },
    tags: { type: [String], required: true },
    explanation: { type: String, required: true }, // Corrected spelling to match validator
  },
  { timestamps: true },
);

export const QuestionModel =
  models.Question || model<Question>("Question", QuestionsSchema);
