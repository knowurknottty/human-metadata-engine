/* Deterministic, offline Tarot card illustration renderer. No remote assets. */
(() => {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const CARD_ASSETS = Object.freeze({
    "cups-01": "/assets/tarot/cups-01.webp",
    "cups-02": "/assets/tarot/cups-02.webp",
    "cups-03": "/assets/tarot/cups-03.webp",
    "cups-04": "/assets/tarot/cups-04.webp",
    "cups-05": "/assets/tarot/cups-05.webp",
    "cups-06": "/assets/tarot/cups-06.webp",
    "cups-07": "/assets/tarot/cups-07.webp",
    "cups-08": "/assets/tarot/cups-08.webp",
    "cups-09": "/assets/tarot/cups-09.webp",
    "cups-10": "/assets/tarot/cups-10.webp",
    "cups-11": "/assets/tarot/cups-11.webp",
    "cups-12": "/assets/tarot/cups-12.webp",
    "cups-13": "/assets/tarot/cups-13.webp",
    "cups-14": "/assets/tarot/cups-14.webp",
    "major-00": "/assets/tarot/major-00-seeker.webp",
    "major-01": "/assets/tarot/major-01-alchemist.webp",
    "major-02": "/assets/tarot/major-02-mirror.webp",
    "major-03": "/assets/tarot/major-03-weaver-many-one.webp",
    "major-04": "/assets/tarot/major-04-builder.webp",
    "major-05": "/assets/tarot/major-05-beacon.webp",
    "major-06": "/assets/tarot/major-06-bridge.webp",
    "major-07": "/assets/tarot/major-07-signal.webp",
    "major-08": "/assets/tarot/major-08-weaver-patterns.webp",
    "major-09": "/assets/tarot/major-09-lantern.webp",
    "major-10": "/assets/tarot/major-10-wheel.webp",
    "major-11": "/assets/tarot/major-11-justice.webp",
    "major-12": "/assets/tarot/major-12-suspension.webp",
    "major-13": "/assets/tarot/major-13.webp",
    "major-14": "/assets/tarot/major-14.webp",
    "major-15": "/assets/tarot/major-15.webp",
    "major-16": "/assets/tarot/major-16.webp",
    "major-17": "/assets/tarot/major-17.webp",
    "major-18": "/assets/tarot/major-18.webp",
    "major-19": "/assets/tarot/major-19.webp",
    "major-20": "/assets/tarot/major-20.webp",
    "major-21": "/assets/tarot/major-21.webp",
    "pentacles-01": "/assets/tarot/pentacles-01.webp",
    "pentacles-02": "/assets/tarot/pentacles-02.webp",
    "pentacles-03": "/assets/tarot/pentacles-03.webp",
    "pentacles-04": "/assets/tarot/pentacles-04.webp",
    "pentacles-05": "/assets/tarot/pentacles-05.webp",
    "pentacles-06": "/assets/tarot/pentacles-06.webp",
    "pentacles-07": "/assets/tarot/pentacles-07.webp",
    "pentacles-08": "/assets/tarot/pentacles-08.webp",
    "pentacles-09": "/assets/tarot/pentacles-09.webp",
    "pentacles-10": "/assets/tarot/pentacles-10.webp",
    "pentacles-11": "/assets/tarot/pentacles-11.webp",
    "pentacles-12": "/assets/tarot/pentacles-12.webp",
    "pentacles-13": "/assets/tarot/pentacles-13.webp",
    "pentacles-14": "/assets/tarot/pentacles-14.webp",
    "swords-01": "/assets/tarot/swords-01.webp",
    "swords-02": "/assets/tarot/swords-02.webp",
    "swords-03": "/assets/tarot/swords-03.webp",
    "swords-04": "/assets/tarot/swords-04.webp",
    "swords-05": "/assets/tarot/swords-05.webp",
    "swords-06": "/assets/tarot/swords-06.webp",
    "swords-07": "/assets/tarot/swords-07.webp",
    "swords-08": "/assets/tarot/swords-08.webp",
    "swords-09": "/assets/tarot/swords-09.webp",
    "swords-10": "/assets/tarot/swords-10.webp",
    "swords-11": "/assets/tarot/swords-11.webp",
    "swords-12": "/assets/tarot/swords-12.webp",
    "swords-13": "/assets/tarot/swords-13.webp",
    "swords-14": "/assets/tarot/swords-14.webp",
    "wands-01": "/assets/tarot/wands-01.webp",
    "wands-02": "/assets/tarot/wands-02.webp",
    "wands-03": "/assets/tarot/wands-03.webp",
    "wands-04": "/assets/tarot/wands-04.webp",
    "wands-05": "/assets/tarot/wands-05.webp",
    "wands-06": "/assets/tarot/wands-06.webp",
    "wands-07": "/assets/tarot/wands-07.webp",
    "wands-08": "/assets/tarot/wands-08.webp",
    "wands-09": "/assets/tarot/wands-09.webp",
    "wands-10": "/assets/tarot/wands-10.webp",
    "wands-11": "/assets/tarot/wands-11.webp",
    "wands-12": "/assets/tarot/wands-12.webp",
    "wands-13": "/assets/tarot/wands-13.webp",
    "wands-14": "/assets/tarot/wands-14.webp",
  });
  const MAJOR_ASSETS = Object.freeze({
    0: CARD_ASSETS["major-00"],
    1: CARD_ASSETS["major-01"],
    2: CARD_ASSETS["major-02"],
    3: CARD_ASSETS["major-03"],
    4: CARD_ASSETS["major-04"],
    5: CARD_ASSETS["major-05"],
    6: CARD_ASSETS["major-06"],
    7: CARD_ASSETS["major-07"],
    8: CARD_ASSETS["major-08"],
    9: CARD_ASSETS["major-09"],
    10: CARD_ASSETS["major-10"],
    11: CARD_ASSETS["major-11"],
    12: CARD_ASSETS["major-12"],
    13: CARD_ASSETS["major-13"],
    14: CARD_ASSETS["major-14"],
    15: CARD_ASSETS["major-15"],
    16: CARD_ASSETS["major-16"],
    17: CARD_ASSETS["major-17"],
    18: CARD_ASSETS["major-18"],
    19: CARD_ASSETS["major-19"],
    20: CARD_ASSETS["major-20"],
    21: CARD_ASSETS["major-21"],
  });
  const MAJOR_SCENES = [
    "wanderer","tools","pillars","garden","throne","arch","choice","chariot","strength","lantern","wheel",
    "scales","suspension","renewal","vessels","chain","tower","star","moon","sun","call","wreath",
  ];
  const SUITS = {
    Wands: {tone:"#d9a441", accent:"#7a3e1f"}, Cups: {tone:"#77c8cf", accent:"#255f73"},
    Swords: {tone:"#b9c4d2", accent:"#4a5365"}, Pentacles: {tone:"#e3bd62", accent:"#6f5521"},
  };
  const COURTS = {11:"PAGE",12:"KNIGHT",13:"QUEEN",14:"KING"};
  const make = (tag, attrs = {}) => {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
    return node;
  };
  const add = (parent, tag, attrs = {}) => { const node = make(tag, attrs); parent.append(node); return node; };
  const seed = text => [...String(text)].reduce((value, ch) => ((value * 33) ^ ch.charCodeAt(0)) >>> 0, 5381);
  const rng = value => () => ((value = Math.imul(1664525, value) + 1013904223 >>> 0) / 4294967296);
  const base = card => {
    const svg = make("svg", {viewBox:"0 0 220 280", focusable:"false", "aria-hidden":"true"});
    const random = rng(seed(card.id || card.name));
    add(svg,"rect",{x:2,y:2,width:216,height:276,rx:8,fill:"#0b1017",stroke:"#d7ad59","stroke-width":2});
    add(svg,"rect",{x:11,y:11,width:198,height:258,rx:5,fill:"none",stroke:"#53606d","stroke-width":1});
    for (let i=0;i<20;i+=1) add(svg,"circle",{cx:18+random()*184,cy:22+random()*220,r:.6+random()*1.2,fill:i%4===0?"#d7ad59":"#8a96a4",opacity:.35+random()*.45});
    add(svg,"path",{d:"M30 229 Q110 247 190 229",fill:"none",stroke:"#d7ad59","stroke-width":1,opacity:.55});
    return svg;
  };
  const suitSymbol = (parent, suit, x, y, scale=1) => {
    const cfg=SUITS[suit] || SUITS.Pentacles;
    const g=add(parent,"g",{transform:`translate(${x} ${y}) scale(${scale})`,stroke:cfg.tone,fill:"none","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"});
    if (suit === "Wands") { add(g,"path",{d:"M0 13 L0 -13"}); add(g,"path",{d:"M0 -5 C-8 -10 -9 -3 -3 1 M0 4 C8 -1 9 6 3 9"}); }
    else if (suit === "Cups") { add(g,"path",{d:"M-9 -11 H9 L6 0 Q0 8 -6 0 Z M0 7 V13 M-6 13 H6"}); }
    else if (suit === "Swords") { add(g,"path",{d:"M0 -15 V11 M-8 5 H8 M-3 11 L0 15 L3 11"}); }
    else { add(g,"circle",{cx:0,cy:0,r:12}); add(g,"path",{d:"M0 -10 L2.9 -3.2 L10 -3.1 L4.6 1.3 L6.3 8.2 L0 4.4 L-6.3 8.2 L-4.6 1.3 L-10 -3.1 L-2.9 -3.2 Z"}); }
    return g;
  };
  const pipPositions = count => {
    const layouts = {
      1:[[110,128]], 2:[[110,88],[110,168]], 3:[[110,72],[110,128],[110,184]],
      4:[[78,88],[142,88],[78,168],[142,168]], 5:[[78,78],[142,78],[110,128],[78,178],[142,178]],
      6:[[78,72],[142,72],[78,128],[142,128],[78,184],[142,184]],
      7:[[78,64],[142,64],[78,112],[142,112],[110,148],[78,192],[142,192]],
      8:[[78,60],[142,60],[78,104],[142,104],[78,152],[142,152],[78,196],[142,196]],
      9:[[78,58],[142,58],[78,100],[142,100],[110,128],[78,158],[142,158],[78,200],[142,200]],
      10:[[78,52],[142,52],[78,88],[142,88],[78,124],[142,124],[78,160],[142,160],[78,196],[142,196]],
    };
    return layouts[count] || [[110,128]];
  };
  const renderPips = (svg, card) => {
    const cfg=SUITS[card.suit];
    add(svg,"circle",{cx:110,cy:127,r:82,fill:cfg.accent,opacity:.09,stroke:cfg.tone,"stroke-width":1});
    for(const [x,y] of pipPositions(card.number)) suitSymbol(svg,card.suit,x,y,card.number>=8?.7:.86);
    add(svg,"text",{x:110,y:218,"text-anchor":"middle",fill:cfg.tone,"font-size":13,"font-family":"Georgia,serif","letter-spacing":3}).textContent=String(card.number);
  };
  const renderCourt = (svg, card) => {
    const cfg=SUITS[card.suit], rank=COURTS[card.number] || "COURT";
    const yShift = {11:6,12:-2,13:-6,14:-10}[card.number] || 0;
    add(svg,"circle",{cx:110,cy:82+yShift,r:25,fill:"#111923",stroke:cfg.tone,"stroke-width":2});
    add(svg,"path",{d:"M66 194 Q72 116 110 110 Q148 116 154 194 Z",fill:cfg.accent,opacity:.4,stroke:cfg.tone,"stroke-width":2});
    if (card.number === 11) add(svg,"path",{d:"M86 60 Q110 44 134 60",fill:"none",stroke:cfg.tone,"stroke-width":3});
    if (card.number === 12) add(svg,"path",{d:"M82 67 L110 40 L138 67",fill:"none",stroke:cfg.tone,"stroke-width":3});
    if (card.number === 13) add(svg,"path",{d:"M84 60 L96 43 L110 58 L124 43 L136 60",fill:"none",stroke:cfg.tone,"stroke-width":3});
    if (card.number === 14) add(svg,"path",{d:"M80 61 L92 39 L110 56 L128 39 L140 61 L136 70 H84 Z",fill:"none",stroke:cfg.tone,"stroke-width":3});
    suitSymbol(svg,card.suit,110,146,1.28);
    add(svg,"text",{x:110,y:218,"text-anchor":"middle",fill:cfg.tone,"font-size":12,"font-family":"system-ui,sans-serif","font-weight":700,"letter-spacing":3}).textContent=rank;
  };
  const renderMajor = (svg, card) => {
    const n=Number(card.number)||0, scene=MAJOR_SCENES[n] || "major", random=rng(seed(card.id || scene));
    const gold="#d7ad59", pale="#c9d2dc", cyan="#6bb7c4";
    add(svg,"circle",{cx:110,cy:127,r:83,fill:"#111923",stroke:gold,"stroke-width":1.2});
    for(let ring=0;ring<3;ring+=1) add(svg,"ellipse",{cx:110,cy:125,rx:48+ring*15,ry:24+ring*21,fill:"none",stroke:ring===1?cyan:pale,"stroke-width":1,opacity:.35+ring*.12,transform:`rotate(${(n*17+ring*31)%180} 110 125)`});
    for(let i=0;i<5+(n%5);i+=1){const angle=(Math.PI*2*i)/(5+(n%5))+(n*.13),rad=34+(i%3)*16;add(svg,"circle",{cx:110+Math.cos(angle)*rad,cy:126+Math.sin(angle)*rad,r:2.5+(i%2)*1.4,fill:i%2?cyan:gold});}
    const mode=n%5;
    if(mode===0) add(svg,"path",{d:"M70 181 L110 72 L150 181 Z",fill:"none",stroke:gold,"stroke-width":3});
    if(mode===1){ add(svg,"circle",{cx:110,cy:126,r:38,fill:"none",stroke:gold,"stroke-width":4}); add(svg,"line",{x1:110,y1:72,x2:110,y2:180,stroke:pale,"stroke-width":2}); }
    if(mode===2) add(svg,"path",{d:"M65 178 Q110 58 155 178 M79 178 Q110 94 141 178",fill:"none",stroke:gold,"stroke-width":3});
    if(mode===3) add(svg,"path",{d:"M110 70 L121 107 L160 107 L128 130 L140 168 L110 145 L80 168 L92 130 L60 107 L99 107 Z",fill:"none",stroke:gold,"stroke-width":3});
    if(mode===4){ add(svg,"rect",{x:72,y:88,width:76,height:82,rx:6,fill:"none",stroke:gold,"stroke-width":3}); add(svg,"path",{d:"M72 130 H148 M110 88 V170",stroke:cyan,"stroke-width":2}); }
    for(let i=0;i<4;i+=1){const x=55+random()*110,y=82+random()*92;add(svg,"line",{x1:110,y1:126,x2:x,y2:y,stroke:pale,"stroke-width":.8,opacity:.5});}
    add(svg,"text",{x:110,y:36,"text-anchor":"middle",fill:gold,"font-size":13,"font-family":"Georgia,serif","letter-spacing":2}).textContent=n===0?"0":String(n);
    add(svg,"text",{x:110,y:220,"text-anchor":"middle",fill:pale,"font-size":9,"font-family":"system-ui,sans-serif","letter-spacing":2}).textContent=scene.toUpperCase();
  };
  const renderFallbackArt = card => {
    const svg=base(card);
    if(card.arcana === "Major") renderMajor(svg,card);
    else if(card.number >= 11) renderCourt(svg,card);
    else renderPips(svg,card);
    return svg;
  };
  const renderCardArt = card => {
    const wrap=document.createElement("div");
    wrap.className="tarot-card-art";
    wrap.dataset.cardArt=card.id || card.name;

    const majorIndex = card.arcana === "Major" ? Number(card.number) : -1;
    const asset = CARD_ASSETS[card.id] || MAJOR_ASSETS[majorIndex];
    if (asset) {
      const img=document.createElement("img");
      img.className="tarot-card-art-image";
      img.src=asset;
      img.alt="";
      img.loading="lazy";
      img.decoding="async";
      img.draggable=false;
      img.setAttribute("aria-hidden","true");
      img.addEventListener("error", () => {
        if (img.isConnected) img.replaceWith(renderFallbackArt(card));
      }, {once:true});
      wrap.classList.add("tarot-card-art--library");
      wrap.append(img);
      return wrap;
    }

    wrap.append(renderFallbackArt(card));
    return wrap;
  };
  window.TarotArt = Object.freeze({CARD_ASSETS, MAJOR_ASSETS, MAJOR_SCENES, pipPositions, renderMajor, renderPips, renderCourt, renderFallbackArt, renderCardArt});
})();
