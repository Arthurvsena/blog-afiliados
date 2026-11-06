import React from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

const ROXO = '#7C5CFF';
const ROXO2 = '#A693FF';
const FUNDO = '#050507';
const ROSA = '#FF5D73';
const FONTE = 'Inter Tight, Inter, sans-serif';

const fontes = `@font-face{font-family:'Inter Tight';src:url('${staticFile('InterTight.ttf')}') format('truetype');font-weight:100 900;}`;

// ---------- marca ----------
const Simbolo = ({s}) => (
  <svg width={s} height={s} viewBox="0 0 64 64">
    <rect x="4" y="4" width="56" height="56" rx="14" fill={ROXO} />
    <path d="M20 46V18l24 28V18" fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="20" cy="18" r="5" fill="#fff" /><circle cx="44" cy="46" r="5" fill="#fff" />
    <circle cx="20" cy="46" r="3.5" fill={FUNDO} /><circle cx="44" cy="18" r="3.5" fill={FUNDO} />
  </svg>
);

const Topo = ({selo, k, progresso, cenas, frame}) => (
  <>
    <div style={{position: 'absolute', top: 0, left: 0, right: 0, display: 'flex', gap: 6 * k, padding: `${14 * k}px ${30 * k}px 0`}}>
      {cenas.map((c, i) => {
        const p = Math.min(1, Math.max(0, (frame - c.ini) / c.dur));
        return (
          <div key={i} style={{flex: c.dur, height: 7 * k, borderRadius: 4 * k, background: 'rgba(255,255,255,.22)', overflow: 'hidden'}}>
            <div style={{width: `${p * 100}%`, height: '100%', background: '#fff'}} />
          </div>
        );
      })}
    </div>
    <div style={{position: 'absolute', top: 44 * k, left: 34 * k, right: 34 * k, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14 * k}}>
        <Simbolo s={72 * k} />
        <span style={{fontFamily: FONTE, fontWeight: 800, fontSize: 46 * k, color: '#fff', letterSpacing: -0.5 * k, textShadow: '0 2px 12px rgba(0,0,0,.6)'}}>
          Nexus <span style={{color: ROXO2}}>Tech</span>
        </span>
      </div>
      {selo ? (
        <span style={{fontFamily: FONTE, fontWeight: 700, fontSize: 34 * k, color: '#fff', padding: `${10 * k}px ${26 * k}px`, borderRadius: 999,
          background: 'rgba(10,10,14,.65)', border: `${2 * k}px solid rgba(255,255,255,.18)`, backdropFilter: 'blur(8px)'}}>{selo}</span>
      ) : null}
    </div>
  </>
);

// ---------- fundo com várias fotos ----------
const Foto = ({img, dur, i, vertical}) => {
  const f = useCurrentFrame();
  const dir = i % 2 === 0 ? 1 : -1;
  const z = interpolate(f, [0, dur], [1.06, 1.24], {extrapolateRight: 'clamp'});
  const x = interpolate(f, [0, dur], [-2.5 * dir, 2.5 * dir], {extrapolateRight: 'clamp'});
  const y = interpolate(f, [0, dur], [1.5, -1.5], {extrapolateRight: 'clamp'});
  const op = interpolate(f, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  if (img.produto) {
    return (
      <AbsoluteFill style={{opacity: op}}>
        <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #2a2350 0%, #0b0b12 70%)'}} />
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: vertical ? '28%' : 0}}>
          <div style={{width: vertical ? '74%' : '42%', aspectRatio: '1', borderRadius: 48, background: 'linear-gradient(160deg,#ffffff,#e9eaf0)',
            boxShadow: '0 40px 120px rgba(124,92,255,.45)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            transform: `scale(${interpolate(f, [0, dur], [0.96, 1.04])}) rotate(${interpolate(f, [0, dur], [-1.5 * dir, 1.5 * dir])}deg)`}}>
            <Img src={staticFile(img.src)} style={{width: '82%', height: '82%', objectFit: 'contain'}} />
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  if (vertical && (img.prop || 1) > 1.15) {
    // foto deitada num vídeo em pé: a foto INTEIRA no alto (nada cortado) e ela mesma desfocada de fundo
    const zc = interpolate(f, [0, dur], [1.0, 1.1], {extrapolateRight: 'clamp'});
    return (
      <AbsoluteFill style={{opacity: op, overflow: 'hidden'}}>
        <Img src={staticFile(img.src)} style={{width: '100%', height: '100%', objectFit: 'cover',
          filter: 'blur(30px) brightness(.45) saturate(1.2)', transform: `scale(${1.3 + f / 1200})`}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: '15%', aspectRatio: `${img.prop}`, overflow: 'hidden',
          boxShadow: '0 30px 90px rgba(0,0,0,.65)'}}>
          <Img src={staticFile(img.src)} style={{width: '100%', height: '100%', objectFit: 'cover',
            transform: `scale(${zc}) translate(${x * 0.6}%, 0)`}} />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{opacity: op, overflow: 'hidden'}}>
      <Img src={staticFile(img.src)} style={{width: '100%', height: '100%', objectFit: 'cover',
        transform: `scale(${z}) translate(${x}%, ${y}%)`}} />
    </AbsoluteFill>
  );
};

const FundoMarca = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: FUNDO}}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{position: 'absolute', width: '90%', aspectRatio: '1', borderRadius: '50%',
          left: `${30 + 25 * Math.sin(f / 40 + i * 2)}%`, top: `${20 + 20 * Math.cos(f / 50 + i)}%`, transform: 'translate(-50%,-50%)',
          border: `${10 - i * 3}px solid rgba(124,92,255,${0.6 - i * 0.18})`}} />
      ))}
    </AbsoluteFill>
  );
};

