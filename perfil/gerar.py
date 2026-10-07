"""Gera o perfil a partir de perfil/projetos.json.

    python perfil/gerar.py

Saídas:
  perfil/svg/*.svg        topo, números, mapa e árvore (animados, tema claro e escuro, PT e EN)
  PROJETOS.md             a árvore completa, com o propósito e a situação de cada projeto
  README.md / README-en.md  montados a partir de perfil/README.pt.md e perfil/README.en.md

Para atualizar o perfil: edite perfil/projetos.json (situação, propósito, destaque...) e rode o script —
ou só faça o commit: a Action .github/workflows/perfil.yml roda ele sozinha.
"""
import html, json, math, os, re
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERFIL = os.path.join(RAIZ, "perfil")
SVG = os.path.join(PERFIL, "svg")
RAW = "https://raw.githubusercontent.com/Davicjc/{}/main/{}"
os.makedirs(SVG, exist_ok=True)

DADOS = json.load(open(os.path.join(PERFIL, "projetos.json"), encoding="utf-8"))
P = DADOS["projetos"]

TEMAS = {
    "escuro": dict(bg="#0d1117", painel="#161b22", linha="#30363d", texto="#e6edf3", fraco="#8b949e",
                   acento="#58a6ff", pacote="#3fb950", grade="#21262d"),
    "claro": dict(bg="#ffffff", painel="#f6f8fa", linha="#d0d7de", texto="#1f2328", fraco="#59636e",
                  acento="#0969da", pacote="#1a7f37", grade="#eaeef2"),
}
SITUACAO = {  # chave: (cor, PT, EN)
    "no_ar": ("#3fb950", "No ar", "Live"),
    "manutencao": ("#58a6ff", "Recebe atualizações", "Maintained"),
    "entregue": ("#8b949e", "Entregue", "Delivered"),
    "desenvolvimento": ("#d29922", "Em desenvolvimento", "In development"),
    "aguardando": ("#a371f7", "Aguardando o cliente", "Awaiting client"),
    "recusado": ("#f85149", "Proposta recusada", "Proposal declined"),
    "prototipo": ("#db61a2", "Protótipo", "Prototype"),
    "pausado": ("#6e7681", "Pausado", "Paused"),
    "abandonado": ("#6e7681", "Abandonado", "Abandoned"),
    "historico": ("#6e7681", "Histórico", "Archive"),
    "": ("#8b949e", "A confirmar", "To be confirmed"),
}
EMOJI = {"no_ar": "✅", "manutencao": "🔄", "entregue": "📦", "desenvolvimento": "🛠️", "aguardando": "👀",
         "recusado": "❌", "prototipo": "🧪", "pausado": "⏸️", "abandonado": "🛑", "historico": "🗄️", "": "❔"}
ORIGEM = {  # chave: (PT, EN, ordem)
    "cliente": ("Para clientes", "For clients", 0),
    "empresa": ("Para a empresa (Audicom)", "For my company (Audicom)", 1),
    "proposta": ("Propostas", "Proposals", 2),
    "pessoal": ("Projetos pessoais", "Personal projects", 3),
    "estudo": ("Faculdade e estudo", "College & study", 4),
}
FONTE = "ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'Cascadia Code',Consolas,monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def gravar(nome, conteudo):
    open(os.path.join(SVG, nome), "w", encoding="utf-8", newline="\n").write(conteudo)


def aparecer(atraso, dur=0.6, total=None):
    """Sem animação de entrada: o primeiro quadro precisa estar completo (prévias e apps não animam)."""
    return ""
    total = total or atraso + dur
    k = round(atraso / total, 4)
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k};1" dur="{total:.2f}s" fill="freeze"/>')


def desenhar_traco(comp, atraso, dur=0.7):
    return ""  # linhas sempre visíveis; o movimento fica com os pacotes
    total = atraso + dur
    k = round(atraso / total, 4)
    return (f'stroke-dasharray="{comp:.0f}" '
            f'><animate attributeName="stroke-dashoffset" values="{comp:.0f};{comp:.0f};0" keyTimes="0;{k};1" '
            f'dur="{total:.2f}s" fill="freeze"/')


