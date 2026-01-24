from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional
import math

app = FastAPI(title="Brand Archetype Demo", version="0.1")

Option = Literal["A", "B", "C", "D", "E"]

# 1) Dimensiot (B2B-kestävä setti)
DIMENSIONS = [
    "Competence",      # osaaminen, laatu, suoritus
    "Integrity",       # rehellisyys, selkäranka, läpinäkyvyys
    "Authority",       # standardit, normatiivisuus, johtajuus
    "Sophistication",  # premium, estetiikka, status
    "Vision",          # tulevaisuus, murros, transformaatio
    "Discipline",      # prosessikuri, ennustettavuus
    "Boldness",        # rohkeus, rajaaminen, kantaaottavuus
    "Warmth",          # kumppanuus, empatia
    "Playfulness"      # keveys, huumori
]

# 2) Arkkityyppiprototyypit (0..1 painot)
ARCHETYPES: Dict[str, Dict[str, float]] = {
    "Ruler":     {"Authority":0.95,"Discipline":0.75,"Sophistication":0.70,"Competence":0.70,"Warmth":0.20,"Playfulness":0.05,"Boldness":0.55,"Integrity":0.60,"Vision":0.30},
    "Sage":      {"Competence":0.85,"Integrity":0.65,"Authority":0.60,"Vision":0.55,"Discipline":0.45,"Sophistication":0.35,"Warmth":0.25,"Playfulness":0.05,"Boldness":0.25},
    "Hero":      {"Boldness":0.80,"Competence":0.70,"Discipline":0.60,"Authority":0.45,"Vision":0.55,"Integrity":0.45,"Sophistication":0.25,"Warmth":0.20,"Playfulness":0.10},
    "Creator":   {"Vision":0.85,"Sophistication":0.45,"Competence":0.55,"Boldness":0.50,"Integrity":0.35,"Authority":0.25,"Discipline":0.25,"Warmth":0.25,"Playfulness":0.35},
    "Explorer":  {"Boldness":0.70,"Vision":0.60,"Competence":0.45,"Integrity":0.30,"Authority":0.20,"Discipline":0.20,"Sophistication":0.30,"Warmth":0.20,"Playfulness":0.25},
    "Outlaw":    {"Boldness":0.95,"Vision":0.55,"Authority":0.30,"Discipline":0.15,"Integrity":0.35,"Sophistication":0.20,"Competence":0.45,"Warmth":0.10,"Playfulness":0.15},
    "Magician":  {"Vision":0.90,"Authority":0.35,"Competence":0.55,"Sophistication":0.40,"Integrity":0.35,"Discipline":0.25,"Boldness":0.45,"Warmth":0.25,"Playfulness":0.20},
    "Caregiver": {"Warmth":0.90,"Integrity":0.75,"Competence":0.45,"Discipline":0.35,"Authority":0.20,"Sophistication":0.15,"Vision":0.25,"Boldness":0.20,"Playfulness":0.10},
    "Everyman":  {"Warmth":0.55,"Integrity":0.45,"Competence":0.40,"Authority":0.10,"Sophistication":0.10,"Vision":0.15,"Discipline":0.25,"Boldness":0.15,"Playfulness":0.25},
    "Lover":     {"Sophistication":0.70,"Warmth":0.65,"Playfulness":0.35,"Integrity":0.30,"Competence":0.25,"Authority":0.20,"Vision":0.25,"Discipline":0.10,"Boldness":0.25},
    "Jester":    {"Playfulness":0.95,"Warmth":0.45,"Boldness":0.35,"Vision":0.25,"Discipline":0.05,"Authority":0.05,"Sophistication":0.15,"Competence":0.25,"Integrity":0.20},
    "Innocent":  {"Integrity":0.70,"Warmth":0.60,"Discipline":0.35,"Competence":0.35,"Authority":0.10,"Sophistication":0.15,"Vision":0.20,"Boldness":0.10,"Playfulness":0.15}
}