const Fundo = ({cena, vertical}) => {
  const imgs = cena.imagens || [];
  if (!imgs.length) return <FundoMarca />;
  const seg = Math.max(40, Math.floor(cena.dur / imgs.length));
  return (
    <AbsoluteFill style={{background: FUNDO}}>
      {imgs.map((img, i) => (
        <Sequence key={i} from={i * seg} durationInFrames={i === imgs.length - 1 ? cena.dur - i * seg + 12 : seg + 12} layout="none">
          <Foto img={img} dur={seg + 12} i={i + cena.n} vertical={vertical} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

// ---------- textos ----------
const Legenda = ({palavras, base, k, vertical, baixo, modo}) => {
  const f = useCurrentFrame() + base; // frame absoluto
  const {fps} = useVideoConfig();
  const atual = palavras.filter((w) => w.ini <= f).pop();
  if (!atual) return null;
  const grupo = palavras.filter((w) => w.g === atual.g);
  const ent = spring({frame: f - grupo[0].ini, fps, config: {damping: 14, stiffness: 180}});
  if (modo === 'frase') {
    // Histórias Tech: frase inteira, sóbria, sem destaque palavra a palavra
    const fade = interpolate(f - grupo[0].ini, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
    return (
      <div style={{position: 'absolute', left: 70 * k, right: 70 * k, top: vertical ? (baixo ? '78%' : '66%') : undefined, bottom: vertical ? undefined : 70 * k,
        textAlign: 'center', opacity: fade}}>
        <span style={{fontFamily: FONTE, fontWeight: 600, fontSize: (vertical ? 58 : 44) * k, lineHeight: 1.25, color: '#fff',
          background: 'rgba(5,5,7,.55)', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone', padding: `${6 * k}px ${16 * k}px`,
          borderRadius: 10 * k, textShadow: '0 2px 10px rgba(0,0,0,.8)'}}>{grupo.map((w) => w.t).join(' ')}</span>
      </div>
    );
  }
  return (
    <div style={{position: 'absolute', left: 50 * k, right: 50 * k, top: vertical ? (baixo ? '76%' : '58%') : undefined, bottom: vertical ? undefined : 70 * k,
      display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `${10 * k}px ${16 * k}px`,
      background: 'rgba(5,5,7,.62)', borderRadius: 28 * k, padding: `${18 * k}px ${20 * k}px`, backdropFilter: 'blur(6px)',
      transform: `translateY(${(1 - ent) * 40}px) scale(${0.9 + 0.1 * ent})`, opacity: ent}}>
      {grupo.map((w, i) => {
        const falando = w.ini <= f && f < w.fim;
        const dito = f >= w.ini;
        const pop = spring({frame: f - w.ini, fps, config: {damping: 10, stiffness: 260}});
        return (
          <span key={i} style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 84 : 58) * k, lineHeight: 1.05,
            textTransform: 'uppercase', letterSpacing: -1 * k, color: dito ? '#fff' : 'rgba(255,255,255,.55)',
            padding: `${2 * k}px ${12 * k}px`, borderRadius: 14 * k, background: falando ? ROXO : 'transparent',
            transform: `scale(${falando ? 1 + 0.08 * pop : 1}) rotate(${falando ? -2 : 0}deg)`,
            textShadow: falando ? 'none' : '0 4px 24px rgba(0,0,0,.9), 0 0 2px #000', WebkitTextStroke: falando ? 0 : `${2 * k}px rgba(0,0,0,.35)`}}>
            {w.t}
          </span>
        );
      })}
    </div>
  );
};

const Gancho = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const palavras = (cena.tela || '').split(/\s+/).filter(Boolean);
  const passo = Math.max(3, Math.floor(Math.min(cena.dur * 0.6, 40) / Math.max(1, palavras.length)));
  return (
    <AbsoluteFill style={{justifyContent: vertical ? 'flex-start' : 'center', alignItems: 'center', paddingTop: vertical ? '52%' : 0, paddingLeft: 60 * k, paddingRight: 60 * k}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `${4 * k}px ${18 * k}px`, maxWidth: vertical ? '100%' : '80%',
        background: 'rgba(5,5,7,.62)', backdropFilter: 'blur(14px)', padding: `${28 * k}px ${30 * k}px`, borderRadius: 28 * k,
        boxShadow: '0 20px 60px rgba(0,0,0,.6)', opacity: interpolate(f, [0, 6], [0, 1], {extrapolateRight: 'clamp'})}}>
        {palavras.map((p, i) => {
          const s = spring({frame: f - i * passo, fps, config: {damping: 9, stiffness: 220}});
          const destaque = i === palavras.length - 1 || /\d/.test(p);
          return (
            <span key={i} style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 118 : 92) * k, lineHeight: 1,
              textTransform: 'uppercase', letterSpacing: -2 * k, color: destaque ? '#fff' : '#fff',
              background: destaque ? ROXO : 'transparent', padding: destaque ? `${4 * k}px ${16 * k}px` : 0, borderRadius: 16 * k,
              opacity: s, transform: `scale(${interpolate(s, [0, 1], [2.2, 1])}) rotate(${interpolate(s, [0, 1], [i % 2 ? 6 : -6, 0])}deg)`,
              textShadow: destaque ? 'none' : '0 6px 30px rgba(0,0,0,.95)'}}>{p}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const formatar = (n) => n.toLocaleString('pt-BR');

const Numero = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const m = (cena.destaque || '').match(/^(\D*?)([\d.,]+)(.*)$/);
  let texto = cena.destaque || '';
  if (m) {
    const alvo = parseFloat(m[2].replace(/\./g, '').replace(',', '.'));
    const prog = interpolate(f, [4, 26], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
    const casas = m[2].includes(',') ? m[2].split(',')[1].length : 0;
    const v = alvo * prog;
    texto = m[1] + (casas ? v.toLocaleString('pt-BR', {minimumFractionDigits: casas, maximumFractionDigits: casas}) : formatar(Math.round(v))) + m[3];
  }
  const s = spring({frame: f, fps, config: {damping: 11, stiffness: 160}});
  const r = spring({frame: f - 10, fps, config: {damping: 14}});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', paddingBottom: vertical ? '10%' : 0}}>
      <div style={{transform: `scale(${interpolate(s, [0, 1], [0.4, 1])})`, opacity: s, textAlign: 'center'}}>
        <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 150 : 140) * k, color: '#fff', letterSpacing: -4 * k,
          textShadow: `0 0 60px ${ROXO}, 0 8px 40px rgba(0,0,0,.9)`, whiteSpace: 'nowrap'}}>{texto}</div>
        {cena.rotulo ? (
          <div style={{display: 'inline-block', marginTop: 18 * k, fontFamily: FONTE, fontWeight: 800, fontSize: (vertical ? 52 : 44) * k, color: '#fff',
            background: ROXO, padding: `${8 * k}px ${26 * k}px`, borderRadius: 16 * k, transform: `translateY(${(1 - r) * 60}px)`, opacity: r}}>{cena.rotulo}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const Produto = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = cena.produto || {};
  const s = spring({frame: f, fps, config: {damping: 15, stiffness: 120}});
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 30%, #2a2350 0%, #07070b 75%)', flexDirection: vertical ? 'column' : 'row',
      alignItems: 'center', justifyContent: 'center', gap: 40 * k, padding: `${150 * k}px ${60 * k}px ${vertical ? 520 : 120}px`}}>
      <div style={{width: vertical ? '78%' : '40%', aspectRatio: '1', borderRadius: 44 * k, background: 'linear-gradient(160deg,#fff,#e8e9ef)',
        boxShadow: `0 40px 140px rgba(124,92,255,.5)`, display: 'flex', alignItems: 'center', justifyContent: 'center',
        transform: `translateY(${(1 - s) * 300}px) rotate(${interpolate(f, [0, cena.dur], [-2, 2])}deg) scale(${interpolate(f, [0, cena.dur], [0.97, 1.03])})`}}>
        {p.imagem ? <Img src={staticFile(p.imagem)} style={{width: '84%', height: '84%', objectFit: 'contain'}} /> : null}
      </div>
      <div style={{width: vertical ? '100%' : '46%', textAlign: vertical ? 'center' : 'left'}}>
        {cena.capitulo ? <div style={{fontFamily: FONTE, fontWeight: 800, fontSize: 30 * k, color: ROXO2, textTransform: 'uppercase', letterSpacing: 2 * k,
          opacity: s}}>{cena.capitulo}</div> : null}
        <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 62 : 54) * k, color: '#fff', lineHeight: 1.05, marginTop: 8 * k,
          opacity: s, transform: `translateX(${(1 - s) * 80}px)`}}>{p.nome}</div>
        <div style={{display: 'flex', flexWrap: 'wrap', gap: 12 * k, marginTop: 22 * k, justifyContent: vertical ? 'center' : 'flex-start'}}>
          {(p.destaques || []).slice(0, 4).map((d, i) => {
            const c = spring({frame: f - 14 - i * 7, fps, config: {damping: 12}});
            return <span key={i} style={{fontFamily: FONTE, fontWeight: 700, fontSize: 30 * k, color: '#fff', background: 'rgba(124,92,255,.25)',
              border: `${2 * k}px solid ${ROXO}`, borderRadius: 999, padding: `${8 * k}px ${20 * k}px`, opacity: c, transform: `scale(${c})`}}>{d}</span>;
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Chamada = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 12}});
  const pulo = Math.sin(f / 4) * 14 * k;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', background: 'rgba(5,5,7,.55)'}}>
      <div style={{textAlign: 'center', transform: `scale(${s})`}}>
        <div style={{fontSize: 120 * k, transform: `translateY(${vertical ? -pulo : pulo}px)`, color: ROXO2, fontFamily: FONTE, fontWeight: 900}}>{vertical ? '↑' : '↓'}</div>
        <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 92 : 80) * k, color: '#fff', textTransform: 'uppercase', letterSpacing: -2 * k}}>
          {vertical ? 'Link na bio' : 'Links na descrição'}
        </div>
        <div style={{display: 'inline-block', marginTop: 24 * k, fontFamily: FONTE, fontWeight: 800, fontSize: 46 * k, color: '#fff', background: ROXO,
          padding: `${10 * k}px ${30 * k}px`, borderRadius: 18 * k}}>nexustechai.com.br</div>
        {cena.tela ? <div style={{marginTop: 34 * k, fontFamily: FONTE, fontWeight: 800, fontSize: 50 * k, color: '#fff', padding: `0 ${60 * k}px`}}>{cena.tela}</div> : null}
      </div>
    </AbsoluteFill>
  );
};


