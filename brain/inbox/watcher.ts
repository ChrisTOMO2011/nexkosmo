export interface WatchEvent { path:string; event:'created'|'modified'; }
export interface WatcherAdapter { watch(dir:string,onEvent:(e:WatchEvent)=>Promise<void>):Promise<void>; }
export interface Processor { processPath(path:string):Promise<void>; }

export class InboxWatcher {
 constructor(private adapter:WatcherAdapter, private processor:Processor, private inboxRoot:string){}
 async start():Promise<void>{
   await this.adapter.watch(this.inboxRoot, async (event)=>{
     if(event.event!=='created') return;
     await this.processor.processPath(event.path);
   });
 }
}
