// JS mirror of catchup's rules (parser + flagger + template brief). The model brief is NOT run here.
const STAMP=/^(\d{1,2}\/\d{1,2}\/\d{2,4}),\s+(\d{1,2}:\d{2}(?:\s?[AP]M)?)\s+-\s+(.*)$/i;
const SYS=["messages and calls are end-to-end encrypted","created group","changed the subject","changed this group's icon","joined using this group's invite link","left","removed","added","you deleted this message","this message was deleted","missed voice call","missed video call"];
const MEDIA=["<media omitted>","image omitted","video omitted","sticker omitted","audio omitted","document omitted","gif omitted"];
const QW=/\b(who|what|when|where|why|how|which|can|could|should|shall|are|is|do|does|did|will|would|kya|kab|kahan|kaun)\b/i;
const DT=/\b(today|tomorrow|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|am|pm|\d{1,2}[:/]\d{2})\b/i;
const PL=/\b(plan|meet|call|movie|dinner|lunch|trip|exam|deadline|submit|book|ticket|reach|leave|come|bring)\b/i;
function parse(text){const msgs=[];for(const raw of text.split("\n")){const line=raw.trim();if(!line)continue;const m=line.match(STAMP);
 if(m){let rest=m[3],sender="",body=rest;const i=rest.indexOf(": ");if(i>=0){sender=rest.slice(0,i);body=rest.slice(i+2);}
  if(SYS.some(h=>body.toLowerCase().includes(h)))continue;
  msgs.push({date:m[1],time:m[2],sender:sender.trim(),text:body.trim(),media:MEDIA.some(t=>body.toLowerCase().includes(t))});}
 else if(msgs.length){msgs[msgs.length-1].text+=" "+line;}}return msgs;}
function flagged(msgs,you){const out=[];msgs.forEach((m,i)=>{let s=0;const t=m.text;if(t.includes("?")||QW.test(t))s+=2;if(DT.test(t))s+=1;if(PL.test(t))s+=1;
 if(you&&t.toLowerCase().includes(you.toLowerCase()))s+=2;if(m.media)s-=1;if(s>=2)out.push(i);});return out;}
function templateBrief(msgs,you){const per={};msgs.forEach(m=>per[m.sender]=1);const names=Object.keys(per);
 const key=flagged(msgs,you).slice(0,6).map(i=>msgs[i]);
 const l1=`${msgs.length} messages from ${names.length} people (${names.join(", ")}) between ${msgs[0].date}, ${msgs[0].time} and ${msgs[msgs.length-1].date}, ${msgs[msgs.length-1].time}.`;
 return l1+"\n"+(key.length?"Worth a look: "+key.map(m=>`${m.sender}: ${m.text.slice(0,80)}`).join(" | "):"Nothing urgent was flagged.");}