// ---------- ícones (cena info) ----------
const ICONES = {
  chip: <><rect x="14" y="10" width="36" height="44" rx="6"/><path d="M14 22h-6M14 32h-6M14 42h-6M50 22h6M50 32h6M50 42h6"/><rect x="22" y="20" width="20" height="24" rx="3"/></>,
  calendario: <><rect x="8" y="12" width="48" height="44" rx="6"/><path d="M8 26h48M20 6v12M44 6v12"/><path d="M18 36h6M30 36h6M42 36h6M18 46h6M30 46h6"/></>,
  caixa: <><path d="M8 20 32 8l24 12v26L32 58 8 46z"/><path d="M8 20l24 12 24-12M32 32v26"/></>,
  dinheiro: <><rect x="6" y="16" width="52" height="32" rx="5"/><circle cx="32" cy="32" r="8"/><path d="M14 24v16M50 24v16"/></>,
  tela: <><rect x="16" y="4" width="32" height="56" rx="6"/><path d="M28 52h8"/></>,
  dobravel: <><rect x="6" y="10" width="24" height="44" rx="4"/><rect x="34" y="10" width="24" height="44" rx="4"/><path d="M32 8v48"/></>,
  bateria: <><rect x="6" y="18" width="46" height="28" rx="5"/><path d="M56 26v12"/><path d="M14 26h14v12H14z"/></>,
  camera: <><rect x="6" y="16" width="52" height="38" rx="6"/><circle cx="32" cy="35" r="11"/><path d="M22 16l4-8h12l4 8"/></>,
  alerta: <><path d="M32 6 60 56H4z"/><path d="M32 24v14M32 46v2"/></>,
  check: <><circle cx="32" cy="32" r="26"/><path d="M20 33l8 8 16-18"/></>,
  wifi: <><path d="M6 24a38 38 0 0 1 52 0M14 33a26 26 0 0 1 36 0M22 42a14 14 0 0 1 20 0"/><circle cx="32" cy="51" r="3"/></>,
  carrinho: <><path d="M4 8h8l6 32h34l6-22H16"/><circle cx="24" cy="52" r="4"/><circle cx="48" cy="52" r="4"/></>,
  jogo: <><rect x="4" y="18" width="56" height="30" rx="14"/><path d="M18 27v12M12 33h12"/><circle cx="44" cy="30" r="2.5"/><circle cx="50" cy="37" r="2.5"/></>,
  ia: <><rect x="12" y="12" width="40" height="40" rx="8"/><path d="M24 4v8M40 4v8M24 52v8M40 52v8M4 24h8M4 40h8M52 24h8M52 40h8"/><path d="M24 40l6-16 6 16M26 35h8M42 24v16"/></>,
  cadeado: <><rect x="12" y="28" width="40" height="30" rx="5"/><path d="M20 28v-8a12 12 0 0 1 24 0v8"/><circle cx="32" cy="42" r="3"/></>,
  relogio: <><circle cx="32" cy="32" r="26"/><path d="M32 16v16l10 8"/></>,
};

