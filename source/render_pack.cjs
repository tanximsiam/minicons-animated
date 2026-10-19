const fs=require('fs'),path=require('path'),sharp=require('sharp');
const root=path.basename(__dirname)==='source'?path.dirname(__dirname):path.join(__dirname,'../emotion-faces');
const data=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
(async()=>{let n=0;for(const item of data.items){await sharp(path.join(root,item.static),{density:288}).resize(256,256).png().toFile(path.join(root,item.png));n++}console.log('Rendered '+n+' transparent PNGs.');})().catch(e=>{console.error(e);process.exit(1)});
