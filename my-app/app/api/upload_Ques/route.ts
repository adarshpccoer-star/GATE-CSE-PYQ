import helper from "@/lib/helper"; // Import your processing logic
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const qFile = formData.get("questions") as File;

    if (!qFile) {
      return NextResponse.json({ success: false, error: "Missing file" }, { status: 400 });
    }

    // 1. Send to Python Server for PDF cleaning
    const pythonFormData = new FormData();
    pythonFormData.append("questions", qFile);

    const response = await fetch("http://127.0.0.1:8000/process-pdfs", {
      method: "POST",
      body: pythonFormData,
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Python Server Error: ${err}`);
    }
    
    const pythonData = await response.json(); // This is the 'data' array from Python
    // 2. Direct Processing (Replacing BullMQ Worker)
    // Instead of pdfQueue.add, we loop and process here
    const JSON_DATA: any[] = [];
    let count = 0;
    for (const item of pythonData.data) {
      console.log(`Processing item ${count++}...`);
      const result = await helper(item);
      if (result) {
        JSON_DATA.push(result);
        console.log(result);
      }
    }

    // 3. Return the result directly to the frontend
    return NextResponse.json({
      success: true,
      result: JSON_DATA // The frontend is now expecting 'result'
    });

  } catch (error: any) {
    console.error("Route Error:", error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}