const Info = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 10, stiffness: 140}});
  const pulso = 1 + 0.04 * Math.sin(f / 5);
  const d = interpolate(f, [0, 30], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const tam = (vertical ? 520 : 360) * k;
  return (
    <AbsoluteFill style={{background: 'transparent', alignItems: 'center',
      justifyContent: vertical ? 'flex-start' : 'center', paddingTop: vertical ? '36%' : 0}}>
      {[0, 1, 2].map((i) => {
        const r = ((f / 40 + i / 3) % 1);
        return <div key={i} style={{position: 'absolute', top: vertical ? '49.5%' : '50%', left: '50%', width: tam * (1 + r * 1.6), height: tam * (1 + r * 1.6),
          transform: 'translate(-50%,-50%)', borderRadius: '50%', border: `${4 * k}px solid rgba(124,92,255,${0.5 * (1 - r)})`}} />;
      })}
      <div style={{width: tam, height: tam, borderRadius: '50%', background: `linear-gradient(150deg, ${ROXO}, #4b2fd6)`, display: 'flex',
        alignItems: 'center', justifyContent: 'center', boxShadow: `0 30px 120px rgba(124,92,255,.6)`,
        transform: `scale(${s * pulso}) rotate(${interpolate(s, [0, 1], [-25, 0])}deg)`}}>
        <svg width={tam * 0.55} height={tam * 0.55} viewBox="0 0 64 64" fill="none" stroke="#fff" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"
          style={{strokeDasharray: 400, strokeDashoffset: 400 * (1 - d)}}>
          {ICONES[cena.icone] || ICONES.alerta}
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ---------- data (calendário) ----------
const Data = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const [mes, ano] = (cena.destaque || '').split(/\s+/);
  const s = spring({frame: f, fps, config: {damping: 12, stiffness: 120}});
  const vira = interpolate(f, [6, 22], [90, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.6))});
  const w = (vertical ? 560 : 380) * k;
  return (
    <AbsoluteFill style={{background: 'transparent', alignItems: 'center',
      justifyContent: vertical ? 'flex-start' : 'center', paddingTop: vertical ? '30%' : 0, perspective: 1600}}>
      <div style={{width: w, borderRadius: 40 * k, overflow: 'hidden', boxShadow: '0 40px 140px rgba(124,92,255,.55)', transform: `scale(${s})`}}>
        <div style={{background: ROSA, height: 150 * k, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 80 * k, position: 'relative'}}>
          <div style={{width: 26 * k, height: 26 * k, borderRadius: '50%', background: '#0a0a12'}} />
          <div style={{width: 26 * k, height: 26 * k, borderRadius: '50%', background: '#0a0a12'}} />
        </div>
        <div style={{background: '#fff', padding: `${30 * k}px 0 ${44 * k}px`, textAlign: 'center', transformOrigin: 'top', transform: `rotateX(${vira}deg)`}}>
          <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: 130 * k, color: '#0b0b12', lineHeight: 1, textTransform: 'uppercase'}}>{mes}</div>
          {ano ? <div style={{fontFamily: FONTE, fontWeight: 800, fontSize: 90 * k, color: ROXO, lineHeight: 1.1}}>{ano}</div> : null}
        </div>
      </div>
      {cena.rotulo ? <div style={{marginTop: 40 * k, fontFamily: FONTE, fontWeight: 800, fontSize: 48 * k, color: '#fff', background: 'rgba(124,92,255,.25)',
        border: `${3 * k}px solid ${ROXO}`, borderRadius: 18 * k, padding: `${10 * k}px ${28 * k}px`,
        opacity: interpolate(f, [18, 28], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{cena.rotulo}</div> : null}
    </AbsoluteFill>
  );
};

// ---------- comparativo (dois números lado a lado) ----------
const Comparativo = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const itens = (cena.itens || []).slice(0, 3);
  return (
    <AbsoluteFill style={{background: 'transparent', alignItems: 'center',
      justifyContent: vertical ? 'flex-start' : 'center', paddingTop: vertical ? '28%' : 0}}>
      <div style={{display: 'flex', gap: 34 * k, alignItems: 'flex-end'}}>
        {itens.map((it, i) => {
          const s = spring({frame: f - i * 10, fps, config: {damping: 12, stiffness: 140}});
          const alto = (vertical ? 360 : 220) * k * (1 + i * 0.35);
          return (
            <div key={i} style={{textAlign: 'center', transform: `translateY(${(1 - s) * 300}px)`, opacity: s}}>
              <div style={{width: (vertical ? 380 : 240) * k, height: alto, borderRadius: 34 * k, border: `${6 * k}px solid #fff`,
                background: i === itens.length - 1 ? `linear-gradient(160deg, ${ROXO}, #3b22b8)` : 'rgba(255,255,255,.08)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 30px 100px rgba(124,92,255,.35)'}}>
                <span style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 130 : 96) * k, color: '#fff', letterSpacing: -3 * k}}>{it.valor}</span>
              </div>
              <div style={{marginTop: 22 * k, fontFamily: FONTE, fontWeight: 800, fontSize: 52 * k, color: '#fff', textTransform: 'uppercase'}}>{it.rotulo}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Capitulo = ({cena, k}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 14}});
  const sai = interpolate(f, [40, 52], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (!cena.capitulo || cena.tipo === 'produto') return null;
  return (
    <div style={{position: 'absolute', left: 60 * k, top: 150 * k, opacity: sai, transform: `translateX(${(1 - s) * -400}px)`}}>
      <span style={{fontFamily: FONTE, fontWeight: 900, fontSize: 44 * k, color: '#fff', background: ROXO, padding: `${10 * k}px ${26 * k}px`,
        borderRadius: 14 * k, textTransform: 'uppercase'}}>{cena.capitulo}</span>
    </div>
  );
};

// ---------- manchete: print da notícia com marca-texto ----------
const Manchete = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const m = cena.manchete || {};
  const s = spring({frame: f, fps, config: {damping: 14, stiffness: 110}});
  const largura = (vertical ? 980 : 760) * k * (vertical ? 1 : 1.33);
  const altura = largura / (m.proporcao || 0.8);
  const janela = vertical ? 1180 * k : 520 * k * 1.33;
  const destaque = (m.destaque || [])[0];
  // começa no título e desce até o trecho destacado, com zoom
  const alvoY = destaque ? Math.max(0, destaque.y * altura - janela * 0.45) : 0;
  const desce = interpolate(f, [12, Math.max(30, cena.dur * 0.45)], [0, Math.min(alvoY, Math.max(0, altura - janela))], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const zoom = interpolate(f, [cena.dur * 0.4, cena.dur], [1, 1.12], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const marca = interpolate(f, [cena.dur * 0.42, cena.dur * 0.62], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: 'transparent', alignItems: 'center',
      justifyContent: vertical ? 'flex-start' : 'center', paddingTop: vertical ? 170 * k : 0}}>
      <div style={{width: largura, height: Math.min(janela, altura), overflow: 'hidden', borderRadius: 26 * k, background: '#fff',
        boxShadow: '0 40px 120px rgba(0,0,0,.7), 0 0 0 1px rgba(255,255,255,.15)',
        transform: `perspective(1600px) rotateX(${interpolate(s, [0, 1], [18, 0])}deg) translateY(${(1 - s) * 260}px) scale(${zoom})`, opacity: s}}>
        <div style={{position: 'relative', width: largura, height: altura, transform: `translateY(${-desce}px)`}}>
          <Img src={staticFile(m.src)} style={{width: largura, height: altura}} />
          {(m.destaque || []).map((r, i) => (
            <div key={i} style={{position: 'absolute', left: r.x * largura - 4, top: r.y * altura - 2, height: r.h * altura + 4,
              width: (r.w * largura + 8) * Math.min(1, Math.max(0, marca * (m.destaque.length) - i)),
              background: 'rgba(255, 214, 10, .55)', mixBlendMode: 'multiply', borderRadius: 4}} />
          ))}
        </div>
      </div>
      <div style={{marginTop: 26 * k, display: 'flex', alignItems: 'center', gap: 14 * k, opacity: s}}>
        <span style={{fontFamily: FONTE, fontWeight: 800, fontSize: 30 * k, color: '#fff', background: 'rgba(255,255,255,.1)',
          border: `${2 * k}px solid rgba(255,255,255,.25)`, borderRadius: 999, padding: `${8 * k}px ${22 * k}px`}}>Fonte: {m.site}</span>
      </div>
    </AbsoluteFill>
  );
};

