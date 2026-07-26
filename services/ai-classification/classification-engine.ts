export interface ClassificationResult{assetType:string;category:string;confidence:number;tags:string[];projectHint?:string;department?:string;requiresReview:boolean;}
export interface AIClassifierProvider{classify(input:{path:string;mimeType?:string;metadata?:Record<string,unknown>}):Promise<ClassificationResult>;}
export interface ClassificationRules{minimumConfidence:number;reviewThreshold:number;}
export class AIClassificationEngine{
constructor(private provider:AIClassifierProvider,private rules:ClassificationRules={minimumConfidence:0.6,reviewThreshold:0.85}){}
async classify(input:{path:string;mimeType?:string;metadata?:Record<string,unknown>}):Promise<ClassificationResult>{
const r=await this.provider.classify(input);
return {...r,requiresReview:r.confidence<this.rules.reviewThreshold};
}
applyToManifest(manifest:any,result:ClassificationResult){
manifest.asset_type_hint=result.assetType;
manifest.project_hint??=result.projectHint;
manifest.ai_analysis={...(manifest.ai_analysis??{}),tags:result.tags,confidence:result.confidence,summary:`Classified as ${result.assetType} (${result.category})`};
manifest.review={...(manifest.review??{}),required:result.requiresReview};
return manifest;
}}