# 3) Kysymykset (minidemo). Lisää myöhemmin lisää samalla rakenteella.
QUESTIONS = [
    {
        "id": 1,
        "text": "Haluamme, että yrityksemme olemassaolon syy nähdään ennen kaikkea näin:",
        "options": {
            "A": "Teemme asiat tehokkaammin kuin muut",
            "B": "Teemme asiat laadukkaammin kuin muut",
            "C": "Teemme asiat oikein, vaikka se olisi hitaampaa",
            "D": "Muutamme koko toimialan toimintatapaa"
        }
    },
    {
        "id": 2,
        "text": "Haluamme, että meidät tunnetaan eniten siitä, että emme hyväksy:",
        "options": {
            "A": "Keskinkertaista laatua",
            "B": "Epärehellistä toimintaa",
            "C": "Lyhytnäköisiä ratkaisuja",
            "D": "Rohkeuden puutetta"
        }
    },
    {
        "id": 5,
        "text": "Millaisena haluamme tulla nähdyksi:",
        "options": {
            "A": "Varovainen",
            "B": "Rohkea",
            "C": "Kurinalainen",
            "D": "Suora"
        }
    },
    {
        "id": 7,
        "text": "Asiakkaan pitäisi tuntea meitä valitessaan (valitse 2):",
        "multi_select": True,
        "options": {
            "A": "Ylpeyttä",
            "B": "Kunnianhimoa",
            "C": "Rauhallista varmuutta",
            "D": "Moraalista selkeyttä"
        }
    },
    {
        "id": 9,
        "text": "Brändin rooli päätöksessä:",
        "options": {
            "A": "Auttaa vertailemaan",
            "B": "Helpottaa valintaa",
            "C": "Pienentää riskiä",
            "D": "Määrittää, mikä on oikea valinta"
        }
    },
    {
        "id": 11,
        "text": "Olemme ennen kaikkea:",
        "options": {
            "A": "Kurinalainen rakentaja",
            "B": "Rohkea suunnannäyttäjä",
            "C": "Moraalinen standardi",
            "D": "Älyllinen auktoriteetti"
        }
    },
    {
  "id": 12,
  "text": "Haluamme tulla nähdyksi ensisijaisesti:",
  "options": {
    "A": "Turvallisena",
    "B": "Rohkeana",
    "C": "Arvokkaana",
    "D": "Uudistavana"
  }
}

]

# 4) Painot: (kysymys -> vaihtoehto -> dimensiot)
# Tässä on esimerkki; tämä on se “aivot”, jota säädät.
WEIGHTS: Dict[int, Dict[str, Dict[str, float]]] = {
    1: {
        "A": {"Competence": 0.6, "Discipline": 0.4},
        "B": {"Competence": 0.8, "Sophistication": 0.2},
        "C": {"Integrity": 0.9, "Discipline": 0.3},
        "D": {"Vision": 0.9, "Boldness": 0.5, "Authority": 0.2}
    },
    2: {
        "A": {"Competence": 0.7, "Discipline": 0.3},
        "B": {"Integrity": 0.9, "Authority": 0.2},
        "C": {"Discipline": 0.5, "Authority": 0.3},
        "D": {"Boldness": 0.8, "Vision": 0.4}
    },
    5: {
        "A": {"Discipline": 0.5},
        "B": {"Boldness": 0.7, "Vision": 0.3},
        "C": {"Discipline": 0.8, "Authority": 0.2},
        "D": {"Authority": 0.4, "Integrity": 0.2}
    },
    7: {
        "A": {"Sophistication": 0.4, "Authority": 0.2},
        "B": {"Boldness": 0.5, "Vision": 0.3},
        "C": {"Integrity": 0.4, "Discipline": 0.3},
        "D": {"Integrity": 0.7, "Authority": 0.2}
    },
    9: {
        "A": {"Competence": 0.2},
        "B": {"Competence": 0.3, "Warmth": 0.2},
        "C": {"Integrity": 0.4, "Discipline": 0.4},
        "D": {"Authority": 0.8, "Sophistication": 0.2}
    },
    11: {
        "A": {"Discipline": 0.8, "Competence": 0.3},
        "B": {"Boldness": 0.7, "Vision": 0.5},
        "C": {"Integrity": 0.9, "Authority": 0.4},
        "D": {"Authority": 0.7, "Competence": 0.6}
    },
    12: {
        "A": {"Integrity": 0.4, "Discipline": 0.4},
        "B": {"Boldness": 0.6, "Vision": 0.2},
        "C": {"Sophistication": 0.6, "Authority": 0.2},
        "D": {"Vision": 0.7, "Boldness": 0.3}
}

}