// ---------- lista: itens que entram um a um ----------
const Lista = ({cena, k: k0, vertical}) => {
  const k = vertical ? k0 : k0 * 0.58;  // no 16:9 os itens ficam menores para caber na tela
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const itens = (cena.itens || []).slice(0, 5);
  const passo = cena.dur / Math.max(1, itens.length);
  const atual = Math.min(itens.length - 1, Math.floor(f / passo));
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center',
      padding: `0 ${60 * k}px ${vertical ? 420 * k : 60 * k}px`}}>
      {cena.titulo_lista ? <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: 84 * k, color: '#fff', textTransform: 'uppercase', marginBottom: 40 * k}}>{cena.titulo_lista}</div> : null}
      {itens.map((it, i) => {
        const e = spring({frame: f - i * passo, fps, config: {damping: 13, stiffness: 150}});
        const ativo = i === atual;
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', gap: 26 * k, marginBottom: 26 * k, opacity: e * (ativo ? 1 : 0.45),
            transform: `translateX(${(1 - e) * -500}px) scale(${ativo ? 1.04 : 1})`, transformOrigin: 'left center'}}>
            <span style={{minWidth: 140 * k, height: 140 * k, borderRadius: 34 * k, background: ativo ? ROXO : 'rgba(255,255,255,.08)',
              border: `${3 * k}px solid ${ativo ? ROXO2 : 'rgba(255,255,255,.2)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: FONTE, fontWeight: 900, fontSize: 80 * k, color: '#fff'}}>{i + 1}</span>
            <span style={{fontFamily: FONTE, fontWeight: 800, fontSize: 70 * k, color: '#fff', lineHeight: 1.1}}>{it}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- barras: compara números com barras que crescem ----------
const Barras = ({cena, k: k0, vertical}) => {
  const k = vertical ? k0 : k0 * 0.58;  // no 16:9 os itens ficam menores para caber na tela
  const f = useCurrentFrame();
  const itens = (cena.itens || []).slice(0, 4);
  const max = Math.max(...itens.map((i) => Number(i.valor) || 0), 1);
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center',
      padding: `0 ${70 * k}px ${vertical ? 420 * k : 60 * k}px`}}>
      {itens.map((it, i) => {
        const p = interpolate(f, [8 + i * 8, 34 + i * 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const v = (Number(it.valor) || 0) * p;
        return (
          <div key={i} style={{marginBottom: 60 * k}}>
            <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: FONTE, fontWeight: 800, fontSize: 64 * k, color: '#fff', marginBottom: 16 * k}}>
              <span>{it.rotulo}</span><span style={{color: i === 0 ? ROXO2 : '#fff'}}>{formatar(Math.round(v))}{it.unidade ? ' ' + it.unidade : ''}</span>
            </div>
            <div style={{height: 84 * k, borderRadius: 999, background: 'rgba(255,255,255,.08)', overflow: 'hidden'}}>
              <div style={{height: '100%', width: `${(Number(it.valor) || 0) / max * 100 * p}%`, borderRadius: 999,
                background: i === 0 ? `linear-gradient(90deg, ${ROXO}, ${ROSA})` : 'rgba(255,255,255,.45)'}} />
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- linha do tempo ----------
const Linha = ({cena, k: k0, vertical}) => {
  const k = vertical ? k0 : k0 * 0.58;  // no 16:9 os itens ficam menores para caber na tela
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const evs = (cena.itens || []).slice(0, 4);
  const passo = cena.dur / Math.max(1, evs.length);
  const prog = interpolate(f, [0, cena.dur * 0.9], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center', padding: `0 ${80 * k}px ${vertical ? 420 * k : 60 * k}px`}}>
      <div style={{position: 'relative', paddingLeft: 90 * k}}>
        <div style={{position: 'absolute', left: 22 * k, top: 10 * k, width: 8 * k, height: `${prog * 100}%`, background: `linear-gradient(${ROXO}, ${ROSA})`, borderRadius: 8}} />
        {evs.map((e, i) => {
          const s = spring({frame: f - i * passo, fps, config: {damping: 13}});
          return (
            <div key={i} style={{position: 'relative', marginBottom: 56 * k, opacity: s, transform: `translateY(${(1 - s) * 60}px)`}}>
              <div style={{position: 'absolute', left: -82 * k, top: 20 * k, width: 50 * k, height: 50 * k, borderRadius: '50%', background: ROXO, border: `${5 * k}px solid #fff`}} />
              <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: 84 * k, color: ROXO2}}>{e.data}</div>
              <div style={{fontFamily: FONTE, fontWeight: 700, fontSize: 60 * k, color: '#fff', lineHeight: 1.15}}>{e.texto}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- citação ----------
const Citacao = ({cena, k, vertical}) => {
  const f = useCurrentFrame();
  const texto = cena.tela || '';
  const n = Math.floor(interpolate(f, [6, Math.max(20, cena.dur * 0.6)], [0, texto.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <AbsoluteFill style={{background: 'transparent', justifyContent: 'center', padding: `0 ${80 * k}px`}}>
      <div style={{fontFamily: 'Georgia, serif', fontSize: 260 * k, color: ROXO, lineHeight: 0.6, height: 140 * k}}>“</div>
      <div style={{fontFamily: FONTE, fontWeight: 800, fontSize: (vertical ? 74 : 60) * k, color: '#fff', lineHeight: 1.15}}>{texto.slice(0, n)}<span style={{opacity: f % 16 < 8 ? 1 : 0, color: ROXO2}}>|</span></div>
      {cena.autor ? <div style={{marginTop: 34 * k, fontFamily: FONTE, fontWeight: 700, fontSize: 38 * k, color: ROXO2}}>— {cena.autor}</div> : null}
    </AbsoluteFill>
  );
};

// ---------- botão de inscrição animado ----------
export const Inscrever = ({k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const e = spring({frame: f, fps, config: {damping: 12, stiffness: 160}});
  const clicou = f > 34;
  const cx = interpolate(f, [10, 30], [260, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const cy = interpolate(f, [10, 30], [180, 10], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const aperto = f > 30 && f < 36 ? 0.92 : 1;
  const sino = f > 40 ? Math.sin((f - 40) * 0.9) * Math.max(0, 22 - (f - 40)) : 0;
  const sai = interpolate(f, [70, 80], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: vertical ? 'flex-end' : 'flex-end', alignItems: 'center', paddingBottom: (vertical ? 330 : 90) * k, opacity: sai, pointerEvents: 'none'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 18 * k, transform: `translateY(${(1 - e) * 200}px) scale(${e * aperto})`,
        background: 'rgba(15,15,20,.92)', border: `${2 * k}px solid rgba(255,255,255,.18)`, borderRadius: 999, padding: `${14 * k}px ${18 * k}px ${14 * k}px ${14 * k}px`,
        boxShadow: '0 20px 60px rgba(0,0,0,.6)', position: 'relative'}}>
        <Simbolo s={74 * k} />
        <span style={{fontFamily: FONTE, fontWeight: 800, fontSize: 36 * k, color: '#fff', marginRight: 8 * k}}>Nexus Tech IA</span>
        <span style={{fontFamily: FONTE, fontWeight: 900, fontSize: 34 * k, color: clicou ? '#ddd' : '#fff', background: clicou ? '#3a3a44' : '#ff0033',
          borderRadius: 999, padding: `${14 * k}px ${30 * k}px`, textTransform: 'uppercase'}}>{clicou ? 'Inscrito' : 'Inscrever-se'}</span>
        <svg width={56 * k} height={56 * k} viewBox="0 0 24 24" style={{transform: `rotate(${sino}deg)`, transformOrigin: '50% 10%'}}>
          <path d="M12 22a2.5 2.5 0 0 0 2.5-2.5h-5A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5-6.7V3.5a2 2 0 0 0-4 0v.8A7 7 0 0 0 5 11v5l-2 2v1h18v-1l-2-2z" fill={clicou ? '#ffd60a' : '#fff'} />
        </svg>
        <svg width={64 * k} height={64 * k} viewBox="0 0 24 24" style={{position: 'absolute', right: 150 * k - cx * k, top: 40 * k + cy * k, opacity: f < 60 ? 1 : 0}}>
          <path d="M5 3l14 8-6 1.5 3.5 7-2.5 1.2-3.5-7L5 18z" fill="#fff" stroke="#000" strokeWidth="1.2" />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ---------- fotos em tela dividida ----------
const Dividida = ({cena, vertical}) => {
  const f = useCurrentFrame();
  const imgs = (cena.imagens || []).slice(0, 2);
  const abre = interpolate(f, [0, 14], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: FUNDO, flexDirection: vertical ? 'column' : 'row', gap: 10}}>
      {imgs.map((img, i) => (
        <div key={i} style={{flex: 1, overflow: 'hidden', position: 'relative',
          transform: vertical ? `translateX(${(1 - abre) * (i ? 100 : -100)}%)` : `translateY(${(1 - abre) * (i ? 100 : -100)}%)`}}>
          <Img src={staticFile(img.src)} style={{width: '100%', height: '100%', objectFit: img.produto ? 'contain' : 'cover', background: img.produto ? '#eef0f4' : FUNDO,
            transform: `scale(${interpolate(f, [0, cena.dur], [1.05, 1.18])})`}} />
        </div>
      ))}
    </AbsoluteFill>
  );
};

// entradas variadas (cada cena entra de um jeito)
const ENTRADAS = ['zoom', 'slide', 'subida', 'glitch', 'cortina', 'giro', 'desfoque'];
const entrada = (tipo, f, fps) => {
  const s = spring({frame: f, fps, config: {damping: 16, stiffness: 190}});
  switch (tipo) {
    case 'slide': return {transform: `translateX(${(1 - s) * 100}%)`};
    case 'subida': return {transform: `translateY(${(1 - s) * 100}%)`};
    case 'giro': return {transform: `rotate(${(1 - s) * -8}deg) scale(${interpolate(s, [0, 1], [1.3, 1])})`};
    case 'desfoque': return {filter: `blur(${(1 - s) * 30}px)`, transform: `scale(${interpolate(s, [0, 1], [1.08, 1])})`};
    case 'cortina': return {clipPath: `inset(0 ${(1 - s) * 100}% 0 0)`};
    case 'glitch': return {transform: `translateX(${f < 8 ? (f % 2 ? 24 : -24) : 0}px)`, filter: f < 8 ? `hue-rotate(${f * 40}deg) saturate(2)` : 'none'};
    default: return {transform: `scale(${interpolate(s, [0, 1], [1.12, 1])})`};
  }
};

// ---------- fundo das cenas gráficas: a foto do assunto desfocada ----------
const FundoGrafico = ({cena}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: FUNDO}}>
      {cena.fundo ? <Img src={staticFile(cena.fundo)} style={{width: '100%', height: '100%', objectFit: 'cover',
        filter: 'blur(26px) brightness(.38) saturate(1.3)', transform: `scale(${1.25 + f / 900}) translateX(${Math.sin(f / 60) * 2}%)`}} /> : null}
      <AbsoluteFill style={{background: cena.fundo ? 'radial-gradient(circle at 50% 40%, rgba(124,92,255,.22) 0%, rgba(5,5,7,.55) 70%)' : 'radial-gradient(circle at 50% 30%, #241b4f 0%, #07070b 70%)'}} />
    </AbsoluteFill>
  );
};

// ---------- cena ----------
// ---------- vinheta do quadro (2,5 s, sempre depois do gancho) ----------
const Vinheta = ({titulo, k, vertical}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 12, stiffness: 140}});
  const sai = interpolate(f, [62, 75], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const linha = interpolate(f, [8, 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 50% 50%, #2a1f66 0%, ${FUNDO} 65%)`, opacity: sai,
      justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 30 * k}}>
      <div style={{transform: `scale(${s}) rotate(${interpolate(s, [0, 1], [-90, 0])}deg)`}}><Simbolo s={170 * k} /></div>
      <div style={{fontFamily: FONTE, fontWeight: 900, fontSize: (vertical ? 96 : 110) * k, color: '#fff', letterSpacing: -2 * k,
        textTransform: 'uppercase', opacity: s, transform: `translateY(${(1 - s) * 60}px)`}}>{titulo}</div>
      <div style={{width: 520 * k * linha, height: 8 * k, borderRadius: 8 * k, background: ROXO, boxShadow: `0 0 40px ${ROXO}`}} />
    </AbsoluteFill>
  );
};

