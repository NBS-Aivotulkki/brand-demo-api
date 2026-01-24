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
        "text": "Jos joudumme valitsemaan, haluamme että brändimme tuntuu enemmän:",
        "options": {
            "A": "Yritysten tehokkaalta työkalulta",
            "B": "Yritysten strategiselta suunnannäyttäjältä",
            "C": "Ihmisten arkea helpottavalta kumppanilta",
            "D": "Ihmisten identiteettiä vahvistavalta ilmiöltä"
        }
    },
    {
        "id": 2,
        "text": "Haluamme brändimme painottuvan enemmän:",
        "options": {
            "A": "Suorituskykyyn ja tuloksiin",
            "B": "Kokemukseen ja vuorovaikutukseen",
            "C": "Ajatteluun ja asiantuntijuuteen",
            "D": "Tunnesuhteeseen ja merkitykseen"
        }
    },
    {
        "id": 3,
        "text": "Kun joku kohtaa meidät, haluamme hänen ensisijaisesti kokevan:",
        "options": {
            "A": "Luottamusta organisaatioon",
            "B": "Vetovoimaa tuotteeseen",
            "C": "Kiinnostusta ideologiaan",
            "D": "Yhteyttä persoonaan"
        }
    },
    {
        "id": 4,
        "text": "Haluamme mieluummin, että meistä sanotaan:",
        "options": {
            "A": "Toimii aina",
            "B": "Tuntuu paremmalta kuin muut",
            "C": "Näyttää paremmalta kuin muut",
            "D": "Ajattelee pidemmälle kuin muut"
        }
    },
    {
        "id": 5,
        "text": "Kun asiakas valitsee meidät, hänen pitäisi ensisijaisesti tuntea:",
        "options": {
            "A": "Turvaa",
            "B": "Ylpeyttä",
            "C": "Innostusta",
            "D": "Rauhaa"
        }
    },
    {
        "id": 6,
        "text": "Haluamme brändimme olevan mieluummin:",
        "options": {
            "A": "Auktoriteetti",
            "B": "Kumppani",
            "C": "Haastaja",
            "D": "Suunnannäyttäjä"
        }
    },
    {
        "id": 7,
        "text": "Valitsemme mieluummin:",
        "options": {
            "A": "Että kaikki eivät pidä meistä",
            "B": "Että olemme helposti lähestyttäviä",
            "C": "Että herätämme keskustelua",
            "D": "Että koemme harvoin vastustusta"
        }
    },
    {
        "id": 8,
        "text": "Brändimme on tarkoitus ennemmin:",
        "options": {
            "A": "Määritellä oikea tapa",
            "B": "Rikkoa vanha tapa",
            "C": "Yhdistää molemmat",
            "D": "Ohittaa koko keskustelu"
        }
    },
    {
        "id": 9,
        "text": "Valitsemme mieluummin, että ratkaisumme on:",
        "options": {
            "A": "Kaunis",
            "B": "Nopea",
            "C": "Älykäs",
            "D": "Turvallinen"
        }
    },
    {
        "id": 10,
        "text": "Haluamme brändimme tuntuvan enemmän:",
        "options": {
            "A": "Lämpimältä",
            "B": "Itsevarmalta",
            "C": "Terävältä",
            "D": "Ylevältä"
        }
    },
    {
        "id": 11,
        "text": "Brändimme suhtautuminen sääntöihin on mieluummin:",
        "options": {
            "A": "Noudatamme niitä",
            "B": "Luomme niitä",
            "C": "Muutamme niitä",
            "D": "Rikomme niitä tarvittaessa"
        }
    },
    {
        "id": 12,
        "text": "Jos brändimme olisi henkilö, hän olisi ennemmin:",
        "options": {
            "A": "Johtaja",
            "B": "Ajattelija",
            "C": "Ystävä",
            "D": "Visionääri"
        }
    },
    {
        "id": 13,
        "text": "Haluamme että meistä muistetaan ensisijaisesti:",
        "options": {
            "A": "Mitä saatiin aikaan",
            "B": "Miltä tuntui",
            "C": "Miten ajattelu muuttui",
            "D": "Mitä uskallettiin"
        }
    },
    {
        "id": 14,
        "text": "Valitsemme mieluummin:",
        "options": {
            "A": "Ennustettavuuden",
            "B": "Hallitun riskin",
            "C": "Rohkean position",
            "D": "Epämukavan erottumisen"
        }
    },
    {
        "id": 15,
        "text": "Haluamme brändimme olevan maailmassa ennen kaikkea:",
        "options": {
            "A": "Vakauden lähde",
            "B": "Muutoksen katalyytti",
            "C": "Turvan rakentaja",
            "D": "Nautinnon mahdollistaja"
        }
    },
    {
        "id": 16,
        "text": "Valitse kaksi, mihin haluamme eniten kallistua:",
        "multi_select": True,
        "options": {
            "A": "Auktoriteetti",
            "B": "Lämpö",
            "C": "Rohkeus",
            "D": "Estetiikka",
            "E": "Äly"
        }
    },
    {
        "id": 17,
        "text": "Valitse kaksi, mitä olemme valmiita uhraamaan:",
        "multi_select": True,
        "options": {
            "A": "Nopeus",
            "B": "Massasuosio",
            "C": "Pehmeys",
            "D": "Varovaisuus",
            "E": "Mukavuus"
        }
    },
    {
        "id": 18,
        "text": "Haluamme, että asiakas:",
        "options": {
            "A": "Kuuntelee meitä",
            "B": "Kunnioittaa meitä",
            "C": "Luottaa meihin",
            "D": "Seuraa meitä"
        }
    },
    {
        "id": 19,
        "text": "Haluamme olla enemmän:",
        "options": {
            "A": "Ratkaisu",
            "B": "Ajatus",
            "C": "Kokemus",
            "D": "Liike"
        }
    },
    {
        "id": 20,
        "text": "Jos meidät on pakko kuvata yhdellä lauseella, valitsemme mieluummin:",
        "options": {
            "A": "Turvallinen ja vahva",
            "B": "Rohkea ja erottuva",
            "C": "Lämmin ja inhimillinen",
            "D": "Älykäs ja visionäärinen"
        }
    }
]

