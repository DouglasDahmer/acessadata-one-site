/* AcessaData-Health: narrativa D3 independente, dados agregados, sem analytics. */
"use strict";

(() => {
  const chart = document.getElementById("chart");
  const chartTitle = document.getElementById("chart-title");
  const chartDeck = document.getElementById("chart-deck");
  const summary = document.getElementById("chart-summary");
  const caution = document.getElementById("chart-caution");
  const controls = document.getElementById("controls");
  const tablePanel = document.getElementById("data-panel");
  const table = document.getElementById("data-table");
  const stepButtons = [...document.querySelectorAll(".story-step")];
  const sexButtons = [...document.querySelectorAll("[data-sex]")];
  const yearInput = document.getElementById("ano");
  const yearLabel = document.getElementById("ano-label");
  const integer = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
  const decimal = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const decimal4 = new Intl.NumberFormat("pt-BR", {minimumFractionDigits:4,maximumFractionDigits:4});
  const colors = { Feminino: "#d0734d", Masculino: "#0b6582" };
  let step = 0;
  let sex = "Ambos";
  let year = 2024;
  let dataset = null;

  const chapters = [
    {title:"Óbitos no Rio Grande do Sul — 2024", deck:"Uma fotografia do total de mortes registradas no RS, com destaque para as neoplasias malignas.", caution:"21.072 / 101.480 é uma proporção de registros de óbitos, não uma taxa populacional."},
    {title:"Dez grupos CID-10 em destaque — 2024", deck:"Contagens por código de três caracteres. Os dez grupos não representam todos os óbitos por câncer.", caution:"Códigos CID-10 são grupos de causa básica, não estimativas de incidência nem de risco individual."},
    {title:"Contagens anuais por sexo", deck:"Cada linha representa óbitos classificados por neoplasias malignas entre residentes do RS.", caution:"Contagens absolutas não permitem concluir, isoladamente, que o risco populacional aumentou."},
    {title:"Taxas brutas por 100 mil habitantes", deck:"Agora consideramos a população de cada sexo e ano — mas ainda não controlamos a estrutura etária.", caution:"Uma taxa bruta não controla mudanças na composição etária da população."},
    {title:"Taxas padronizadas por idade", deck:"As taxas específicas foram combinadas usando uma estrutura etária fixa: população conjunta do RS em 2024.", caution:"A população-padrão é interna ao estudo; a padronização não demonstra causalidade nem quantifica isoladamente o efeito do envelhecimento."},
    {title:"Tendência ajustada e incerteza", deck:"APC anual estimada em modelos de Poisson ajustados por idade, na especificação linear com CR2/Satterthwaite.", caution:"Essas estimativas foram transcritas da auditoria original; o storytelling não recalcula os modelos inferenciais."},
    {title:"Conciliação e registros não classificados", deck:"Os 19 registros fora das séries estratificadas permanecem no total geral de 194.368 óbitos.", caution:"O confronto com TabNet para 2022 e 2023 verifica contagens, não substitui a auditoria documental dos layouts sem cabeçalho."}
  ];

  function svgCanvas(label, description) {
    chart.replaceChildren();
    const svg = d3.select(chart).append("svg").attr("class","chart-svg")
      .attr("viewBox","0 0 660 340").attr("role","img").attr("aria-label",label);
    svg.append("title").text(label);
    svg.append("desc").text(description);
    return svg;
  }
  function tickFormat(value){ return value >= 1000 ? `${Math.round(value/1000)} mil` : decimal.format(value); }
  function axisStyles(axis){axis.selectAll("text").attr("font-size",12);}
  function background(svg, margin, width, height, yScale, ticks=5){
    const grid=svg.append("g").attr("class","grid").attr("transform",`translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).ticks(ticks).tickSize(-(width-margin.left-margin.right)).tickFormat(""));
    grid.selectAll("line").attr("stroke","#e1ebed");
  }
  /* Convencao visual de theme_minimal() (ggplot2): grades principais discretas. */
  function ggplotGridX(svg, scale, top, bottom, ticks=5){
    const g=svg.append("g").attr("class","grid ggplot-major-x")
      .attr("transform",`translate(0,${bottom})`)
      .call(d3.axisBottom(scale).ticks(ticks).tickSize(-(bottom-top)).tickFormat(""));
    g.select("path").remove();
  }
  function addTable(headers, rows, caption){
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    thead.replaceChildren(); tbody.replaceChildren();
    const tr=document.createElement("tr");
    for (const h of headers){ const th=document.createElement("th"); th.scope="col"; th.textContent=h; tr.append(th); }
    thead.append(tr);
    for(const row of rows){ const trBody=document.createElement("tr");
      for(const cell of row){ const td=document.createElement("td");td.textContent=String(cell);trBody.append(td); }tbody.append(trBody); }
    document.getElementById("table-caption").textContent=caption;
  }
  function drawComposition(){
    const a=dataset.fase1_2024;
    const values=[{name:"Neoplasias malignas",v:a.obitos_rs_cancer,color:"#0a8f94"},{name:"Demais causas",v:a.obitos_rs_demais_causas,color:"#0e425d"}];
    const svg=svgCanvas("Composição dos óbitos entre residentes do RS em 2024", "Duas barras: neoplasias malignas 21.072 e demais causas 80.408, total de 101.480 óbitos no recorte.");
    const margin={top:48,right:78,bottom:62,left:155},w=660,h=340;
    const x=d3.scaleLinear().domain([0,85000]).range([margin.left,w-margin.right]);
    const y=d3.scaleBand().domain(values.map(d=>d.name)).range([margin.top,230]).padding(.32);
    svg.append("g").attr("class","grid").attr("transform","translate(0,230)").call(d3.axisBottom(x).ticks(4).tickSize(-184).tickFormat(""));
    const bottom=svg.append("g").attr("class","axis").attr("transform","translate(0,230)").call(d3.axisBottom(x).ticks(4).tickFormat(tickFormat));axisStyles(bottom);
    const left=svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0));left.select("path").remove();axisStyles(left);
    svg.selectAll(".composition-bar").data(values).join("rect").attr("x",margin.left).attr("y",d=>y(d.name)).attr("height",y.bandwidth()).attr("width",d=>x(d.v)-margin.left).attr("fill",d=>d.color).attr("rx",4);
    svg.selectAll(".composition-value").data(values).join("text").attr("class","value-label").attr("x",d=>x(d.v)+10).attr("y",d=>y(d.name)+y.bandwidth()/2+5).text(d=>integer.format(d.v));
    svg.append("text").attr("x",w/2).attr("y",306).attr("text-anchor","middle").attr("font-weight",750).attr("font-size",13).text("Número de óbitos (contagem absoluta)");
    const pct=(a.obitos_rs_cancer/a.obitos_rs_todas_causas*100).toFixed(1).replace(".",",");
    summary.textContent=`Em 2024, ${integer.format(a.obitos_rs_cancer)} de ${integer.format(a.obitos_rs_todas_causas)} óbitos de residentes do RS foram atribuídos a neoplasias malignas (${pct}% dos registros desse recorte).`;
    addTable(["Grupo de causas","Óbitos em 2024"],values.map(d=>[d.name,integer.format(d.v)]),"Composição dos óbitos registrados, RS, 2024");
  }
  function drawCid10(){
    const values=dataset.fase1_2024.top_cid10_tres_caracteres;
    const svg=svgCanvas("Dez códigos CID-10 com maiores contagens de óbitos, RS 2024", "C34: 3609; C18: 1596; C50: 1433; C25: 1389; C61: 1283; C22: 924; C15: 857; C16: 856; C71: 717; C67: 518.");
    const w=660,h=340,m={left:72,right:70,top:18,bottom:60};
    const x=d3.scaleLinear().domain([0,4000]).range([m.left,w-m.right]);
    const y=d3.scaleBand().domain(values.map(d=>d.codigo)).range([m.top,h-m.bottom]).padding(.18);
    ggplotGridX(svg,x,m.top,h-m.bottom,4);
    const bottom=svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.bottom})`).call(d3.axisBottom(x).ticks(4).tickFormat(tickFormat));axisStyles(bottom);
    const left=svg.append("g").attr("class","axis").attr("transform",`translate(${m.left},0)`).call(d3.axisLeft(y).tickSize(0));left.select("path").remove();axisStyles(left);
    svg.selectAll(".cid-bar").data(values).join("rect").attr("x",m.left).attr("y",d=>y(d.codigo)).attr("width",d=>x(d.obitos)-m.left).attr("height",y.bandwidth()).attr("rx",3).attr("fill",(d,i)=>i===0?"#078b95":"#23657a");
    svg.selectAll(".cid-label").data(values).join("text").attr("class","bar-label").attr("x",d=>x(d.obitos)+6).attr("y",d=>y(d.codigo)+y.bandwidth()/2+4).text(d=>integer.format(d.obitos));
    svg.append("text").attr("x",w/2).attr("y",326).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",750).text("Número de óbitos (contagem absoluta)");
    summary.textContent=`O código C34 (brônquios e pulmão) lidera entre os grupos CID-10 de três caracteres apresentados em 2024, com ${integer.format(values[0].obitos)} óbitos. Os dez grupos são uma seleção, não o total das neoplasias.`;
    addTable(["CID-10","Descrição resumida","Óbitos em 2024"],values.map(d=>[d.codigo,d.descricao,integer.format(d.obitos)]),"Dez códigos CID-10 com maiores contagens, RS, 2024");
  }
  function seriesMetric(){ return step===2 ? "obitos" : step===3 ? "taxa_bruta" : "taxa_padronizada"; }
  function drawSeries(){
    const key=seriesMetric();
    const selectedSexes=sex==="Ambos"?["Feminino","Masculino"]:[sex];
    const rows=dataset.series.filter(d=>selectedSexes.includes(d.sexo));
    const years=d3.range(2015,2025);
    const maxValue=d3.max(rows,d=>d[key]);
    const ymax=key==="obitos"?13000:Math.ceil(maxValue/50)*50;
    const svg=svgCanvas(chapters[step].title,`Séries anuais de 2015 a 2024 por sexo. Indicador: ${key}. Ano em destaque: ${year}.`);
    const w=660,h=340,m={top:33,right:40,bottom:63,left:67};
    const x=d3.scaleLinear().domain([2015,2024]).range([m.left,w-m.right]);
    const y=d3.scaleLinear().domain([0,ymax]).range([h-m.bottom,m.top]);
    background(svg,m,w,h,y,5);
    ggplotGridX(svg,x,m.top,h-m.bottom,5);
    const xaxis=svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.bottom})`).call(d3.axisBottom(x).ticks(5).tickFormat(d3.format("d")));axisStyles(xaxis);
    const yaxis=svg.append("g").attr("class","axis").attr("transform",`translate(${m.left},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(key==="obitos"?(v=>v===0?"0":`${v/1000} mil`):(v=>integer.format(v))));axisStyles(yaxis);
    svg.append("line").attr("x1",x(year)).attr("x2",x(year)).attr("y1",m.top).attr("y2",h-m.bottom).attr("stroke","#9db8b8").attr("stroke-dasharray","4 5");
    const line=d3.line().x(d=>x(d.ano)).y(d=>y(d[key]));
    for(const s of selectedSexes){
      const group=rows.filter(d=>d.sexo===s).sort((a,b)=>a.ano-b.ano);
      svg.append("path").datum(group).attr("class","series-line").attr("d",line).attr("stroke",colors[s]);
      svg.selectAll(`.point-${s}`).data(group).join("circle").attr("class","dot-point").attr("cx",d=>x(d.ano)).attr("cy",d=>y(d[key])).attr("r",d=>d.ano===year?6:3.4).attr("fill",colors[s]);
      const current=group.find(d=>d.ano===year);
      svg.append("circle").attr("cx",x(year)).attr("cy",y(current[key])).attr("r",9).attr("fill","none").attr("stroke",colors[s]).attr("stroke-width",1.8);
    }
    const legend=svg.append("g").attr("class","legend").attr("transform",`translate(${m.left+8},15)`);
    selectedSexes.forEach((s,i)=>{legend.append("line").attr("x1",i*134).attr("x2",i*134+20).attr("y1",0).attr("y2",0).attr("stroke",colors[s]).attr("stroke-width",3);legend.append("text").attr("x",i*134+26).attr("y",4).text(s);});
    svg.append("text").attr("x",w/2).attr("y",326).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",750).text("Ano do óbito");
    const fmt=(v)=>key==="obitos"?integer.format(v):decimal.format(v)+" por 100 mil";
    const selected=rows.filter(d=>d.ano===year).sort((a,b)=>a.sexo.localeCompare(b.sexo));
    summary.textContent=`Em ${year}: ${selected.map(d=>`${d.sexo}: ${fmt(d[key])}`).join("; ")}. ${key==="obitos"?"São contagens classificadas, não medidas de risco.":key==="taxa_bruta"?"A taxa bruta não é ajustada por idade.":"Padrão etário: população conjunta do RS em 2024."}`;
    addTable(["Ano","Sexo",key==="obitos"?"Óbitos classificados":"Taxa por 100 mil habitantes"],rows.slice().sort((a,b)=>a.ano-b.ano||a.sexo.localeCompare(b.sexo)).map(d=>[d.ano,d.sexo,fmt(d[key])]),`Série anual: ${chapters[step].title}`);
  }
  function drawTrend(){
    const rows=dataset.tendencias.filter(d=>d.modelo==="Linear").sort((a,b)=>a.sexo.localeCompare(b.sexo));
    const svg=svgCanvas("APC linear anual e intervalos de confiança CR2", "Feminino: estimativa -0,4144 por cento, IC de -0,8788 a +0,0522; masculino: -1,6318, IC de -1,9945 a -1,2677.");
    const m={left:125,right:52,top:66,bottom:82},w=660,h=340;
    const x=d3.scaleLinear().domain([-2.3,.6]).range([m.left,w-m.right]);
    const y=d3.scalePoint().domain(rows.map(d=>d.sexo)).range([104,210]);
    ggplotGridX(svg,x,63,247,6);
    const bottom=svg.append("g").attr("class","axis").attr("transform","translate(0,247)").call(d3.axisBottom(x).ticks(6).tickFormat(v=>`${decimal.format(v)}%`));axisStyles(bottom);
    const left=svg.append("g").attr("class","axis").attr("transform",`translate(${m.left},0)`).call(d3.axisLeft(y).tickSize(0));left.select("path").remove();axisStyles(left);
    svg.append("line").attr("class","zero-line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",63).attr("y2",247);
    rows.forEach(d=>{
      svg.append("line").attr("x1",x(d.inferior)).attr("x2",x(d.superior)).attr("y1",y(d.sexo)).attr("y2",y(d.sexo)).attr("stroke",colors[d.sexo]).attr("stroke-width",4);
      svg.append("circle").attr("cx",x(d.apc)).attr("cy",y(d.sexo)).attr("r",8).attr("fill",colors[d.sexo]).attr("stroke","white").attr("stroke-width",2);
      for(const v of [d.inferior,d.superior]) svg.append("line").attr("x1",x(v)).attr("x2",x(v)).attr("y1",y(d.sexo)-8).attr("y2",y(d.sexo)+8).attr("stroke",colors[d.sexo]).attr("stroke-width",2.5);
      svg.append("text").attr("x",x(d.apc)).attr("y",y(d.sexo)-17).attr("font-size",12).attr("font-weight",750).attr("text-anchor","middle").text(`${decimal4.format(d.apc)}%`);
    });
    svg.append("text").attr("x",w/2).attr("y",316).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",750).text("Variação percentual anual (APC)");
    summary.textContent="Modelo linear com CR2/Satterthwaite: Masculino −1,6318%/ano (IC95% −1,9945 a −1,2677); Feminino −0,4144%/ano (IC95% −0,8788 a +0,0522). O intervalo feminino inclui zero.";
    addTable(["Sexo","APC anual","IC95% inferior","IC95% superior","p CR2"],rows.map(d=>[d.sexo,`${decimal4.format(d.apc)}%`,`${decimal4.format(d.inferior)}%`,`${decimal4.format(d.superior)}%`,d.p]),"Tendência linear: estimativas transcritas da auditoria, não recalculadas");
  }
  function drawAudit(){
    const rows=dataset.conciliacao;
    const svg=svgCanvas("Registros fora das séries classificadas por ano", "Diferenças de 1,0,1,6,0,0,6,5,0,0 de 2015 a 2024, total 19.");
    const w=660,h=340,m={left:61,right:29,top:30,bottom:73};
    const x=d3.scaleBand().domain(rows.map(d=>d.ano)).range([m.left,w-m.right]).padding(.23);
    const y=d3.scaleLinear().domain([0,7]).range([h-m.bottom,m.top]);
    background(svg,m,w,h,y,7);
    ggplotGridX(svg,x,m.top,h-m.bottom,5);
    const xaxis=svg.append("g").attr("class","axis").attr("transform",`translate(0,${h-m.bottom})`).call(d3.axisBottom(x).tickSize(0));axisStyles(xaxis);
    const yaxis=svg.append("g").attr("class","axis").attr("transform",`translate(${m.left},0)`).call(d3.axisLeft(y).ticks(7).tickFormat(d3.format("d")));axisStyles(yaxis);
    svg.selectAll(".audit-bar").data(rows).join("rect").attr("x",d=>x(d.ano)).attr("y",d=>y(d.diferenca)).attr("height",d=>y(0)-y(d.diferenca)).attr("width",x.bandwidth()).attr("fill","#0e8194").attr("rx",2);
    svg.selectAll(".audit-label").data(rows).join("text").attr("class","value-label").attr("x",d=>x(d.ano)+x.bandwidth()/2).attr("y",d=>y(d.diferenca)-8).attr("text-anchor","middle").text(d=>d.diferenca);
    svg.append("text").attr("x",w/2).attr("y",326).attr("text-anchor","middle").attr("font-size",13).attr("font-weight",750).text("Ano do óbito");
    summary.textContent="Entre 2015 e 2024: 194.368 óbitos totais, 194.349 classificados e 19 não incluídos nos estratos por sexo/idade. Confrontos SIM × TabNet: 20.234 em 2022 e 20.291 em 2023, com diferenças iguais a zero.";
    addTable(["Ano","Óbitos totais","Classificados","Fora das séries"],rows.map(d=>[d.ano,integer.format(d.total),integer.format(d.classificados),d.diferenca]),"Conciliação anual das contagens SIM, 2015–2024");
  }
  function render(){
    const c=chapters[step];
    chartTitle.textContent=c.title;
    chartDeck.textContent=c.deck;
    caution.textContent=c.caution;
    controls.hidden=!(step>=2 && step<=4);
    document.getElementById("chapter-index").textContent=`CAPÍTULO ${String(step+1).padStart(2,"0")} / 07`;
    document.getElementById("pager-state").textContent=`${String(step+1).padStart(2,"0")} de 07`;
    document.getElementById("prev").disabled=step===0;
    document.getElementById("next").disabled=step===6;
    yearLabel.textContent=year;
    stepButtons.forEach((b,i)=>{b.classList.toggle("active",i===step);b.setAttribute("aria-pressed",String(i===step));});
    if(step===0) drawComposition();
    else if(step===1) drawCid10();
    else if(step<=4) drawSeries();
    else if(step===5) drawTrend();
    else drawAudit();
  }
  function changeStep(next){
    if(next<0||next>6||!dataset)return;
    step=next;
    render();
  }
  stepButtons.forEach(b=>b.addEventListener("click",()=>changeStep(Number(b.dataset.step))));
  sexButtons.forEach(b=>b.addEventListener("click",()=>{
    sex=b.dataset.sex;
    sexButtons.forEach(other=>{const on=other===b;other.classList.toggle("selected",on);other.setAttribute("aria-pressed",String(on));});
    if(dataset && step>=2 && step<=4)render();
  }));
  yearInput.addEventListener("input",()=>{ year=Number(yearInput.value);if(dataset && step>=2 && step<=4)render(); });
  document.getElementById("prev").addEventListener("click",()=>changeStep(step-1));
  document.getElementById("next").addEventListener("click",()=>changeStep(step+1));
  document.getElementById("show-data").addEventListener("click",()=>{
    const isHidden=tablePanel.hidden;
    tablePanel.hidden=!isHidden;
    const button=document.getElementById("show-data");
    button.setAttribute("aria-expanded",String(isHidden));
    button.textContent=isHidden?"Ocultar tabela acessível":"Ver tabela acessível";
  });
  async function init(){
    if(typeof d3==="undefined"){
      chart.innerHTML="";
      const p=document.createElement("p");p.className="fallback-msg";p.textContent="A biblioteca D3 local não foi encontrada. Execute iniciar.ps1 para instalar a dependência. Os resultados científicos resumidos continuam disponíveis na página.";chart.append(p);
      return;
    }
    try{
      const response=await fetch("data/story.json",{cache:"no-store"});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      dataset=await response.json();
      if(dataset.resumo_2015_2024.total!==194368 || dataset.series.length!==20 || dataset.fase1_2024.obitos_rs_cancer!==21072) throw new Error("Dados resumidos divergentes da versão validada.");
      render();
    }catch(error){
      chart.replaceChildren();
      const p=document.createElement("p");p.className="fallback-msg";p.textContent=`O gráfico não pôde carregar os dados agregados locais. Verifique o servidor HTTP e a pasta data/. Detalhe: ${error.message}`;chart.append(p);
    }
  }
  init();
})();
