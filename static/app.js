(function(){
 const canvas=document.getElementById('historyChart'); if(!canvas)return;
 const data=window.SIM_HISTORY||[]; const ctx=canvas.getContext('2d');
 const W=canvas.width,H=canvas.height,p=42; ctx.clearRect(0,0,W,H);
 ctx.strokeStyle='#293653';ctx.fillStyle='#9eabc7';ctx.font='12px system-ui';ctx.lineWidth=1;
 for(let i=0;i<=5;i++){const y=p+(H-2*p)*i/5;ctx.beginPath();ctx.moveTo(p,y);ctx.lineTo(W-p,y);ctx.stroke();ctx.fillText(String(100-i*20),8,y+4)}
 const series=[['gdp_real_growth_qoq_pct','#66d9ef',-5,6],['ipca_12m_pct','#ffd166',-1,20],['unemployment_pct','#ff7b7b',2,20],['gross_debt_pct_gdp','#6ee7a8',50,130]];
 function x(i){return data.length<=1?p:(p+(W-2*p)*i/(data.length-1))}
 series.forEach(([key,color,min,max])=>{ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();data.forEach((d,i)=>{let v=Number(d[key]||0);let y=H-p-(H-2*p)*(v-min)/(max-min);y=Math.max(p,Math.min(H-p,y)); if(i===0)ctx.moveTo(x(i),y);else ctx.lineTo(x(i),y)});ctx.stroke()});
 ctx.fillStyle='#9eabc7'; data.forEach((d,i)=>{if(i===0||i===data.length-1||i%4===0)ctx.fillText(d.period||'',x(i)-18,H-15)});
})();

(function(){
 const sliders=document.querySelectorAll('input[type="range"][data-slider-output]');
 const format=(input)=>{
   const out=document.getElementById(input.dataset.sliderOutput); if(!out)return;
   const n=Number(input.value); const decimals=Number(out.dataset.decimals||0);
   const signed=out.dataset.signed==='true'; const suffix=out.dataset.suffix||'';
   const sign=signed && n>0?'+':'';
   out.textContent=`${sign}${n.toFixed(decimals).replace('.',',')}${suffix}`;
   const min=Number(input.min),max=Number(input.max);
   const pct=max>min?((n-min)/(max-min))*100:50;
   input.style.setProperty('--range-pct',`${Math.max(0,Math.min(100,pct))}%`);
 };
 sliders.forEach(input=>{
   format(input);
   input.addEventListener('input',()=>format(input));
 });
})();