# ------------------------------------------------------------------ topo: topologia de rede animada
def topo(tema, idioma):
    c = TEMAS[tema]
    W, H = 1200, 340
    papel = {"pt": ("Desenvolvedor full stack · Infraestrutura de redes", "Uberlândia · MG · Brasil",
                    ["construo sistemas para operações de campo", "monitoro a rede de um provedor de internet",
                     "entrego sites que trazem clientes", "automatizo o trabalho repetitivo com IA"]),
             "en": ("Full-stack developer · Network infrastructure", "Uberlândia · MG · Brazil",
                    ["I build systems for field operations", "I monitor an internet provider's network",
                     "I ship websites that bring in clients", "I automate repetitive work with AI"])}[idioma]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Davi Castro — {esc(papel[0])}">',
         f'<defs><pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{c["grade"]}"/></pattern>'
         f'<radialGradient id="brilho"><stop offset="0" stop-color="{c["pacote"]}" stop-opacity=".9"/>'
         f'<stop offset="1" stop-color="{c["pacote"]}" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{c["bg"]}"/><stop offset=".55" stop-color="{c["bg"]}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="16" fill="{c["bg"]}"/>',
         f'<rect width="{W}" height="{H}" rx="16" fill="url(#g)"/>',
         f'<rect width="{W}" height="{H}" rx="16" fill="url(#fade)"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{c["linha"]}"/>']
    # texto
    s.append(f'<g font-family="{FONTE}">'
             f'<text x="56" y="86" font-family="{MONO}" font-size="15" fill="{c["fraco"]}">~/davicjc<tspan fill="{c["pacote"]}"> ●</tspan>'
             f'<tspan fill="{c["fraco"]}"> online</tspan>{aparecer(0.1)}</text>'
             f'<text x="52" y="160" font-size="66" font-weight="700" fill="{c["texto"]}" letter-spacing="-1.5">Davi Castro{aparecer(0.2)}</text>'
             f'<text x="56" y="200" font-size="21" fill="{c["texto"]}" opacity=".88">{esc(papel[0])}{aparecer(0.45)}</text>'
             f'<text x="56" y="232" font-size="15" fill="{c["fraco"]}">{esc(papel[1])}{aparecer(0.6)}</text>')
    # frase que alterna (cada uma 3,5 s)
    n, d = len(papel[2]), 3.5
    for i, f in enumerate(papel[2]):
        ini, fim = i / n, (i + 1) / n
        k = f"0;{ini + 0.001:.4f};{ini + 0.03:.4f};{fim - 0.03:.4f};{fim:.4f};1"
        k = ";".join(sorted(set(k.split(";")), key=float)) if i == 0 or i == n - 1 else k
        vals = "0;0;1;1;0;0"
        if i == 0:
            k, vals = f"0;{fim - 0.03:.4f};{fim:.4f};1", "1;1;0;0"
        elif i == n - 1:
            k, vals = f"0;{ini:.4f};{ini + 0.03:.4f};1", "0;0;1;1"
        s.append(f'<text x="56" y="282" font-family="{MONO}" font-size="17" fill="{c["acento"]}" opacity="{1 if i == 0 else 0}">'
                 f'<tspan fill="{c["fraco"]}">$ </tspan>{esc(f)}'
                 f'<animate attributeName="opacity" values="{vals}" keyTimes="{k}" dur="{n * d}s" repeatCount="indefinite"/></text>')
    s.append("</g>")
    # topologia
    cx, cy = 930, 172
    nos = [("web", 790, 78), ("sistemas" if idioma == "pt" else "systems", 1075, 78), ("redes" if idioma == "pt" else "networks", 760, 228),
           ("IA" if idioma == "pt" else "AI", 1100, 236), ("clientes" if idioma == "pt" else "clients", 930, 304), ("dados" if idioma == "pt" else "data", 930, 44)]
    anel = [0, 5, 1, 3, 4, 2, 0]
    for a, b in zip(anel, anel[1:]):
        (_, x1, y1), (_, x2, y2) = nos[a], nos[b]
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["linha"]}" stroke-width="1" stroke-dasharray="3 5" opacity=".8"/>')
    for i, (rot, x, y) in enumerate(nos):
        comp = math.hypot(x - cx, y - cy)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{c["acento"]}" stroke-width="1.6" opacity=".55" '
                 f'{desenhar_traco(comp, 0.3 + i * 0.12)}></line>')
    for i, (rot, x, y) in enumerate(nos):  # pacotes indo e voltando
        ida, dur = f"M{cx},{cy} L{x},{y}", 2.2 + (i % 3) * 0.5
        for j, caminho in enumerate((ida, f"M{x},{y} L{cx},{cy}")):
            atraso = round(1.2 + i * 0.37 + j * dur / 2, 2)
            s.append(f'<g opacity="0"><circle r="9" fill="url(#brilho)"/><circle r="3" fill="{c["pacote"]}"/>'
                     f'<animateMotion path="{caminho}" dur="{dur}s" begin="{atraso}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="{dur}s" begin="{atraso}s" repeatCount="indefinite"/></g>')
    for i, (rot, x, y) in enumerate(nos):
        s.append(f'<g font-family="{MONO}">'
                 f'<circle cx="{x}" cy="{y}" r="7" fill="{c["painel"]}" stroke="{c["acento"]}" stroke-width="2">'
                 f'<animate attributeName="r" values="6;8;6" dur="3s" begin="{i * 0.4}s" repeatCount="indefinite"/></circle>'
                 f'<text x="{x}" y="{y + (-16 if y < cy else 26)}" text-anchor="middle" font-size="13" fill="{c["fraco"]}">{esc(rot)}</text>'
                 f'{aparecer(0.5 + i * 0.1)}</g>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{c["painel"]}" stroke="{c["acento"]}" stroke-width="2"/>'
             f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{c["acento"]}" stroke-width="2">'
             f'<animate attributeName="r" values="40;58" dur="2.6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".6;0" dur="2.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="600" fill="{c["texto"]}">davicjc</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ números
def numeros(tema, idioma):
    c = TEMAS[tema]
    para_outros = sum(1 for p in P if p["origem"] in ("cliente", "empresa", "proposta"))
    no_ar = sum(1 for p in P if p["site"])
    techs = len({t for p in P for t in p["stack"]})
    desde = min(int(p["ano"]) for p in P if str(p["ano"]).isdigit())
    itens = {"pt": [(len(P), "projetos"), (para_outros, "para clientes e empresa"), (no_ar, "com site no ar"),
                    (techs, "tecnologias"), (desde, "programando desde")],
             "en": [(len(P), "projects"), (para_outros, "for clients & company"), (no_ar, "with a live site"),
                    (techs, "technologies"), (desde, "coding since")]}[idioma]
    W, H, n = 1200, 132, len(itens)
    larg = (W - 16 * (n - 1)) / n
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONTE}" role="img" '
         f'aria-label="{esc(", ".join(f"{v} {t}" for v, t in itens))}">']
    for i, (v, t) in enumerate(itens):
        x = i * (larg + 16)
        s.append(f'<g>{aparecer(0.15 * i, 0.5)}'
                 f'<rect x="{x + .5:.1f}" y=".5" width="{larg - 1:.1f}" height="{H - 1}" rx="12" fill="{c["painel"]}" stroke="{c["linha"]}"/>'
                 f'<rect x="{x + 20:.1f}" y="22" width="26" height="3" rx="1.5" fill="{c["acento"]}"/>'
                 f'<text x="{x + 20:.1f}" y="80" font-size="44" font-weight="700" fill="{c["texto"]}" letter-spacing="-1">{v}</text>'
                 f'<text x="{x + 20:.1f}" y="108" font-size="15" fill="{c["fraco"]}">{esc(t)}</text></g>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ grupos (origem) usados no mapa e na árvore
def grupos():
    g = {}
    for p in P:
        g.setdefault(p["origem"], []).append(p)
    return sorted(g.items(), key=lambda kv: ORIGEM.get(kv[0], ("", "", 9))[2])


def cadeado(x, y, cor):
    return (f'<g transform="translate({x},{y})" fill="none" stroke="{cor}" stroke-width="1.4">'
            f'<rect x="0" y="5" width="9" height="7" rx="1.5" fill="{cor}" stroke="none"/><path d="M2 5V3.2a2.5 2.5 0 0 1 5 0V5"/></g>')


# ------------------------------------------------------------------ mapa compacto (README)
def mapa(tema, idioma):
    c = TEMAS[tema]
    gs = grupos()
    W, lin = 1200, 74
    H = 40 + len(gs) * lin
    rx, ry = 70, H / 2
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONTE}" role="img" '
         f'aria-label="{"Mapa dos projetos" if idioma == "pt" else "Project map"}">']
    for i, (org, ps) in enumerate(gs):
        y = 20 + i * lin + lin / 2
        cam = f"M{rx + 34},{ry} C{rx + 150},{ry} {250},{y} {330},{y}"
        s.append(f'<path d="{cam}" fill="none" stroke="{c["acento"]}" stroke-width="1.6" opacity=".6" {desenhar_traco(900, 0.2 + i * 0.15)}></path>')
        s.append(f'<g opacity="0"><circle r="3.2" fill="{c["pacote"]}"/><animateMotion path="{cam}" dur="2.4s" begin="{1.5 + i * 0.6}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="2.4s" begin="{1.5 + i * 0.6}s" repeatCount="indefinite"/></g>')
        nome = ORIGEM.get(org, (org, org, 9))[0 if idioma == "pt" else 1]
        privados = sum(1 for p in ps if p["privado"])
        s.append(f'<g>{aparecer(0.4 + i * 0.15)}'
                 f'<rect x="330" y="{y - 22}" width="300" height="44" rx="22" fill="{c["painel"]}" stroke="{c["linha"]}"/>'
                 f'<text x="352" y="{y + 6}" font-size="17" font-weight="600" fill="{c["texto"]}">{esc(nome)}</text>'
                 f'<text x="612" y="{y + 6}" text-anchor="end" font-size="17" font-weight="700" fill="{c["acento"]}">{len(ps)}</text></g>')
        # barra de situação
        x0, larg = 660, 300
        cont = {}
        for p in ps:
            cont[p["situacao"]] = cont.get(p["situacao"], 0) + 1
        x = x0
        s.append(f'<g>{aparecer(0.6 + i * 0.15)}')
        for k in SITUACAO:
            if k in cont:
                w = larg * cont[k] / len(ps)
                s.append(f'<rect x="{x:.1f}" y="{y - 6}" width="{max(w - 2, 2):.1f}" height="12" rx="3" fill="{SITUACAO[k][0]}" '
                         f'opacity="{.35 if k == "" else .95}"/>')
                x += w
        pub = len(ps) - privados
        txt = f"{privados} privados · {pub} públicos" if idioma == "pt" else f"{privados} private · {pub} public"
        s.append(f'<text x="{x0 + larg + 18}" y="{y + 5}" font-size="14" fill="{c["fraco"]}">{esc(txt)}</text></g>')
    # raiz
    s.append(f'<circle cx="{rx}" cy="{ry}" r="34" fill="{c["painel"]}" stroke="{c["acento"]}" stroke-width="2"/>'
             f'<circle cx="{rx}" cy="{ry}" r="34" fill="none" stroke="{c["acento"]}" stroke-width="2">'
             f'<animate attributeName="r" values="34;50" dur="2.6s" repeatCount="indefinite"/><animate attributeName="opacity" values=".5;0" dur="2.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{rx}" y="{ry + 5}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="600" fill="{c["texto"]}">davicjc</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ árvore completa (PROJETOS.md)
def arvore(tema, idioma):
    c = TEMAS[tema]
    gs = grupos()
    W, lin, gap, topo_y = 1200, 30, 26, 70
    H = topo_y + sum(len(ps) * lin for _, ps in gs) + gap * (len(gs) - 1) + 30
    rx, ry = 66, topo_y + (H - topo_y) / 2 - 10
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONTE}" role="img" '
         f'aria-label="{"Árvore de projetos" if idioma == "pt" else "Project tree"}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{c["bg"]}"/><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{c["linha"]}"/>']
    # legenda
    x = 30
    for k, (cor, pt, en) in SITUACAO.items():
        rot = pt if idioma == "pt" else en
        if k in ("abandonado", "historico"):
            continue
        s.append(f'<circle cx="{x + 5}" cy="34" r="5" fill="{cor}" opacity="{.4 if k == "" else 1}"/>'
                 f'<text x="{x + 15}" y="39" font-size="13" fill="{c["fraco"]}">{esc(rot)}</text>')
        x += 30 + len(rot) * 6.6
    s.append(cadeado(x + 4, 27, c["fraco"]) + f'<text x="{x + 20}" y="39" font-size="13" fill="{c["fraco"]}">{"privado" if idioma == "pt" else "private"}</text>')
    y = topo_y
    atraso = 0.2
    for gi, (org, ps) in enumerate(gs):
        gy = y + len(ps) * lin / 2
        gx = 300
        cam = f"M{rx + 32},{ry} C{rx + 130},{ry} {gx - 130},{gy} {gx},{gy}"
        s.append(f'<path d="{cam}" fill="none" stroke="{c["acento"]}" stroke-width="1.8" opacity=".55" {desenhar_traco(1800, atraso, 1.0)}></path>')
        nome = ORIGEM.get(org, (org, org, 9))[0 if idioma == "pt" else 1]
        s.append(f'<g>{aparecer(atraso + 0.3)}<rect x="{gx}" y="{gy - 17}" width="230" height="34" rx="17" fill="{c["painel"]}" stroke="{c["linha"]}"/>'
                 f'<text x="{gx + 16}" y="{gy + 5}" font-size="14.5" font-weight="600" fill="{c["texto"]}">{esc(nome)}</text>'
                 f'<text x="{gx + 214}" y="{gy + 5}" text-anchor="end" font-size="14.5" font-weight="700" fill="{c["acento"]}">{len(ps)}</text></g>')
        for i, p in enumerate(ps):
            ly = y + i * lin + lin / 2
            folha = f"M{gx + 230},{gy} C{gx + 290},{gy} {560},{ly} {600},{ly}"
            a = atraso + 0.5 + i * 0.05
            s.append(f'<path d="{folha}" fill="none" stroke="{c["linha"]}" stroke-width="1.2" {desenhar_traco(900, a, 0.6)}></path>')
            cor = SITUACAO.get(p["situacao"], SITUACAO[""])[0]
            rot_sit = SITUACAO.get(p["situacao"], SITUACAO[""])[1 if idioma == "pt" else 2]
            prop = p["proposito"] if len(p["proposito"]) <= 50 else p["proposito"][:48].rstrip(" ,.;:—-") + "…"
            s.append(f'<g>{aparecer(a + 0.3, 0.4)}<circle cx="608" cy="{ly}" r="6" fill="{cor}" opacity="{.4 if not p["situacao"] else 1}"/>'
                     + (cadeado(624, ly - 7, c["fraco"]) if p["privado"] else "")
                     + f'<text x="{642 if p["privado"] else 624}" y="{ly + 5}" font-size="14" font-weight="600" fill="{c["texto"]}">{esc(p["titulo"][:30])}</text>'
                     + f'<text x="880" y="{ly + 5}" font-size="12.5" fill="{c["fraco"]}">{esc(prop)}</text>'
                     f'<title>{esc(p["titulo"])} — {esc(rot_sit)}</title></g>')
        y += len(ps) * lin + gap
        atraso += 0.35
    s.append(f'<circle cx="{rx}" cy="{ry}" r="32" fill="{c["painel"]}" stroke="{c["acento"]}" stroke-width="2"/>'
             f'<circle cx="{rx}" cy="{ry}" r="32" fill="none" stroke="{c["acento"]}" stroke-width="2"><animate attributeName="r" values="32;48" dur="2.6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".5;0" dur="2.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{rx}" y="{ry + 5}" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="600" fill="{c["texto"]}">davicjc</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ markdown
def imagem_tema(base, alt, larg="100%"):
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="perfil/svg/{base}-escuro.svg">\n'
            f'  <img src="perfil/svg/{base}-claro.svg" alt="{esc(alt)}" width="{larg}">\n</picture>')