# 5) Micro-suositukset (minidemo)
REC_ARCHETYPE = {
    "Ruler": {
        "tone": ["Puhu standardeista ja periaatteista, älä trendeistä.", "Käytä päätöskieltä; vältä liiallista selittelyä."],
        "proof": ["Sertifikaatit/auditoinnit + referenssitalot.", "SLA:t, vasteajat ja riskinpoistomekanismit."],
        "design": ["Järjestelmällinen, selkeä hierarkia, ei koristeita."],
        "cx": ["Ennustettava rytmi, selkeä omistajuus, eskalointipolku."],
        "bounds": ["Karsi asiakkuudet, joissa periaatteita ei kunnioiteta."]
    },
    "Sage": {
        "tone": ["Opeta ja määrittele; tee päätöksenteko helpoksi."],
        "proof": ["Data, benchmarkit, menetelmät ja perustelut."],
        "design": ["Selkeä informaatioarkkitehtuuri, havainnollistavat kaaviot."],
        "cx": ["Dokumentaatio ja jatkuva oppiminen osaksi toimitusta."],
        "bounds": ["Vältä hype-kieltä; pysy todennettavassa."]
    },
    "Hero": {
        "tone": ["Haasta ja kannusta; puhu voittamisesta ja vaikeista valinnoista."],
        "proof": ["Ennen–jälkeen -tulokset, kovat numerot, vaikeat caset."],
        "design": ["Selkeä ja jämäkkä; visuaalisesti energinen mutta hallittu."],
        "cx": ["Nopea reagointi, selkeät lupaukset ja tiukka toteutus."],
        "bounds": ["Älä pehmennä ydinhaastetta miellyttämisen takia."]
    }
}

REC_DIMENSION = {
    "Integrity": ["Läpinäkyvyys oletukseksi: päätöskriteerit ja hinnoittelun logiikka näkyviin.", "Kirjoita 'mitä emme tee' ja pidä siitä kiinni."],
    "Authority": ["Muotoile kategorian standardi: 'Näin tämä tehdään oikein'.", "Rajaa: kenelle et ole ja miksi."],
    "Vision": ["Näytä suunta: tiekartta, ennen–jälkeen -mallit.", "Tee murros konkreettisiksi valinnoiksi, ei iskulauseiksi."],
    "Discipline": ["SLA ja toimitusrytmi: ennustettavuus on brändi.", "Lupauskuri: yksi lupaus, yksi omistaja."],
    "Sophistication": ["Premium näkyy yksityiskohdissa: typografia, rytmi, tila, materiaalit.", "Älä alihinnoittele, jos haluat premium-position."],
    "Boldness": ["Valitse puolensa ja hyväksy, että kaikki eivät pidä.", "Kirjoita eksplisiittiset rajat: 'emme tee X'."],
    "Warmth": ["Kumppanuus näkyy käytöksessä: kuuntelu, ennakointi, reiluus.", "Tee vaikeasta helpompaa asiakkaalle, ilman alistumista."],
    "Competence": ["Todista osaaminen: caset, benchmarkit, referenssit, menetelmät.", "Näytä laadunvarmistus: miten estätte virheet."],
    "Playfulness": ["Käytä keveyttä harkiten: selkeys ensin, vitsi vasta sitten.", "Pidä huumori brändin palvelijana, ei sen johtajana."]
}


class Answer(BaseModel):
    question_id: int
    option: Option

class AssessRequest(BaseModel):
    answers: List[Answer]
    respondent_label: Optional[str] = None

def cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    dot = sum(a[k] * b[k] for k in DIMENSIONS)
    na = math.sqrt(sum(a[k] * a[k] for k in DIMENSIONS))
    nb = math.sqrt(sum(b[k] * b[k] for k in DIMENSIONS))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def compute_dimensions(answers: List[Answer]) -> Dict[str, float]:
    raw = {d: 0.0 for d in DIMENSIONS}
    for a in answers:
        qmap = WEIGHTS.get(a.question_id, {})
        w = qmap.get(a.option, {})
        for d, val in w.items():
            raw[d] += float(val)
    # skaalaus 0..100 (clamp)
    out = {}
    for d, v in raw.items():
        lo, hi = -10.0, 10.0  # demossa pieni kysymysmäärä; myöhemmin nosta tätä
        vv = max(lo, min(hi, v))
        out[d] = (vv - lo) / (hi - lo) * 100.0
    return out

