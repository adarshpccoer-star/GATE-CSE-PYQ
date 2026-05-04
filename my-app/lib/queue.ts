import IORedis from "ioredis";
import { Queue } from "bullmq";

const connection = new IORedis(process.env.REDIS_URL! || "redis://127.0.0.1:6379", {
  maxRetriesPerRequest: null,
});

export const pdfQueue = new Queue("pdfQueue", {
  connection,
});