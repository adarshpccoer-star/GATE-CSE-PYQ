import { QuestionModel } from "@/lib/schema";
import { Question } from "@/lib/vaildtor";
import next from "next";
import { NextResponse } from "next/server";



export const saveToMongo=async(data: Question[])=> {
    try {
      if(!data) return console.error("No data provided");
      console.log(data);
    
      const newData = await QuestionModel.insertMany(data);
        
      return NextResponse.json({
        success: true,
        data: newData
      });

    } catch (error) {
        error instanceof Error ? console.error(error.message) : console.error(error);
    }
}