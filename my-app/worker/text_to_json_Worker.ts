import helper from "@/lib/helper";
import { Worker } from "bullmq";
import IORedis from "ioredis";

const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

new Worker(
  "txt_json",
  async (job) => {
    let JSON_DATA :any= [];
    try {
      const { data } = job.data;
let count = 0;
      for (const item of data) {
        console.log(`Processing item ${count++}...`);
        const result = await helper(item);
        if (result) {
          JSON_DATA.push(result);
        }
      }
      return JSON_DATA;




    } catch (error) {
      if (error instanceof Error) {
          console.log(JSON_DATA);
        console.error(error.message);
        return JSON_DATA;
      } else {
        console.error(error);
      }
    }
  },
  { connection },
);
