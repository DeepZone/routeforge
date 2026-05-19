export type CheckResponse = {
  report_id: number; status: string; summary: string; recommendations: string[]; details: Record<string, unknown>; markdown: string; html: string;
}
