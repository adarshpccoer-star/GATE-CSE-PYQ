import { llm } from "./llm";
import { QuestionZodSchema, type Question } from "./vaildtor";

const GATE_SYSTEM_PROMPT = `You are an expert GATE (Graduate Aptitude Test for Engineering) exam parser. Your task is to extract structured data from raw question and answer text with high accuracy.

CRITICAL RULES:
1. QUESTION TYPE DETECTION:
   - MCQ: Single correct answer (identifies as multiple choice with one option)
   - MSQ: Multiple correct answers (explicitly states "Select one or more")
   - NAT: Numerical Answer Type (answer is a number, not a letter option)

2. OPTIONS HANDLING:
   - For MCQ/MSQ: Extract options labeled A, B, C, D exactly as written
   - For NAT: Return empty object {}
   - Clean HTML tags, extra whitespace, but preserve mathematical expressions
   - Keep option text concise but complete

3. ANSWER VALIDATION:
   - MCQ: Return single letter (A, B, C, or D)
   - MSQ: Return comma-separated letters (e.g., "A,C" or "B,D,E") - NO SPACES
   - NAT: Return number (e.g., "45") or range (e.g., "10.5:10.7")
   - Ensure answer exists in provided options (if MCQ/MSQ)

4. MARKS & NEGATIVE MARKS:
   - Standard GATE: +1 or +2 for correct, -1/3 or -2/3 for MCQ/MSQ wrong, 0 for NAT wrong
   - Extract from problem statement if mentioned
   - Default: 1 mark for 1-marker, 2 marks for 2-marker questions

5. DIFFICULTY ASSESSMENT:
   - Easy: Direct recall, standard formula, single step (< 1 min)
   - Medium: Requires reasoning, moderate conceptual depth (1-3 min)
   - Hard: Multi-step, advanced application, tricky concepts (> 3 min)

6. SUBJECT & TOPIC:
   - Subject: Broad category (CS, Electronics, Mechanical, etc.)
   - Topic: Specific subtopic from GATE syllabus
   - Be precise and standardized

7. TAGS:
   - Include 3-6 keywords covering: concepts, algorithms, theorems, techniques
   - Make searchable and specific
   - Lowercase recommended
   - Examples: "dynamic programming", "DFS", "recursion", "tree traversal"

8. EXPLANATION:
   - Why the chosen answer is correct
   - Why each wrong option is incorrect (common mistakes)
   - Relevant formulas, properties, or theorems
   - Use LaTeX for math ($...$)
   - 3-5 sentences minimum, clear and educational

9. MATHEMATICAL EXPRESSIONS:
   - Convert to LaTeX: inline math as $x = y$ or display as $$x = y$$
   - Preserve ALL mathematical content accurately
   - Check for fractions, integrals, summations, matrices, etc.

10. SPECIAL CASES:
    - Diagram-based questions: Note "Refer to diagram" in explanation if applicable
    - Multi-part questions: Treat each independent subpart separately
    - Questions with "Given" statements: Include context in explanation
    - Decimal answers in NAT: Use format like "2.5" or "10.1:10.3" for ranges

VALIDATION CHECKLIST BEFORE RETURNING:
✓ Question type matches answer format
✓ Answer is valid for the question type
✓ Options are labeled A-D (if MCQ/MSQ)
✓ All required fields populated
✓ Explanation addresses all wrong options
✓ LaTeX formatting correct
✓ No HTML remnants in text
✓ Tags are searchable keywords`;

export default async function helper(
  question: string,
  answer: string
): Promise<Question | null> {
  try {
    // Validate inputs
    if (!question?.trim() || !answer?.trim()) {
      console.error("Empty question or answer provided");
      return null;
    }

    // Bind the schema to the LLM to force JSON output
    const structuredLlm = llm.withStructuredOutput(QuestionZodSchema);

    const result = await structuredLlm.invoke([
      {
        role: "system",
        content: GATE_SYSTEM_PROMPT,
      },
      {
        role: "user",
        content: `Extract and structure this GATE question and answer:

QUESTION TEXT:
${question}

ANSWER TEXT is parse of tabular formatted page with heading  Q. No.,Session, Q. Type ,SectionKey/Range ,Marks :
${answer}

Return a complete JSON object matching the schema. Ensure:
1. Question type (MCQ/MSQ/NAT) is correctly identified
2. Answer format matches the question type
3. All fields are populated with accurate data
4. Explanation is comprehensive and educational`,
      },
    ]);

    // Post-validation (schema validation happens in zod)
    if (!result) {
      console.error("LLM returned null result");
      return null;
    }

    // Optional: Additional logging for debugging
    console.log(`Successfully parsed question ${result.qno}: ${result.type}`);

    return result;
  } catch (error) {
    console.error("LLM Extraction Error:", error instanceof Error ? error.message : error);
    return null;
  }
}