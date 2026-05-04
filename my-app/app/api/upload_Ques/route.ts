import { pdfQueue } from "@/lib/queue";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    console.log("🚀 Starting PDF processing...");
    const formData = await req.formData();
    const qFile = formData.get("questions") as File;

    if (!qFile) {
      return NextResponse.json(
        { success: false, error: "Missing file" },
        { status: 400 }
      );
    }

    const pythonFormData = new FormData();
    pythonFormData.append("questions", qFile);

    const response = await fetch(
      "http://127.0.0.1:8000/process-pdfs",
      {
        method: "POST",
        body: pythonFormData,
      }
    );

    if (!response.ok) {
      const err = await response.text();
      throw new Error(err);
    }
    
    const data = await response.json();
   

    const re=await pdfQueue.add("txt_json", { data });
console.log(re);
    return NextResponse.json({
      success: true,
      re,
    });

  } catch (error: any) {
    console.error(error);

    return NextResponse.json(
      {
        success: false,
        error: error.message,
      },
      { status: 500 }
    );
  }
}