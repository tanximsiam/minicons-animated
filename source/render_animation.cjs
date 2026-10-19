const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const root=path.dirname(__dirname),frames=path.join(__dirname,'motion-frames');fs.mkdirSync(frames,{recursive:true});
const data=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE_PATH||undefined,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1536,height:1280},deviceScaleFactor:1});
 await page.setContent('<!doctype html><style>*{box-sizing:border-box}html,body{margin:0;background:transparent}body{display:grid;grid-template-columns:repeat(12,128px);grid-auto-rows:128px}svg{display:block;width:128px;height:128px}</style>'+data.items.map(x=>fs.readFileSync(path.join(root,x.animated),'utf8')).join(''));
 await page.evaluate(()=>{window.animations=document.getAnimations();animations.forEach(a=>{a.pause();a.currentTime=0})});
 console.log('Animation tracks: '+await page.evaluate(()=>animations.length));
 for(let i=0;i<=96;i++){await page.evaluate(t=>animations.forEach(a=>a.currentTime=t),i*50);await page.screenshot({path:path.join(frames,'frame-'+String(i).padStart(3,'0')+'.png'),omitBackground:true});if(i%24===0)console.log('Frame '+i+'/96');}
 await browser.close();console.log('Captured 4.8 seconds at 20 fps.');
})().catch(e=>{console.error(e);process.exit(1)});