def cartao(p, idioma):
    if p["privado"]:
        arq = os.path.join(RAIZ, "imagens", "projetos", p["repo"] + ".jpg")
        img = f"imagens/projetos/{p['repo']}.jpg" if os.path.exists(arq) else None
    else:
        img = p["imagem"]
    link = p["site"] or (None if p["privado"] else f"https://github.com/Davicjc/{p['repo']}")
    sit = p["situacao"]
    selo = f'{EMOJI[sit]} {SITUACAO[sit][1 if idioma == "pt" else 2]}'
    tag = ("🔒 Privado" if idioma == "pt" else "🔒 Private") if p["privado"] else ""
    texto = (p.get("proposito_en") or p["proposito"]) if idioma == "en" else p["proposito"]
    figura = f'<img src="{img}" alt="{esc(p["titulo"])}">' if img else ""
    if link and figura:
        figura = f'<a href="{link}">{figura}</a>'
    titulo = f'<b>{esc(p["titulo"])}</b>'
    if link:
        titulo = f'<a href="{link}">{titulo}</a>'
    extra = f" · <code>{tag}</code>" if tag else ""
    linha_selo = f"{selo}{extra}" if sit else extra.lstrip(" ·")
    linha_selo = f"      <sub>{linha_selo}</sub><br>\n" if linha_selo else ""
    return (f'    <td width="50%" valign="top">\n      {figura}{"<br>" if figura else ""}\n      {titulo}<br>\n'
            f'{linha_selo}      <sub>{esc(texto)}</sub>\n    </td>')


