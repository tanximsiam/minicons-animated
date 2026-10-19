const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const root=__dirname;
const scenes=[['wall',960,540],['closeup',720,720],['orbit',720,720]];
async function main(){
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE_PATH||undefined,args:['--no-sandbox']});
 for(const [scene,width,height] of scenes){
  const folder=path.join(root,'frames',scene);fs.mkdirSync(folder,{recursive:true});
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  page.on('pageerror',e=>{throw e});
  await page.goto(pathToFileURL(path.join(root,'Minicons_Media_Studio.html')).href+'?scene='+scene+'&capture=1');
  await page.waitForFunction(()=>window.sceneReady);
  const sampleOnly=process.argv.includes('--samples');
  const frameNumbers=sampleOnly?[0,24,48,72,96,120,144,168]:Array.from({length:193},(_,i)=>i);
  for(const i of frameNumbers){
   await page.evaluate(t=>renderAt(t),i/20);
   await page.screenshot({path:path.join(folder,String(i).padStart(4,'0')+'.png')});
   if(i%48===0)console.log(scene,i+'/192');
  }
  await page.close();
 }
 await browser.close();
}
main().catch(e=>{console.error(e);process.exit(1)});
