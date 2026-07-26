export interface ReasoningQuery{question:string;context?:Record<string,unknown>;}
export interface Evidence{source:string;confidence:number;summary:string;}
export interface ReasoningAnswer{answer:string;confidence:number;evidence:Evidence[];nextActions:string[];}
export interface GraphGateway{query(q:string):Promise<Evidence[]>;}
export class KnowledgeReasoningEngine{constructor(private graph:GraphGateway){} async reason(input:ReasoningQuery):Promise<ReasoningAnswer>{const evidence=await this.graph.query(input.question);return{answer:'Reasoning generated from production graph.',confidence:evidence.length?0.9:0.2,evidence,nextActions:['Inspect dependencies','Review workflow state','Validate affected assets']};}}