def score_archetypes(dim_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    scores = []
    for name, proto in ARCHETYPES.items():
        b = {d: float(proto.get(d, 0.0)) for d in DIMENSIONS}
        sim = cosine_similarity(dim_scores, b)
        scores.append({"key": name, "similarity": sim})
    scores.sort(key=lambda x: x["similarity"], reverse=True)
    return scores

def make_recommendations(primary: str, top_dims: List[str]) -> List[Dict[str, Any]]:
    recs = []
    arch = REC_ARCHETYPE.get(primary, {})
    if arch:
        recs.append({"title": "Tone of voice", "items": arch.get("tone", [])})
        recs.append({"title": "Proof-strategia", "items": arch.get("proof", [])})
        recs.append({"title": "Design-signaalit", "items": arch.get("design", [])})
        recs.append({"title": "CX-signaalit", "items": arch.get("cx", [])})
        recs.append({"title": "Rajaus", "items": arch.get("bounds", [])})

    for d in top_dims:
        items = REC_DIMENSION.get(d, [])
        if items:
            recs.append({"title": f"Tarkennus: {d}", "items": items})
    return recs

@app.get("/questions")
def get_questions():
    return QUESTIONS

@app.post("/assess")
def assess(req: AssessRequest):
    dim_scores = compute_dimensions(req.answers)
    archetypes = score_archetypes(dim_scores)

    primary = archetypes[0]["key"]
    secondary = archetypes[1]["key"] if len(archetypes) > 1 else None
    shadow = archetypes[-1]["key"] if len(archetypes) > 2 else None

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]
    low_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1])[:2]]

    recs = make_recommendations(primary, top_dims)

    return {
        "primary_archetype": primary,
        "secondary_archetype": secondary,
        "shadow_archetype": shadow,
        "dimensions": dim_scores,
        "archetypes": archetypes[:5],
        "top_strengths": top_dims,
        "conscious_lows": low_dims,
        "recommendations": recs
    }
from fastapi.responses import HTMLResponse
from fastapi import Request

def render_form():
    html = []
    html.append("<html><head><meta charset='utf-8'><title>Brand Demo</title></head><body>")
    html.append("<h2>Brändiarkkityyppi & persoonallisuus (demo)</h2>")
    html.append("<form method='post' action='/ui-assess'>")

    for q in QUESTIONS:
        qid = q["id"]
        html.append(f"<fieldset style='margin:12px 0; padding:12px; border:1px solid #ddd;'>")
        html.append(f"<legend><b>{qid}. {q['text']}</b></legend>")

        multi = q.get("multi_select", False)
        input_type = "checkbox" if multi else "radio"
        name = f"q{qid}" if not multi else f"q{qid}[]"

        for opt, label in q["options"].items():
            html.append(
                f"<label style='display:block; margin:6px 0;'>"
                f"<input type='{input_type}' name='{name}' value='{opt}'> "
                f"<b>{opt}</b> {label}"
                f"</label>"
            )

        if multi:
            html.append("<div style='font-size:12px; color:#555;'>Valitse 2</div>")

        html.append("</fieldset>")

    html.append("<button type='submit' style='padding:10px 14px;'>Laske suositus</button>")
    html.append("</form></body></html>")
    return "\n".join(html)

@app.get("/", response_class=HTMLResponse)
def ui():
    return render_form()

@app.post("/ui-assess", response_class=HTMLResponse)
async def ui_assess(request: Request):
    form = await request.form()

    # rakennetaan Answer-lista kuten /assess odottaa
    parsed = []
    for q in QUESTIONS:
        qid = q["id"]
        multi = q.get("multi_select", False)
        if not multi:
            val = form.get(f"q{qid}")
            if val:
                parsed.append(Answer(question_id=qid, option=val))
        else:
            vals = form.getlist(f"q{qid}[]")
            # pidä korkeintaan 2
            for v in vals[:2]:
                parsed.append(Answer(question_id=qid, option=v))

    # käytä samaa logiikkaa kuin /assess
    dim_scores = compute_dimensions(parsed)
    archetypes = score_archetypes(dim_scores)
    primary = archetypes[0]["key"]
    secondary = archetypes[1]["key"] if len(archetypes) > 1 else None
    shadow = archetypes[-1]["key"] if len(archetypes) > 2 else None

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]
    recs = make_recommendations(primary, top_dims)

    # renderöi tulos
    out = []
    out.append("<html><head><meta charset='utf-8'><title>Tulos</title></head><body>")
    out.append("<a href='/'>← takaisin</a>")
    out.append(f"<h2>Pääarkkityyppi: {primary}</h2>")
    out.append(f"<p>Toissijainen: <b>{secondary}</b> · Varjo: <b>{shadow}</b></p>")
    out.append(f"<p><b>Top-dimensiot:</b> {', '.join(top_dims)}</p>")

    out.append("<h3>Dimensiot (0–100)</h3><ul>")
    for k, v in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True):
        out.append(f"<li>{k}: {v:.1f}</li>")
    out.append("</ul>")

    out.append("<h3>Suositukset</h3>")
    for b in recs:
        out.append(f"<h4>{b['title']}</h4><ul>")
        for it in b["items"]:
            out.append(f"<li>{it}</li>")
        out.append("</ul>")

    out.append("</body></html>")
    return "\n".join(out)

