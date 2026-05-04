"use client";

import { useState } from "react";

export default function PdfUploader() {
  const [qFile, setQFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!qFile  ) return alert("Please select both files");

  setLoading(true);
  const formData = new FormData();
  formData.append("questions", qFile);
  
  try {
    const response = await fetch("/api/upload_Ques", {
      method: "POST",
      body: formData,
    });

    const data = await response.json(); // Uncomment this
    if (data.success) {
      setResult(data.data);
      console.log(data.data);
       // Set the result to see it on screen
    } else {
      alert(data.error || "Upload failed");
    }
  } catch (err) {
    console.error(err);
    alert("An error occurred during upload");
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="p-8 max-w-2xl mx-auto border rounded-xl  text-green-300 shadow-sm">
      <h2 className="text-2xl font-bold mb-6">PDF Analyzer</h2>
      
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Question PDF</label>
          <input 
            type="file" 
            accept="application/pdf"
            onChange={(e) => setQFile(e.target.files?.[0] || null)}
            className="w-full border p-2 rounded"
          />
        </div>

        
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-green-600 text-white py-2 rounded font-semibold hover:bg-green-700 disabled:bg-gray-400"
        >
          {loading ? "Processing..." : "Extract & Analyze"}
        </button>
      </form>

      {result && (
        <div className="mt-8 p-4 rounded border">
          <h3 className="font-bold mb-2">Analysis Result:</h3>
          <pre className="text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}