(function(){const S=document.currentScript.closest(".dd"),V=JSON.parse(S.querySelector(".dd-data").textContent),R=S.dataset.root;
const q=c=>S.querySelector(c);
function cur(){const h=location.hash.replace("#","");return V[h]?h:R}
function path(id){const p=[];for(let c=id;c;c=V[c].parent)p.unshift(c);return p}
function go(id){if(location.hash!=="#"+id)history.pushState(null,"","#"+id);render()}
function render(){const id=cur(),v=V[id];
 q(".dd-crumbs").textContent=path(id).map(c=>"Level "+V[c].level+": "+V[c].title).join(" › ");
 q(".dd-title").textContent=v.title;q(".dd-lead").textContent=v.lead;
 const dg=q(".dd-diagram");dg.innerHTML=v.svg;
 dg.querySelectorAll("[data-go]").forEach(g=>{g.addEventListener("click",()=>go(g.dataset.go));g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();go(g.dataset.go)}})});
 const hr=q(".dd-facts thead tr");hr.innerHTML="";v.head.forEach(h=>{const th=document.createElement("th");th.textContent=h;hr.appendChild(th)});
 const tb=q(".dd-facts tbody");tb.innerHTML="";
 v.facts.forEach((f,i)=>{const tr=document.createElement("tr");[i+1,f[0],f[1]].forEach(c=>{const td=document.createElement("td");td.textContent=c;tr.appendChild(td)});tb.appendChild(tr)});
 q(".dd-note").textContent=v.note;q(".dd-up").disabled=!v.parent}
q(".dd-up").addEventListener("click",()=>{const p=V[cur()].parent;if(p)go(p)});
q(".dd-home").addEventListener("click",()=>go(R));
window.addEventListener("popstate",render);window.addEventListener("hashchange",render);
render();if(V[location.hash.replace("#","")])S.scrollIntoView();})();
