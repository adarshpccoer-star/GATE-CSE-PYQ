"use client";

import { useState } from "react";

export default function PdfUploader() {
  const [qFile, setQFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qFile) return alert("Please select a file");

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("questions", qFile);

    try {
      const response = await fetch("/api/upload_Ques", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        // Now expecting 'result' directly from the synchronous response
        setResult(data.result);
      } else {
        alert(data.error || "Extraction failed");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred during extraction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto border rounded-xl bg-slate-900 text-green-300 shadow-xl mt-10">
      <h2 className="text-3xl font-bold mb-6 text-center text-white">GATE PDF Extraction</h2>

      <form onSubmit={handleUpload} className="space-y-6">
        <div className="p-6 border-2 border-dashed border-slate-700 rounded-lg bg-slate-800">
          <label className="block text-sm font-medium mb-2 text-slate-400">Upload Question PDF</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setQFile(e.target.files?.[0] || null)}
            className="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-600 file:text-white hover:file:bg-green-700 cursor-pointer"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-bold text-lg hover:bg-green-700 disabled:bg-slate-700 transition-all shadow-lg shadow-green-900/20"
        >
          {loading ? "Processing (this may take a minute)..." : "Start Extraction"}
        </button>
      </form>

      {result && (
        <div className="mt-8 p-6 rounded-xl bg-slate-800 border border-slate-700 shadow-inner">
          <h3 className="text-xl font-bold mb-4 text-white flex items-center">
            <span className="mr-2">✅</span> Extracted Questions ({result.length})
          </h3>
          <div className="max-h-[500px] overflow-auto custom-scrollbar">
            {result.map((q: any, idx: number) => (
              <div key={idx} className="mb-6 p-4 border-b border-slate-700 last:border-0">
                <p className="text-green-400 font-bold mb-2">
                  Q{q.questionNumber || idx + 1}: {q.type}
                </p>
                <div className="text-slate-300 mb-2 whitespace-pre-wrap">{q.questionText}</div>
                {q.hasImage && <div className="text-xs text-yellow-500 mb-2 italic">[Diagram Extracted]</div>}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-slate-500">Subject: <span className="text-slate-300">{q.subject}</span></div>
                  <div className="text-slate-500">Answer: <span className="text-green-500">{q.answer}</span></div>
                </div>
              </div>
            ))}
          </div>
          <details className="mt-4">
            <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300">View Raw JSON</summary>
            <pre className="text-[10px] mt-2 p-2 bg-black rounded overflow-auto">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
}