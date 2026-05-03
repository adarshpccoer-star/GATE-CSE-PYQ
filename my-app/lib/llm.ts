import { ChatOpenAI } from "@langchain/openai";

export const llm = new ChatOpenAI({
  // Your specific Docker local endpoint
  configuration: {
    baseURL: "http://localhost:12434/engines/llama.cpp/v1",
  },
  apiKey: "local-machine", // Required by the constructor but ignored by local engines
  modelName: "qwen2.5:3B-Q4_K_M", 
  temperature: 0, // Critical: 0 ensures the model stays focused on the JSON structure
});