// ---------- fonte da informação: barra discreta no rodapé ----------
const Rodape = ({texto, k, vertical}) => {
  const f = useCurrentFrame();
  const op = interpolate(f, [6, 16], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 40 * k, bottom: vertical ? undefined : 22 * k, top: vertical ? 150 * k : undefined, opacity: op * 0.9,
      fontFamily: FONTE, fontWeight: 600, fontSize: (vertical ? 30 : 24) * k, color: 'rgba(255,255,255,.85)',
      background: 'rgba(5,5,7,.6)', borderLeft: `${4 * k}px solid ${ROXO}`, padding: `${6 * k}px ${14 * k}px`, borderRadius: 6 * k}}>
      Fonte: {texto}
    </div>
  );
};

const Cena = ({cena, k, vertical, primeira}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const flash = primeira || cena.entrada === 'cortina' ? 0 : interpolate(f, [0, 5], [0.35, 0], {extrapolateRight: 'clamp'});
  const treme = cena.tipo === 'gancho' && f < 12 ? Math.sin(f * 2.2) * (12 - f) * 0.9 : 0;
  const escuro = cena.tipo === 'numero' || cena.tipo === 'gancho' ? 0.5 : 0.35;
  const grafica = ['produto', 'info', 'data', 'comparativo', 'manchete', 'lista', 'barras', 'linha', 'citacao'].includes(cena.tipo);
  const est = primeira ? {} : entrada(cena.entrada || 'zoom', f, fps);
  const T = {produto: Produto, info: Info, data: Data, comparativo: Comparativo, manchete: Manchete, lista: Lista, barras: Barras, linha: Linha, citacao: Citacao};
  const Comp = T[cena.tipo];
  return (
    <AbsoluteFill style={{...est, transform: `${est.transform || ''} translateX(${treme}px)`}}>
      {Comp && cena.tipo !== 'produto' ? <FundoGrafico cena={cena} /> : null}
      {Comp ? <Comp cena={cena} k={k} vertical={vertical} /> : cena.layout === 'dividida' && (cena.imagens || []).length >= 2 ? <Dividida cena={cena} vertical={vertical} /> : <Fundo cena={cena} vertical={vertical} />}
      {!grafica || cena.tipo === 'produto' ? <AbsoluteFill style={{background: vertical ? `linear-gradient(180deg, rgba(5,5,7,.75) 0%, rgba(5,5,7,0) 20%, rgba(5,5,7,${escuro}) 42%, rgba(5,5,7,.78) 56%, rgba(5,5,7,.8) 72%, rgba(5,5,7,.95) 100%)` : `linear-gradient(180deg, rgba(5,5,7,.7) 0%, rgba(5,5,7,0) 22%, rgba(5,5,7,${escuro}) 55%, rgba(5,5,7,.92) 100%)`}} /> : null}
      {cena.tipo === 'gancho' ? <Gancho cena={cena} k={k} vertical={vertical} /> : null}
      {cena.tipo === 'numero' ? <Numero cena={cena} k={k} vertical={vertical} /> : null}
      {cena.tipo === 'cta' ? <Chamada cena={cena} k={k} vertical={vertical} /> : null}
      <Capitulo cena={cena} k={k} />
      {cena.fonte && cena.tipo !== 'manchete' ? <Rodape texto={cena.fonte} k={k} vertical={vertical} /> : null}
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

export const Video = (props) => {
  const {cenas, selo, audio, largura, altura, sons} = props;
  const frame = useCurrentFrame();
  const vertical = altura > largura;
  const k = vertical ? largura / 1080 : largura / 1280 * 0.75;
  const palavras = cenas.flatMap((c) => c.palavras || []);
  return (
    <AbsoluteFill style={{background: FUNDO}}>
      <style>{fontes}</style>
      {cenas.map((c, i) => (
        <Sequence key={i} from={c.ini} durationInFrames={c.dur + (i < cenas.length - 1 ? 0 : 30)}>
          <Cena cena={{...c, n: i}} k={k} vertical={vertical} primeira={i === 0} />
        </Sequence>
      ))}
      {/* legenda palavra por palavra (fica por cima das cenas) */}
      {cenas.map((c, i) => ['fato', 'produto', 'info', 'data', 'comparativo', 'manchete', 'barras'].includes(c.tipo) && (c.palavras || []).length ? (
        <Sequence key={'l' + i} from={c.ini} durationInFrames={c.dur}>
          <Legenda palavras={c.palavras} base={c.ini} k={k} vertical={vertical} modo={props.legenda} baixo={['produto', 'info', 'data', 'comparativo', 'manchete', 'barras'].includes(c.tipo)} />
        </Sequence>
      ) : null)}
      {(props.inscrever || []).map((q, i) => (
        <Sequence key={'i' + i} from={q.ini} durationInFrames={82}>
          <Inscrever k={k} vertical={vertical} />
        </Sequence>
      ))}
      {props.vinheta ? (
        <Sequence from={props.vinheta.ini} durationInFrames={props.vinheta.dur}>
          <Vinheta titulo={props.vinheta.titulo} k={k} vertical={vertical} />
        </Sequence>
      ) : null}
      <Topo selo={selo} k={k} cenas={cenas} frame={frame} />
      {audio ? <Audio src={staticFile(audio)} /> : null}
      {(sons || []).map((s, i) => (
        <Sequence key={'s' + i} from={s.ini} durationInFrames={30}>
          <Audio src={staticFile(s.src)} volume={s.vol ?? 0.25} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
