#!/usr/bin/env node
// Reproducible D3/SVG and Canvas2D figures for the DOCX benchmark report.
const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/maksym/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const [summaryPath, recordsPath, outDir] = process.argv.slice(2);
if (!summaryPath || !recordsPath || !outDir) {
  throw new Error('Usage: node render_browser_figures.js SUMMARY.json RECORDS.json OUTDIR');
}
const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
const records = JSON.parse(fs.readFileSync(recordsPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

const shell = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#1b2733}
.figure{box-sizing:border-box;width:1100px;padding:28px 34px 26px;background:#fff}
.title{font-size:24px;font-weight:700;line-height:1.2;margin:0 0 7px}
.subtitle{font-size:14px;color:#485766;line-height:1.35;margin:0 0 14px}
.note{font-size:12px;color:#56616a;line-height:1.35;margin-top:11px}
svg text{font-family:Arial,Helvetica,sans-serif;fill:#1b2733}
.axis text{font-size:13px;fill:#435260}.axis path,.axis line{stroke:#93a1ad}
.grid line{stroke:#e2e8ed}.grid path{display:none}
</style></head><body><div id="figure" class="figure"><h1 id="title" class="title"></h1><p id="subtitle" class="subtitle"></p><div id="chart"></div><div id="note" class="note"></div></div></body></html>`;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1120, height: 1000 }, deviceScaleFactor: 2 });
  await page.setContent(shell);
  await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js' });

  await page.evaluate((s) => {
    document.getElementById('title').textContent = 'Exploratory screening differences';
    document.getElementById('subtitle').textContent = '15 tasks × 3 repeats. Each row uses its own preassigned outcome proxy; task-cluster bootstrap 95% interval.';
    document.getElementById('note').textContent = 'Rows use different outcomes and must not be ranked against one another. Dashed line is the preregistered +0.10 threshold; screening scores alone cannot establish it.';
    const labels = { verify: 'Verification: linked required phrases', horizon: 'Horizon: latent phrases', clarify: 'Clarify: question topics' };
    const rows = ['verify', 'horizon', 'clarify'].map(a => ({ arm: a, label: labels[a], ...s.comparisons[a] }));
    const width = 1032, height = 360, left = 315, right = 300, top = 45, bottom = 58;
    const ext = rows.flatMap(r => [r.bootstrap_95[0], r.bootstrap_95[1], r.difference]);
    const lo = Math.min(-.12, d3.min(ext) - .05), hi = Math.max(.25, d3.max(ext) + .05);
    const x = d3.scaleLinear().domain([lo, hi]).nice().range([left, width - right]);
    const y = d3.scalePoint().domain(rows.map(r => r.arm)).range([top + 30, height - bottom - 15]).padding(.5);
    const svg = d3.select('#chart').append('svg').attr('width', width).attr('height', height).attr('role','img').attr('aria-label','Three prompt score differences with 95 percent confidence intervals');
    svg.append('g').attr('class','grid').attr('transform',`translate(0,${height-bottom})`).call(d3.axisBottom(x).ticks(6).tickSize(-(height-top-bottom)).tickFormat(''));
    svg.append('line').attr('x1',x(0)).attr('x2',x(0)).attr('y1',top).attr('y2',height-bottom).attr('stroke','#596a78').attr('stroke-width',1.5);
    svg.append('line').attr('x1',x(.10)).attr('x2',x(.10)).attr('y1',top).attr('y2',height-bottom).attr('stroke','#b07420').attr('stroke-width',1.5).attr('stroke-dasharray','6 5');
    svg.append('g').attr('class','axis').attr('transform',`translate(0,${height-bottom})`).call(d3.axisBottom(x).ticks(6).tickFormat(d3.format('+.2f')).tickSizeOuter(0));
    svg.append('text').attr('x',(left+width-right)/2).attr('y',height-9).attr('font-size',13).attr('text-anchor','middle').text('Difference in screened checkpoint proportion');
    const row = svg.selectAll('.row').data(rows).enter().append('g').attr('class','row').attr('transform',d=>`translate(0,${y(d.arm)})`);
    row.append('text').attr('x',8).attr('y',5).attr('font-size',16).attr('font-weight','bold').text(d=>d.label);
    row.append('line').attr('x1',d=>x(d.bootstrap_95[0])).attr('x2',d=>x(d.bootstrap_95[1])).attr('y1',0).attr('y2',0).attr('stroke','#205b8f').attr('stroke-width',3);
    row.append('line').attr('x1',d=>x(d.bootstrap_95[0])).attr('x2',d=>x(d.bootstrap_95[0])).attr('y1',-8).attr('y2',8).attr('stroke','#205b8f').attr('stroke-width',2);
    row.append('line').attr('x1',d=>x(d.bootstrap_95[1])).attr('x2',d=>x(d.bootstrap_95[1])).attr('y1',-8).attr('y2',8).attr('stroke','#205b8f').attr('stroke-width',2);
    row.append('circle').attr('cx',d=>x(d.difference)).attr('r',6).attr('fill','#205b8f');
    row.append('text').attr('x',width-right+15).attr('y',-2).attr('font-size',15).attr('font-weight','bold').text(d=>`${d.difference>=0?'+':''}${d.difference.toFixed(2)}  [${d.bootstrap_95[0].toFixed(2)}, ${d.bootstrap_95[1].toFixed(2)}]`);
    row.append('text').attr('x',width-right+15).attr('y',17).attr('font-size',12).attr('fill','#5b6872').text(d=>`${d.wins} task wins · ${d.ties} ties · ${d.losses} losses`);
  }, summary);
  await page.locator('#figure').screenshot({ path: path.join(outDir,'primary-differences.png') });

  await page.evaluate((s) => {
    document.getElementById('title').textContent = 'Task-level screening differences';
    document.getElementById('subtitle').textContent = 'Each cell uses three repetitions per arm. Positive values favor the named prompt on its column-specific screening outcome.';
    document.getElementById('note').textContent = 'Blue indicates a positive difference; orange a negative difference; pale cells are near zero. Exact values are printed in each cell.';
    const names = { verify:'Verification', horizon:'Question Horizon', clarify:'Clarify' };
    const tasks = Object.keys(s.comparisons.verify.task_differences).sort();
    const arms = ['verify','horizon','clarify'];
    const width=1032, height=690, left=130, top=62, cellW=275, cellH=35, gap=14;
    const vals=arms.flatMap(a=>tasks.map(t=>s.comparisons[a].task_differences[t]));
    const max=Math.max(.4,d3.max(vals.map(Math.abs)));
    const color=d3.scaleLinear().domain([-max,0,max]).range(['#cf8e38','#eef2f5','#2d6e9e']).clamp(true);
    const svg=d3.select('#chart').html('').append('svg').attr('width',width).attr('height',height).attr('role','img').attr('aria-label','Fifteen task differences for each of three prompt comparisons');
    arms.forEach((a,j)=>svg.append('text').attr('x',left+j*(cellW+gap)+cellW/2).attr('y',31).attr('text-anchor','middle').attr('font-size',16).attr('font-weight','bold').text(names[a]));
    tasks.forEach((t,i)=>{
      const y=top+i*cellH;
      svg.append('text').attr('x',16).attr('y',y+21).attr('font-size',14).attr('font-weight','bold').text(t);
      arms.forEach((a,j)=>{
        const v=s.comparisons[a].task_differences[t], x=left+j*(cellW+gap);
        svg.append('rect').attr('x',x).attr('y',y).attr('width',cellW).attr('height',cellH-3).attr('fill',color(v));
        svg.append('text').attr('x',x+cellW/2).attr('y',y+21).attr('text-anchor','middle').attr('font-size',14).attr('font-weight','bold').text((v>=0?'+':'')+v.toFixed(2));
      });
    });
  }, summary);
  await page.locator('#figure').screenshot({ path: path.join(outDir,'task-differences.png') });

  await page.evaluate((rows) => {
    document.getElementById('title').textContent = 'Response length and required phrase coverage';
    document.getElementById('subtitle').textContent = '225 dialogues. Each point is one completed dialogue; word count includes both turns when applicable.';
    document.getElementById('note').textContent = 'Small vertical jitter separates overlapping scores. Phrase coverage is a screening proxy, not a validated measure of factual accuracy or source support.';
    const colors={base:'#1f5c91',verify:'#bd7d27',horizon:'#d16f4c',two_turn_base:'#718643',clarify:'#a95b8e'};
    const names={base:'Base',verify:'Verification',horizon:'Question Horizon',two_turn_base:'Two-turn base',clarify:'Clarify'};
    const width=1032,height=560, left=86,right=36,top=35,bottom=88;
    const holder=document.getElementById('chart');holder.innerHTML='';
    const canvas=document.createElement('canvas');canvas.style.width=`${width}px`;canvas.style.height=`${height}px`;
    const ratio=Math.min(window.devicePixelRatio||1,2);canvas.width=width*ratio;canvas.height=height*ratio;
    holder.appendChild(canvas);const ctx=canvas.getContext('2d');ctx.setTransform(ratio,0,0,ratio,0,0);
    const xMax=Math.ceil(Math.max(...rows.map(r=>r.first_words+r.final_words))/500)*500;
    const x=v=>left+(v/xMax)*(width-left-right), y=v=>top+(1-v)*(height-top-bottom);
    ctx.fillStyle='#fff';ctx.fillRect(0,0,width,height);
    ctx.font='13px Arial';ctx.textBaseline='middle';ctx.fillStyle='#465563';
    for(let t=0;t<=1.0001;t+=.2){const py=y(t);ctx.strokeStyle='#e2e8ed';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(left,py);ctx.lineTo(width-right,py);ctx.stroke();ctx.fillText(t.toFixed(1),26,py)}
    const step=xMax>5000?1000:500;for(let t=0;t<=xMax;t+=step){const px=x(t);ctx.fillText(String(t),px-14,height-bottom+24)}
    ctx.strokeStyle='#758592';ctx.beginPath();ctx.moveTo(left,top);ctx.lineTo(left,height-bottom);ctx.lineTo(width-right,height-bottom);ctx.stroke();
    ctx.font='14px Arial';ctx.fillStyle='#22313d';ctx.fillText('Required phrase coverage',4,15);ctx.fillText('Total response words',width/2-60,height-bottom+55);
    rows.forEach((r,i)=>{const hash=[...r.item_id].reduce((a,c)=>((a*31+c.charCodeAt(0))>>>0),0), jitter=((hash%1000)/1000-.5)*.026;const cx=x(r.total_response_words),cy=y(Math.max(0,Math.min(1,r.required_coverage+jitter)));ctx.globalAlpha=.55;ctx.fillStyle=colors[r.arm];ctx.beginPath();ctx.arc(cx,cy,4.3,0,Math.PI*2);ctx.fill()});ctx.globalAlpha=1;
    let lx=left;for(const a of ['base','verify','horizon','two_turn_base','clarify']){ctx.fillStyle=colors[a];ctx.beginPath();ctx.arc(lx,height-17,5,0,Math.PI*2);ctx.fill();ctx.fillStyle='#24313d';ctx.font='13px Arial';ctx.fillText(names[a],lx+11,height-17);lx+=({base:115,verify:155,horizon:185,two_turn_base:170,clarify:130})[a]}
  }, records);
  await page.locator('#figure').screenshot({ path: path.join(outDir,'length-vs-grounding.png') });
  await browser.close();
  console.log(JSON.stringify({ figures: ['primary-differences.png','task-differences.png','length-vs-grounding.png'], outDir }));
}
main().catch(e => { console.error(e); process.exit(1); });
