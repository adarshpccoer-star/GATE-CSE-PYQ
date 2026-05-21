import Groq from "groq-sdk";
import { client } from "./llm"; 
import { QuestionZodSchema, type Question } from "./vaildtor";


const GATE_SYSTEM_PROMPT = `
You are a precise rawText-to-JSON extractor for GATE exam questions.
Respond ONLY with a valid JSON object. No markdown, no explanations, just JSON.

CRITICAL RULES:
1. ONLY use data from the current input text.
2. NEVER use the year 2023 unless it is explicitly written in the OCR text.
3. Extraction must be 1:1. Do not summarize or change question wording.
4. For NAT type questions, set options to an empty object {}.
5. Use LaTeX for all mathematical expressions (e.g., $x^2$, \\frac{a}{b}).
6. ALWAYS include ALL required fields, even if empty/unknown:
   - If no answer is found, use "Not provided"
   - If no explanation exists, use "No explanation available"
   - If marks are not stated, estimate based on question complexity
   - difficulty: must be one of ["easy", "medium", "hard"]
   - subject: the exam subject (e.g., "Computer Science", "Electronics")
   - topic: the specific topic (e.g., "Data Structures", "Digital Circuits")
   - tags: an array of relevant tags
   - optionImages: empty object {} if no images, or object with image references

REQUIRED JSON STRUCTURE FOR EACH QUESTION:
{
  "year": number,
  "questionNumber": number,
  "questionText": string,
  "type": "MCQ" | "MSQ" | "NAT",
  "options": object (empty {} for NAT),
  "optionImages": object,
  "answer": string,
  "explanation": string,
  "subject": string,
  "topic": string,
  "marks": number,
  "difficulty": "easy" | "medium" | "hard",
  "tags": [string],
  "session": "morning" | "evening" | "afternoon",
  "Date": string
}
`;
export default async function helper(data: string) {
  try {
    const response = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: GATE_SYSTEM_PROMPT },
        { role: "user", content: `CURRENT RAW DATA TO PROCESS:\n\n${data}` }
      ],
      temperature: 0.1,
      max_tokens: 2000
    });

    const content = response.choices[0].message.content?.trim();
    if (!content) return null;

    // Try to extract JSON from response (in case there's extra text)
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.error("No JSON found in response");
      return null;
    }

    const rawJson = JSON.parse(jsonMatch[0]);
    
    // Handle array of questions or single question
    const questions = Array.isArray(rawJson) ? rawJson : [rawJson];
    
    const results = questions.map(q => QuestionZodSchema.parse(q));
    
    console.log("Parsed questions:", results);
    return results.length === 1 ? results[0] : results;
    
  } catch (error) {
    if (error instanceof Error) {
      console.error("GATE Extraction Error:", error.message);
      console.error("Full error:", error);
    }
    return null;
  }
}