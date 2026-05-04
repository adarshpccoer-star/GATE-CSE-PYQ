

// const response = await client.responses.create({
import { zodResponseFormat, zodTextFormat } from "openai/helpers/zod.mjs";
import { client } from "./llm";
import { QuestionZodSchema,type Question } from "./vaildtor";
const GATE_SYSTEM_PROMPT = `
You are an expert parser for GATE exam questions.

Extract structured JSON exactly matching schema.

RULES:

1. Detect type:
- MCQ = one correct option
- MSQ = multiple correct options
- NAT = numerical answer

2. Options:
- MCQ/MSQ => A,B,C,D keys only
- NAT => {}

3. Answer:
- MCQ => single letter
- MSQ => comma-separated letters (A,C)
- NAT => number or range (2.5 or 10.2:10.5)

4. Clean text:
- Remove HTML/noise
- Preserve formulas in LaTeX

5. Difficulty:
easy / medium / hard

6. Subject + topic:
Use standard GATE syllabus names.

7. Tags:
3 to 6 concise searchable tags.

8. Explanation:
- why correct answer is right
- why others wrong
- formulas if needed
- minimum 3 sentences

9. Never invent missing facts.
Use null if unknown.
`;

export default async function helper(data: string): Promise<Question | null> {
  try {
    if (!data?.trim()) {
      console.error("Empty question or answer provided");
      return null;
    }

    // Use parse instead of create for automatic Zod validation and parsing
    const completion = await client.chat.completions.parse({
      model: "gemma4:e2b", // Structured Outputs requires specific models
      messages: [
        { role: "system", content: GATE_SYSTEM_PROMPT },
        {
          role: "user",
          content: `Extract and structure this GATE question, answer, option, and explanation:\n\nPYQ TEXT:\n${data}`,
        },
      ],
     
      response_format: zodResponseFormat(QuestionZodSchema, "gate_question"),
    });

    const result = completion.choices[0].message.parsed;

    if (!result) {
      if (completion.choices[0].message.refusal) {
        console.error("Model refused:", completion.choices[0].message.refusal);
      }
      return null;
    }

    console.log(`Successfully parsed question ${result.questionNumber}: ${result.type}`);
    return result;
  } catch (error) {
    console.error("LLM Extraction Error:", error instanceof Error ? error.message : error);
    return null;
  }
}