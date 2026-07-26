export interface AssetNode{assetId:string;dependsOn:string[];usedBy:string[];}
export interface GraphProvider{getAsset(id:string):Promise<AssetNode|null>;}
export class DependencyResolutionEngine{constructor(private graph:GraphProvider){}
async getImpact(assetId:string){const n=await this.graph.getAsset(assetId);if(!n)return null;return{changedAsset:assetId,directDependencies:n.dependsOn,directDependents:n.usedBy,rebuildOrder:[...n.dependsOn].reverse(),risk:n.usedBy.length>10?'high':n.usedBy.length>3?'medium':'low'};}
async canRelease(assetId:string){const i=await this.getImpact(assetId);if(!i)return false;return i.directDependencies.length===0;}}"}