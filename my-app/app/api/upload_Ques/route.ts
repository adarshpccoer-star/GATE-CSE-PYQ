

// import helper from "@/lib/helper";
// import { NextResponse } from "next/server";
// export const runtime = "nodejs";
// import pdf from "pdf-parse";
// const pdfjsLib = await import("pdfjs-dist/legacy/build/pdf.mjs");
// async function parseWithPdfParse(buffer: Buffer) {
//   const data = await pdf(buffer);
//   return data.text;
// }

import { NextResponse } from "next/server";

// async function parseWithPdfJs(buffer: Buffer) {
//   const uint8 = new Uint8Array(buffer);
//   const doc = await pdfjsLib.getDocument({ data: uint8 }).promise;

//   let fullText = "";

//   for (let i = 1; i <= doc.numPages; i++) {
//     const page = await doc.getPage(i);
//     const content = await page.getTextContent();

//     const text = content.items.map((item: any) => item.str).join(" ");
//     fullText += "\n" + text;
//   }

//   return fullText;
// }

// async function extractText(buffer: Buffer) {
//   let text = await parseWithPdfParse(buffer);

//   // fallback if poor extraction
//   if (!text || text.length < 500) {
//     console.log("Fallback to pdfjs-dist...");
//     text = await parseWithPdfJs(buffer);
//   }

//   return text
//     .normalize("NFKD")
//     .replace(/[^\x00-\x7F]/g, " ")
//     .replace(/\s+/g, " ")
//     .trim();
// }


export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const qFile = formData.get("questions") as File;
    const aFile = formData.get("answers") as File;

    if (!qFile || !aFile) {
      return NextResponse.json({ error: "Missing files" }, { status: 400 });
    }

    // Prepare the data for Python
    const pythonFormData = new FormData();
    pythonFormData.append("questions", qFile); // Must match Python parameter name
    pythonFormData.append("answers", aFile);   // Must match Python parameter name

    // CALL THE PYTHON API
    const response = await fetch("http://127.0.0.1:8000/process-pdfs", {
      method: "POST", // This fixes the 405 error
      body: pythonFormData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Python server error: ${errorText}`);
    }

    const data = await response.json();
console.log(data);
    // Now you can return this to your frontend
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error: any) {
    console.error("Route Error:", error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

// export async function POST(req: Request) {
//   try {
//     const formData = await req.formData();

//     const qFile = formData.get("questions") as File;
//     const aFile = formData.get("answers") as File;

//     if (!qFile || !aFile) {
//       return NextResponse.json(
//         { error: "Both files required" },
//         { status: 400 }
//       );
//     }

//     const qBuffer = Buffer.from(await qFile.arrayBuffer());
//     const aBuffer = Buffer.from(await aFile.arrayBuffer());

//     const qText = await extractText(qBuffer);
//     const aText = await extractText(aBuffer);

//     const result = await helper(qText, aText);

//     return NextResponse.json({
//       success: true,
//       data: result
//     });

//   } catch (error: any) {
//     console.error(error);

//     return NextResponse.json(
//       {
//         success: false,
//         error: error.message
//       },
//       { status: 500 }
//     );
//   }
// }