def grade(lista, idioma):
    linhas = ["<table>"]
    for i in range(0, len(lista), 2):
        par = lista[i:i + 2]
        linhas.append("  <tr>\n" + "\n".join(cartao(p, idioma) for p in par) + ("\n    <td width=\"50%\"></td>" if len(par) == 1 else "") + "\n  </tr>")
    linhas.append("</table>")
    return "\n".join(linhas)


def bloco_destaques(idioma):
    proprios = [p for p in P if p["perfil"] == "destaque" and p["origem"] in ("pessoal", "estudo")]
    outros = [p for p in P if p["perfil"] == "destaque" and p["origem"] not in ("pessoal", "estudo")]
    t = {"pt": ("### 🧪 Projetos próprios", "### 🤝 Feitos para clientes e empresa"),
         "en": ("### 🧪 My own projects", "### 🤝 Built for clients & company")}[idioma]
    return f"{t[0]}\n\n{grade(proprios, idioma)}\n\n{t[1]}\n\n{grade(outros, idioma)}"


def projetos_md():
    linhas = ["<!-- Gerado por perfil/gerar.py a partir de perfil/projetos.json — edite o JSON, não este arquivo. -->",
              "", '<p align="center">', "  " + imagem_tema("arvore", "Árvore de projetos do Davi Castro").replace("\n", "\n  "), "</p>", "",
              "# 🌳 Árvore de projetos", "",
              "Todos os meus projetos num só lugar: **para quem foi feito**, **para que serve** e **em que pé está**. "
              "Os privados (🔒) aparecem com nome e propósito, mas o código continua fechado.", "",
              f"*Atualizado em {date.today().strftime('%d/%m/%Y')} · {len(P)} projetos · "
              f"{sum(1 for p in P if p['privado'])} privados · {sum(1 for p in P if not p['privado'])} públicos*", "",
              "## Legenda", "", "| Situação | Significa |", "|---|---|"]
    sig = {"no_ar": "entregue e funcionando, em uso", "manutencao": "entregue e ainda recebe melhorias",
           "entregue": "entregue, sem atualizações previstas", "desenvolvimento": "sendo construído agora",
           "aguardando": "pronto ou quase, esperando o cliente ver/aprovar", "recusado": "feito como proposta e não aprovado",
           "prototipo": "teste ou prova de conceito", "pausado": "parado por enquanto", "abandonado": "não vai continuar",
           "historico": "antigo, mantido só como registro", "": "ainda não classificado"}
    for k, (_, pt, _) in SITUACAO.items():
        linhas.append(f"| {EMOJI[k]} **{pt}** | {sig[k]} |")
    linhas += ["", "## Índice", ""]
    for org, ps in grupos():
        nome = ORIGEM.get(org, (org, org))[0]
        linhas.append(f"- [{nome}](#{re.sub(r'[^a-z0-9à-ú -]', '', nome.lower()).strip().replace(' ', '-')}) — {len(ps)}")
    for org, ps in grupos():
        nome = ORIGEM.get(org, (org, org))[0]
        linhas += ["", f"## {nome}", "", "| | Projeto | Para que serve | Situação | Ano | Links |", "|---|---|---|---|---|---|"]
        for p in ps:
            links = []
            if p["site"]:
                links.append(f"[site]({p['site']})")
            if not p["privado"]:
                links.append(f"[código](https://github.com/Davicjc/{p['repo']})")
            quem = f"<br><sub>{esc(p['cliente'])}</sub>" if p["cliente"] else ""
            stack = f"<br><sub>{esc(' · '.join(p['stack'][:4]))}</sub>" if p["stack"] else ""
            sit = f"{EMOJI[p['situacao']]} {SITUACAO[p['situacao']][1]}" if p["situacao"] else "—"
            linhas.append(f"| {'🔒' if p['privado'] else '🌐'} | **{esc(p['titulo'])}**{quem} | {esc(p['proposito'])}{stack} | "
                          f"{sit} | {p['ano']} | {' · '.join(links) or '—'} |")
    linhas += ["", "---", "", "**Como atualizar:** edite [`perfil/projetos.json`](perfil/projetos.json) (campo `situacao`, `proposito`, "
               "`perfil` = `destaque` / `lista` / `ocultar`) e faça o commit — a Action regenera esta página, a árvore e o README.", ""]
    return "\n".join(linhas)