# 4) Painot: (kysymys -> vaihtoehto -> dimensiot)
# Tässä on esimerkki; tämä on se “aivot”, jota säädät.
WEIGHTS = {
    1: {
        "A": {"Competence": 0.7, "Discipline": 0.4},
        "B": {"Authority": 0.6, "Vision": 0.5},
        "C": {"Warmth": 0.6, "Integrity": 0.4},
        "D": {"Sophistication": 0.6, "Playfulness": 0.4}
    },
    2: {
        "A": {"Competence": 0.7, "Discipline": 0.4},
        "B": {"Warmth": 0.5, "Playfulness": 0.4},
        "C": {"Authority": 0.5, "Integrity": 0.5},
        "D": {"Vision": 0.6, "Sophistication": 0.4}
    },
    3: {
        "A": {"Authority": 0.6, "Integrity": 0.5},
        "B": {"Sophistication": 0.6, "Playfulness": 0.3},
        "C": {"Vision": 0.6, "Boldness": 0.4},
        "D": {"Warmth": 0.7, "Integrity": 0.3}
    },
    4: {
        "A": {"Discipline": 0.6, "Competence": 0.5},
        "B": {"Warmth": 0.5, "Playfulness": 0.4},
        "C": {"Sophistication": 0.6, "Authority": 0.4},
        "D": {"Vision": 0.7, "Boldness": 0.4}
    },
    5: {
        "A": {"Integrity": 0.7, "Discipline": 0.4},
        "B": {"Boldness": 0.6, "Sophistication": 0.4},
        "C": {"Vision": 0.6, "Playfulness": 0.4},
        "D": {"Warmth": 0.6, "Integrity": 0.4}
    },
    6: {
        "A": {"Authority": 0.8, "Discipline": 0.4},
        "B": {"Warmth": 0.6, "Integrity": 0.4},
        "C": {"Boldness": 0.7, "Vision": 0.4},
        "D": {"Vision": 0.7, "Sophistication": 0.3}
    },
    7: {
        "A": {"Boldness": 0.7, "Authority": 0.4},
        "B": {"Warmth": 0.6, "Integrity": 0.4},
        "C": {"Vision": 0.6, "Playfulness": 0.4},
        "D": {"Discipline": 0.7, "Competence": 0.4}
    },
    8: {
        "A": {"Authority": 0.8, "Discipline": 0.4},
        "B": {"Boldness": 0.8, "Vision": 0.4},
        "C": {"Vision": 0.5, "Integrity": 0.4},
        "D": {"Sophistication": 0.6, "Playfulness": 0.3}
    },
    9: {
        "A": {"Sophistication": 0.7, "Playfulness": 0.3},
        "B": {"Discipline": 0.7, "Competence": 0.4},
        "C": {"Vision": 0.7, "Authority": 0.3},
        "D": {"Integrity": 0.7, "Warmth": 0.3}
    },
    10: {
        "A": {"Warmth": 0.8, "Integrity": 0.4},
        "B": {"Authority": 0.7, "Discipline": 0.4},
        "C": {"Boldness": 0.7, "Vision": 0.4},
        "D": {"Sophistication": 0.7, "Authority": 0.3}
    },
    11: {
        "A": {"Discipline": 0.7, "Integrity": 0.4},
        "B": {"Authority": 0.8, "Competence": 0.4},
        "C": {"Vision": 0.7, "Warmth": 0.4},
        "D": {"Boldness": 0.8, "Playfulness": 0.3}
    },
    12: {
        "A": {"Authority": 0.7, "Discipline": 0.4},
        "B": {"Competence": 0.7, "Integrity": 0.4},
        "C": {"Warmth": 0.7, "Playfulness": 0.3},
        "D": {"Vision": 0.8, "Boldness": 0.4}
    },
    13: {
        "A": {"Competence": 0.7, "Discipline": 0.4},
        "B": {"Warmth": 0.7, "Playfulness": 0.3},
        "C": {"Vision": 0.7, "Integrity": 0.4},
        "D": {"Boldness": 0.7, "Sophistication": 0.3}
    },
    14: {
        "A": {"Discipline": 0.8, "Integrity": 0.4},
        "B": {"Competence": 0.6, "Vision": 0.4},
        "C": {"Boldness": 0.8, "Vision": 0.4},
        "D": {"Playfulness": 0.6, "Sophistication": 0.4}
    },
    15: {
        "A": {"Authority": 0.7, "Integrity": 0.4},
        "B": {"Vision": 0.8, "Boldness": 0.4},
        "C": {"Warmth": 0.7, "Discipline": 0.4},
        "D": {"Sophistication": 0.8, "Playfulness": 0.4}
    },
    16: {
        "A": {"Authority": 0.8},
        "B": {"Warmth": 0.8},
        "C": {"Boldness": 0.8},
        "D": {"Sophistication": 0.8},
        "E": {"Competence": 0.8}
    },
    17: {
        "A": {"Sophistication": 0.6},
        "B": {"Authority": 0.6},
        "C": {"Boldness": 0.6},
        "D": {"Warmth": 0.6},
        "E": {"Discipline": 0.6}
    },
    18: {
        "A": {"Authority": 0.7, "Vision": 0.3},
        "B": {"Authority": 0.7, "Integrity": 0.4},
        "C": {"Integrity": 0.8, "Warmth": 0.4},
        "D": {"Boldness": 0.8, "Playfulness": 0.3}
    },
    19: {
        "A": {"Competence": 0.7, "Discipline": 0.4},
        "B": {"Vision": 0.7, "Integrity": 0.4},
        "C": {"Warmth": 0.6, "Playfulness": 0.4},
        "D": {"Boldness": 0.7, "Sophistication": 0.4}
    },
    20: {
        "A": {"Authority": 0.7, "Integrity": 0.5},
        "B": {"Boldness": 0.8, "Vision": 0.4},
        "C": {"Warmth": 0.8, "Integrity": 0.4},
        "D": {"Vision": 0.7, "Competence": 0.4}
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

