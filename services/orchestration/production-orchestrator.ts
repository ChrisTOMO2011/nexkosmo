export type Stage='inbox'|'preproduction'|'production'|'review'|'mastering'|'release';
export interface WorkItem{id:string;assetId:string;stage:Stage;owner?:string;blockedBy:string[];status:'todo'|'active'|'blocked'|'done';}
export interface Scheduler{assign(item:WorkItem):Promise<WorkItem>;}
export interface DashboardEventSink{publish(event:string,payload:unknown):Promise<void>;}
export class ProductionOrchestrator{constructor(private scheduler:Scheduler,private events:DashboardEventSink){}
async advance(item:WorkItem,next:Stage){if(item.blockedBy.length){item.status='blocked';await this.events.publish('work.blocked',item);return item;}item.stage=next;item.status='active';const assigned=await this.scheduler.assign(item);await this.events.publish('work.advanced',assigned);return assigned;}
async complete(item:WorkItem){item.status='done';await this.events.publish('work.completed',item);return item;}}