def montar_readme(idioma):
    t = open(os.path.join(PERFIL, f"README.{idioma}.md"), encoding="utf-8").read()
    alt = {"pt": ("Davi Castro — desenvolvedor full stack e infraestrutura de redes", "Números", "Mapa dos projetos"),
           "en": ("Davi Castro — full-stack developer and network infrastructure", "Numbers", "Project map")}[idioma]
    suf = "" if idioma == "pt" else "-en"
    t = t.replace("{{TOPO}}", imagem_tema("topo" + suf, alt[0]))
    t = t.replace("{{NUMEROS}}", imagem_tema("numeros" + suf, alt[1]))
    t = t.replace("{{MAPA}}", imagem_tema("mapa" + suf, alt[2]))
    t = t.replace("{{DESTAQUES}}", bloco_destaques(idioma))
    t = t.replace("{{DATA}}", date.today().strftime("%d/%m/%Y" if idioma == "pt" else "%Y-%m-%d"))
    return "<!-- Gerado por perfil/gerar.py — edite perfil/README." + idioma + ".md e perfil/projetos.json. -->\n" + t


if __name__ == "__main__":
    for tema in TEMAS:
        for idioma, suf in (("pt", ""), ("en", "-en")):
            gravar(f"topo{suf}-{tema}.svg", topo(tema, idioma))
            gravar(f"numeros{suf}-{tema}.svg", numeros(tema, idioma))
            gravar(f"mapa{suf}-{tema}.svg", mapa(tema, idioma))
            gravar(f"arvore{suf}-{tema}.svg", arvore(tema, idioma))
    open(os.path.join(RAIZ, "PROJETOS.md"), "w", encoding="utf-8", newline="\n").write(projetos_md())
    for idioma, arq in (("pt", "README.md"), ("en", "README-en.md")):
        if os.path.exists(os.path.join(PERFIL, f"README.{idioma}.md")):
            open(os.path.join(RAIZ, arq), "w", encoding="utf-8", newline="\n").write(montar_readme(idioma))
    print("ok:", len(os.listdir(SVG)), "svgs, PROJETOS.md e READMEs")
