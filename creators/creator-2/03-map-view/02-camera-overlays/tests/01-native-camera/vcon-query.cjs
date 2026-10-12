const net=require('node:net'),fs=require('node:fs'),crypto=require('node:crypto');
const marker='C2_'+crypto.randomBytes(8).toString('hex'); let buf=Buffer.alloc(0),started=false,lines=0;
const socket=net.connect({host:'127.0.0.1',port:Number(process.argv[5]||29000)});
function send(command){const p=Buffer.from(command+'\0'),h=Buffer.alloc(12);h.write('CMND');h.writeUInt32BE(0x00d40000,4);h.writeUInt16BE(p.length+12,8);socket.write(Buffer.concat([h,p]));}
socket.on('connect',()=>{send('echo '+marker);send(process.argv[2]);});
socket.on('data',chunk=>{buf=Buffer.concat([buf,chunk]);while(buf.length>=12){const length=buf.readUInt16BE(8);if(buf.readUInt32BE(4)!==0x00d40000||length<12){buf=buf.subarray(1);continue;}if(buf.length<length)break;const type=buf.toString('ascii',0,4),p=buf.subarray(12,length);buf=buf.subarray(length);if(type!=='PRNT'||p.length<28)continue;const text=p.subarray(28).toString('utf8').replace(/\0+$/,'');if(text.includes(marker))started=true;if(!started)continue;fs.appendFileSync(process.argv[3],JSON.stringify({utc:new Date().toISOString(),text})+'\n');lines++;if(/DotaCoachProbe|Screenshot written|C2_|StallMonitor|No such command/.test(text))console.log(text.slice(0,400));}});
socket.on('error',err=>{console.log(err.code);process.exitCode=1;});
setTimeout(()=>{socket.destroy();console.log(JSON.stringify({marker_received:started,live_lines:lines}));if(!started)process.exitCode=2;},Number(process.argv[4]||1000));
