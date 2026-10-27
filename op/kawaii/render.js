const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const [,,html,out,mode]=process.argv;
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1200}});
  p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('file://'+html);await p.waitForFunction(()=>window.__ready===true);
  const grab=async t=>Buffer.from((await p.evaluate(t=>{window.__renderAt(t);return document.getElementById('cv').toDataURL('image/png').split(',')[1]},t)),'base64');
  if(mode==='stills'){for(const t of [5.2,9.6]) fs.writeFileSync(`${out}/s_${t.toFixed(2)}.png`,await grab(t));await b.close();return}
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30000/1001','-i','-','-i',out.replace(/[^/]+$/,'')+'op.wav',
    '-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-r','30000/1001','-c:a','aac','-b:a','256k','-ar','48000','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<300;i++){const ok=ff.stdin.write(await grab(i*1001/30000));if(!ok)await new Promise(r=>ff.stdin.once('drain',r))}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
})();
