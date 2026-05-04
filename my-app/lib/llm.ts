import OpenAI from "openai";

 
 
 export const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL:"http://localhost:12434/engines/llama.cpp/v1",
 }
 );  
