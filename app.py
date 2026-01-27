from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional
import math
import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# --- KÄÄNNÖSKARTTA (lisätään tähän, heti importtien jälkeen) ---

translations = {
    "Competence": "Osaaminen",
    "Integrity": "Luotettavuus",
    "Authority": "Auktoriteetti",
    "Sophistication": "Tyylikkyys",
    "Vision": "Näkemys",
    "Discipline": "Jämäkkyys",
    "Boldness": "Rohkeus",
    "Warmth": "Lämpö",
    "Playfulness": "Leikkisyys",

    "Ruler": "Hallitsija",
    "Sage": "Viisas",
    "Hero": "Sankari",
    "Creator": "Luoja",
    "Explorer": "Tutkija",
    "Outlaw": "Kapinallinen",
    "Magician": "Visionääri",
    "Caregiver": "Hoivaaja",
    "Everyman": "Tavallinen",
    "Lover": "Rakastaja",
    "Jester": "Narri",
    "Innocent": "Optimisti",
}

# Käännösapu: jos avainta ei löydy, palautetaan alkuperäinen
def t(key: str) -> str:
    return translations.get(key, key)


# --- FASTAPI-APP LUODAAN TÄMÄN JÄLKEEN ---
# HUOM: App luodaan vain kerran (poistettu tuplaluonti)

app = FastAPI(title="Brand Archetype Demo", version="0.1")

# Mountataan static-kansio
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")


# Englanninkieliset avaimet logiikkaa varten
DIMENSIONS = [
    "Competence",
    "Integrity",
    "Authority",
    "Sophistication",
    "Vision",
    "Discipline",
    "Boldness",
    "Warmth",
    "Playfulness",
]

# Käyttöliittymää varten suomenkielinen lista
DIMENSIONS_FI = [t(d) for d in DIMENSIONS]

ARCHETYPE_DESCRIPTIONS = {
    "Ruler": "HALLITSIJA / JOHTAJA rakentaa luottamusta auktoriteetin, rakenteen ja selkeyden kautta. Se määrittelee suunnan, luo järjestyksen ja asettaa standardin, jota muut seuraavat. HALLITSIJA / JOHTAJA -brändi viestii vakaudesta, kontrollista ja pitkäjänteisyydestä. Esimerkkejä ovat Rolex, Mercedes-Benz, IBM ja Microsoft.",
    "Sage": "VIISAS / ASIANTUNTIJA perustuu tietoon, ymmärrykseen ja totuuden etsimiseen. Se auttaa asiakkaitaan näkemään maailmaa kirkkaammin ja tekemään parempia päätöksiä. VIISAS / ASIANTUNTIJA -brändi rakentaa arvonsa asiantuntijuudesta ja luotettavuudesta. Esimerkkejä: Google, BBC, TED, Harvard.",
    "Hero": "SANKARI / VOITTAJA edustaa rohkeutta, päättäväisyyttä ja kykyä ylittää esteet. Se kutsuu toimintaan ja lupaa muutosta tekojen, ei sanojen kautta. SANKARI / VOITTAJA -brändi inspiroi parempaan suoritukseen. Esimerkkejä: Nike, Adidas, Red Bull, Gatorade.",
    "Creator": "LUOJA / INNOSTAJA ammentaa luovuudesta ja omaperäisyydestä. Se rakentaa uutta maailmaa ja haastaa tavanomaiset ratkaisut. LUOJA / INNOSTAJA -brändi rohkaisee ilmaisemaan itseä ja rikkomaan rajoja. Esimerkkejä: Apple, LEGO, Adobe, Pixar.",
    "Explorer": "TUTKIJA / SEIKKAILIJA kutsuu vapauteen ja itsensä löytämiseen. Se rikkoo rajoja, haastaa mukavuusalueen ja etsii jatkuvasti uusia mahdollisuuksia. TUTKIJA / SEIKKAILIJA -brändi lupaa elämyksiä ja itsenäisyyttä. Esimerkkejä: Jeep, The North Face, Patagonia, National Geographic.",
    "Outlaw": "KAPINALLINEN / UUDISTAJA syntyy vastarinnasta ja halusta muuttaa maailmaa. Se rikkoo sääntöjä, kyseenalaistaa järjestelmän ja pakottaa muutoksen tapahtumaan. KAPINALLINEN / UUDISTAJA -brändi vetää puoleensa rohkeita ajattelijoita. Esimerkkejä: Harley-Davidson, Diesel, Vice, Supreme.",
    "Magician": "VISIONÄÄRI / TAIKURI lupaa transformaatiota ja uuden todellisuuden. Se tekee monimutkaisesta yksinkertaista ja mahdottomasta mahdollista. VISIONÄÄRI / TAIKURI -brändi herättää ihmetystä ja uskoa muutokseen. Esimerkkejä: Disney, Tesla, Apple (visionäärinen puoli), SpaceX.",
    "Caregiver": "HOIVAAJA / SUOJELIJA rakentaa turvaa, luottamusta ja inhimillisyyttä. Se asettaa ihmisen ja vastuullisuuden kaiken keskiöön. HOIVAAJA / SUOJELIJA -brändi lupaa, että asiakkaasta pidetään huolta. Esimerkkejä: UNICEF, Red Cross, Dove, Volvo.",
    "Everyman": "TAVALLINEN / LUOTETTAVA edustaa aitoutta, rehellisyyttä ja samaistuttavuutta. Se on helposti lähestyttävä ja tuntuu \"meidän kaltaiseltamme\". TAVALLINEN / LUOTETTAVA-brändi rakentaa luottamusta arkisuuden kautta. Esimerkkejä: IKEA, Levi’s, Target, Volkswagen.",
    "Lover": "RAKASTAJA / ESTEETIKKO rakentuu intohimosta, kauneudesta ja emotionaalisesta vetovoimasta. Se korostaa nautintoa, estetiikkaa ja aistillisuutta. RAKASTAJA / ESTEETIKKO -brändi lupaa elämyksiä ja syvää tunnetta. Esimerkkejä: Chanel, Dior, Ferrari, Häagen-Dazs.",
    "Jester": "NARRI / VIIHDYTTÄJÄ tuo keveyttä, iloa ja vapautta. Se rikkoo vakavuuden huumorilla ja yllättävillä näkökulmilla. NARRI / VIIHDYTTÄJÄ -brändi tekee elämästä hauskempaa ja rennompaa. Esimerkkejä: Old Spice, M&M’s, TikTok, Netflix (viihdepuoli).",
    "Innocent": "VIATON / OPTIMISTI edustaa vilpittömyyttä, toivoa ja uskoa hyvään. Se lupaa turvallisuutta, yksinkertaisuutta ja mielenrauhaa. VIATON / OPTIMISTI -brändi tuo maailmaan valoa ja selkeyttä. Esimerkkejä: Coca-Cola, Dove (puhdas puoli), Innocent Drinks, Aveeno."
}

ARCHETYPES: Dict[str, Dict[str, float]] = {
    "Ruler":     {"Authority": 0.95, "Discipline": 0.75, "Sophistication": 0.70, "Competence": 0.70, "Warmth": 0.20, "Playfulness": 0.05, "Boldness": 0.55, "Integrity": 0.60, "Vision": 0.30},
    "Sage":      {"Competence": 0.85, "Integrity": 0.65, "Authority": 0.60, "Vision": 0.55, "Discipline": 0.45, "Sophistication": 0.35, "Warmth": 0.25, "Playfulness": 0.05, "Boldness": 0.25},
    "Hero":      {"Boldness": 0.80, "Competence": 0.70, "Discipline": 0.60, "Authority": 0.45, "Vision": 0.55, "Integrity": 0.45, "Sophistication": 0.25, "Warmth": 0.20, "Playfulness": 0.10},
    "Creator":   {"Vision": 0.85, "Sophistication": 0.45, "Competence": 0.55, "Boldness": 0.50, "Integrity": 0.35, "Authority": 0.25, "Discipline": 0.25, "Warmth": 0.25, "Playfulness": 0.35},
    "Explorer":  {"Boldness": 0.70, "Vision": 0.60, "Competence": 0.45, "Integrity": 0.30, "Authority": 0.20, "Discipline": 0.20, "Sophistication": 0.30, "Warmth": 0.20, "Playfulness": 0.25},
    "Outlaw":    {"Boldness": 0.95, "Vision": 0.55, "Authority": 0.30, "Discipline": 0.15, "Integrity": 0.35, "Sophistication": 0.20, "Competence": 0.45, "Warmth": 0.10, "Playfulness": 0.15},
    "Magician":  {"Vision": 0.90, "Authority": 0.35, "Competence": 0.55, "Sophistication": 0.40, "Integrity": 0.35, "Discipline": 0.25, "Boldness": 0.45, "Warmth": 0.25, "Playfulness": 0.20},
    "Caregiver": {"Warmth": 0.90, "Integrity": 0.75, "Competence": 0.45, "Discipline": 0.35, "Authority": 0.20, "Sophistication": 0.15, "Vision": 0.25, "Boldness": 0.20, "Playfulness": 0.10},
    "Everyman":  {"Warmth": 0.55, "Integrity": 0.45, "Competence": 0.40, "Authority": 0.10, "Sophistication": 0.10, "Vision": 0.15, "Discipline": 0.25, "Boldness": 0.15, "Playfulness": 0.25},
    "Lover":     {"Sophistication": 0.70, "Warmth": 0.65, "Playfulness": 0.35, "Integrity": 0.30, "Competence": 0.25, "Authority": 0.20, "Vision": 0.25, "Discipline": 0.10, "Boldness": 0.25},
    "Jester":    {"Playfulness": 0.95, "Warmth": 0.45, "Boldness": 0.35, "Vision": 0.25, "Discipline": 0.05, "Authority": 0.05, "Sophistication": 0.15, "Competence": 0.25, "Integrity": 0.20},
    "Innocent":  {"Integrity": 0.70, "Warmth": 0.60, "Discipline": 0.35, "Competence": 0.35, "Authority": 0.10, "Sophistication": 0.15, "Vision": 0.20, "Boldness": 0.10, "Playfulness": 0.15},
}

QUESTIONS = [
    {
        "id": 0,
        "text": "Onko yrityksenne asiakkaista suurin osa",
        "options": {
            "A": "miehiä",
            "B": "naisia",
            "C": "molempia yhtä paljon",
    },
},
    {"id": 1, "text": "Jos joudumme valitsemaan, haluamme että brändimme tuntuu enemmän:", "options": {"A": "Yritysten tehokkaalta työkalulta", "B": "Yritysten strategiselta suunnannäyttäjältä", "C": "Ihmisten arkea helpottavalta kumppanilta", "D": "Ihmisten identiteettiä vahvistavalta ilmiöltä"}},
    {"id": 2, "text": "Haluamme brändimme painottuvan enemmän:", "options": {"A": "Suorituskykyyn ja tuloksiin", "B": "Kokemukseen ja vuorovaikutukseen", "C": "Ajatteluun ja asiantuntijuuteen", "D": "Tunnesuhteeseen ja merkitykseen"}},
    {"id": 3, "text": "Kun joku kohtaa meidät, haluamme hänen ensisijaisesti kokevan:", "options": {"A": "Luottamusta organisaatioon", "B": "Vetovoimaa tuotteeseen", "C": "Kiinnostusta ideologiaan", "D": "Yhteyttä persoonaan"}},
    {"id": 4, "text": "Haluamme mieluummin, että meistä sanotaan:", "options": {"A": "Toimii aina", "B": "Tuntuu paremmalta kuin muut", "C": "Näyttää paremmalta kuin muut", "D": "Ajattelee pidemmälle kuin muut"}},
    {"id": 5, "text": "Kun asiakas valitsee meidät, hänen pitäisi ensisijaisesti tuntea:", "options": {"A": "Turvaa", "B": "Ylpeyttä", "C": "Innostusta", "D": "Rauhaa"}},
    {"id": 6, "text": "Haluamme brändimme olevan mieluummin:", "options": {"A": "Auktoriteetti", "B": "Kumppani", "C": "Haastaja", "D": "Suunnannäyttäjä"}},
    {"id": 7, "text": "Valitsemme mieluummin:", "options": {"A": "Että kaikki eivät pidä meistä", "B": "Että olemme helposti lähestyttäviä", "C": "Että herätämme keskustelua", "D": "Että koemme harvoin vastustusta"}},
    {"id": 8, "text": "Brändimme on tarkoitus ennemmin:", "options": {"A": "Määritellä oikea tapa", "B": "Rikkoa vanha tapa", "C": "Yhdistää molemmat", "D": "Ohittaa koko keskustelu"}},
    {"id": 9, "text": "Valitsemme mieluummin, että ratkaisumme on:", "options": {"A": "Kaunis", "B": "Nopea", "C": "Älykäs", "D": "Turvallinen"}},
    {"id": 10, "text": "Haluamme brändimme tuntuvan enemmän:", "options": {"A": "Lämpimältä", "B": "Itsevarmalta", "C": "Terävältä", "D": "Ylevältä"}},
    {"id": 11, "text": "Brändimme suhtautuminen sääntöihin on mieluummin:", "options": {"A": "Noudatamme niitä", "B": "Luomme niitä", "C": "Muutamme niitä", "D": "Rikomme niitä tarvittaessa"}},
    {"id": 12, "text": "Jos brändimme olisi henkilö, hän olisi ennemmin:", "options": {"A": "Johtaja", "B": "Ajattelija", "C": "Ystävä", "D": "Visionääri"}},
    {"id": 13, "text": "Haluamme että meistä muistetaan ensisijaisesti:", "options": {"A": "Mitä saatiin aikaan", "B": "Miltä tuntui", "C": "Miten ajattelu muuttui", "D": "Mitä uskallettiin"}},
    {"id": 14, "text": "Valitsemme mieluummin:", "options": {"A": "Ennustettavuuden", "B": "Hallitun riskin", "C": "Rohkean position", "D": "Epämukavan erottumisen"}},
    {"id": 15, "text": "Haluamme brändimme olevan maailmassa ennen kaikkea:", "options": {"A": "Vakauden lähde", "B": "Muutoksen katalyytti", "C": "Turvan rakentaja", "D": "Nautinnon mahdollistaja"}},
    {"id": 16, "text": "Valitse kaksi, mihin haluamme eniten kallistua:", "multi_select": True, "options": {"A": "Auktoriteetti", "B": "Lämpö", "C": "Rohkeus", "D": "Estetiikka", "E": "Äly"}},
    {"id": 17, "text": "Valitse kaksi, mitä olemme valmiita uhraamaan:", "multi_select": True, "options": {"A": "Nopeus", "B": "Massasuosio", "C": "Pehmeys", "D": "Varovaisuus", "E": "Mukavuus"}},
    {"id": 18, "text": "Haluamme, että asiakas:", "options": {"A": "Kuuntelee meitä", "B": "Kunnioittaa meitä", "C": "Luottaa meihin", "D": "Seuraa meitä"}},
    {"id": 19, "text": "Haluamme olla enemmän:", "options": {"A": "Ratkaisu", "B": "Ajatus", "C": "Kokemus", "D": "Liike"}},
    {"id": 20, "text": "Jos meidät on pakko kuvata yhdellä lauseella, valitsemme mieluummin:", "options": {"A": "Turvallinen ja vahva", "B": "Rohkea ja erottuva", "C": "Lämmin ja inhimillinen", "D": "Älykäs ja visionäärinen"}},
]

WEIGHTS = {
    1: {"A": {"Competence": 0.7, "Discipline": 0.4}, "B": {"Authority": 0.6, "Vision": 0.5}, "C": {"Warmth": 0.6, "Integrity": 0.4}, "D": {"Sophistication": 0.6, "Playfulness": 0.4}},
    2: {"A": {"Competence": 0.7, "Discipline": 0.4}, "B": {"Warmth": 0.5, "Playfulness": 0.4}, "C": {"Authority": 0.5, "Integrity": 0.5}, "D": {"Vision": 0.6, "Sophistication": 0.4}},
    3: {"A": {"Authority": 0.6, "Integrity": 0.5}, "B": {"Sophistication": 0.6, "Playfulness": 0.3}, "C": {"Vision": 0.6, "Boldness": 0.4}, "D": {"Warmth": 0.7, "Integrity": 0.3}},
    4: {"A": {"Discipline": 0.6, "Competence": 0.5}, "B": {"Warmth": 0.5, "Playfulness": 0.4}, "C": {"Sophistication": 0.6, "Authority": 0.4}, "D": {"Vision": 0.7, "Boldness": 0.4}},
    5: {"A": {"Integrity": 0.7, "Discipline": 0.4}, "B": {"Boldness": 0.6, "Sophistication": 0.4}, "C": {"Vision": 0.6, "Playfulness": 0.4}, "D": {"Warmth": 0.6, "Integrity": 0.4}},
    6: {"A": {"Authority": 0.8, "Discipline": 0.4}, "B": {"Warmth": 0.6, "Integrity": 0.4}, "C": {"Boldness": 0.7, "Vision": 0.4}, "D": {"Vision": 0.7, "Sophistication": 0.3}},
    7: {"A": {"Boldness": 0.7, "Authority": 0.4}, "B": {"Warmth": 0.6, "Integrity": 0.4}, "C": {"Vision": 0.6, "Playfulness": 0.4}, "D": {"Discipline": 0.7, "Competence": 0.4}},
    8: {"A": {"Authority": 0.8, "Discipline": 0.4}, "B": {"Boldness": 0.8, "Vision": 0.4}, "C": {"Vision": 0.5, "Integrity": 0.4}, "D": {"Sophistication": 0.6, "Playfulness": 0.3}},
    9: {"A": {"Sophistication": 0.7, "Playfulness": 0.3}, "B": {"Discipline": 0.7, "Competence": 0.4}, "C": {"Vision": 0.7, "Authority": 0.3}, "D": {"Integrity": 0.7, "Warmth": 0.3}},
    10: {"A": {"Warmth": 0.8, "Integrity": 0.4}, "B": {"Authority": 0.7, "Discipline": 0.4}, "C": {"Boldness": 0.7, "Vision": 0.4}, "D": {"Sophistication": 0.7, "Authority": 0.3}},
    11: {"A": {"Discipline": 0.7, "Integrity": 0.4}, "B": {"Authority": 0.8, "Competence": 0.4}, "C": {"Vision": 0.7, "Warmth": 0.4}, "D": {"Boldness": 0.8, "Playfulness": 0.3}},
    12: {"A": {"Authority": 0.7, "Discipline": 0.4}, "B": {"Competence": 0.7, "Integrity": 0.4}, "C": {"Warmth": 0.7, "Playfulness": 0.3}, "D": {"Vision": 0.8, "Boldness": 0.4}},
    13: {"A": {"Competence": 0.7, "Discipline": 0.4}, "B": {"Warmth": 0.7, "Playfulness": 0.3}, "C": {"Vision": 0.7, "Integrity": 0.4}, "D": {"Boldness": 0.7, "Sophistication": 0.3}},
    14: {"A": {"Discipline": 0.8, "Integrity": 0.4}, "B": {"Competence": 0.6, "Vision": 0.4}, "C": {"Boldness": 0.8, "Vision": 0.4}, "D": {"Playfulness": 0.6, "Sophistication": 0.4}},
    15: {"A": {"Authority": 0.7, "Integrity": 0.4}, "B": {"Vision": 0.8, "Boldness": 0.4}, "C": {"Warmth": 0.7, "Discipline": 0.4}, "D": {"Sophistication": 0.8, "Playfulness": 0.4}},
    16: {"A": {"Authority": 0.8}, "B": {"Warmth": 0.8}, "C": {"Boldness": 0.8}, "D": {"Sophistication": 0.8}, "E": {"Competence": 0.8}},
    17: {"A": {"Sophistication": 0.6}, "B": {"Authority": 0.6}, "C": {"Boldness": 0.6}, "D": {"Warmth": 0.6}, "E": {"Discipline": 0.6}},
    18: {"A": {"Authority": 0.7, "Vision": 0.3}, "B": {"Authority": 0.7, "Integrity": 0.4}, "C": {"Integrity": 0.8, "Warmth": 0.4}, "D": {"Boldness": 0.8, "Playfulness": 0.3}},
    19: {"A": {"Competence": 0.7, "Discipline": 0.4}, "B": {"Vision": 0.7, "Integrity": 0.4}, "C": {"Warmth": 0.6, "Playfulness": 0.4}, "D": {"Boldness": 0.7, "Sophistication": 0.4}},
    20: {"A": {"Authority": 0.7, "Integrity": 0.5}, "B": {"Boldness": 0.8, "Vision": 0.4}, "C": {"Warmth": 0.8, "Integrity": 0.4}, "D": {"Vision": 0.7, "Competence": 0.4}},
}

REC_ARCHETYPE = {
    "Ruler": {
        "tone": ["Puhu standardeista ja periaatteista, älä trendeistä.", "Käytä päätöskieltä; vältä liiallista selittelyä."],
        "proof": ["Sertifikaatit/auditoinnit + referenssitalot.", "SLA:t, vasteajat ja riskinpoistomekanismit."],
        "design": ["Järjestelmällinen, selkeä hierarkia, ei koristeita."],
        "cx": ["Ennustettava rytmi, selkeä omistajuus, eskalointipolku."],
        "bounds": ["Karsi asiakkuudet, joissa periaatteita ei kunnioiteta."],
    },
    "Sage": {
        "tone": ["Opeta ja määrittele; tee päätöksenteko helpoksi."],
        "proof": ["Data, benchmarkit, menetelmät ja perustelut."],
        "design": ["Selkeä informaatioarkkitehtuuri, havainnollistavat kaaviot."],
        "cx": ["Dokumentaatio ja jatkuva oppiminen osaksi toimitusta."],
        "bounds": ["Vältä hype-kieltä; pysy todennettavassa."],
    },
    "Hero": {
        "tone": ["Haasta ja kannusta; puhu voittamisesta ja vaikeista valinnoista."],
        "proof": ["Ennen–jälkeen -tulokset, kovat numerot, vaikeat caset."],
        "design": ["Selkeä ja jämäkkä; visuaalisesti energinen mutta hallittu."],
        "cx": ["Nopea reagointi, selkeät lupaukset ja tiukka toteutus."],
        "bounds": ["Älä pehmennä ydinhaastetta miellyttämisen takia."],
    },
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
    "Playfulness": ["Käytä keveyttä harkiten: selkeys ensin, vitsi vasta sitten.", "Pidä huumori brändin palvelijana, ei sen johtajana."],
}
Option = Literal["A", "B", "C", "D", "E"]

class Answer(BaseModel):
    question_id: int
    option: Option

class AssessRequest(BaseModel):
    answers: List[Answer]
    respondent_label: Optional[str] = None

class OrderRequest(BaseModel):
    company_name: str
    business_id: str
    person_name: str
    person_email: str
    billing_details: str
    primary_archetype: str
    secondary_archetype: Optional[str] = None
    shadow_archetype: Optional[str] = None
    dimensions: Dict[str, float]
    top_strengths: List[str]

def cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in DIMENSIONS)
    na = math.sqrt(sum((a.get(k, 0.0) ** 2) for k in DIMENSIONS))
    nb = math.sqrt(sum((b.get(k, 0.0) ** 2) for k in DIMENSIONS))
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

    out: Dict[str, float] = {}
    for d, v in raw.items():
        lo, hi = -10.0, 10.0
        vv = max(lo, min(hi, v))
        out[d] = (vv - lo) / (hi - lo) * 100.0
    return out

def score_archetypes(dim_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    scores = []
    for name, proto in ARCHETYPES.items():
        proto_vec = {d: float(proto.get(d, 0.0)) for d in DIMENSIONS}
        sim = cosine_similarity(dim_scores, proto_vec)
        scores.append({"key": name, "similarity": sim})
    scores.sort(key=lambda x: x["similarity"], reverse=True)
    return scores

def make_recommendations(primary: str, top_dims: List[str]) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []
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
    
    # Suomenkieliset nimet UI:lle
    primary_fi = t(primary)
    secondary_fi = t(secondary) if secondary else ""
    shadow_fi = t(shadow) if shadow else ""

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]
    top_dims_fi = [t(d) for d in top_dims]

    dim_scores_fi = {t(k): v for k, v in dim_scores.items()}

    low_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1])[:2]]

    recs = make_recommendations(primary, top_dims)

    return {
        "primary_archetype": primary_fi,
        "secondary_archetype": secondary_fi,
        "shadow_archetype": shadow_fi,
        "dimensions": dim_scores_fi,
        "archetypes": archetypes[:5],
        "top_strengths": top_dims_fi,
        "conscious_lows": low_dims,
        "recommendations": recs,
    }



# ---------------------------
# VISUAL UI (landing / survey / results)
# ---------------------------

# KORVAA koko ui_shell()-funktion <head>…</style>-osuus tällä versiolla.
# (Sisältö muuten samaksi; tämä poistaa Garamondit ja pakottaa Helvetica-tyylin + vasemman asemoinnin.)

def ui_shell(title: str, inner_html: str) -> str:
    return f"""<!doctype html>
<html lang="fi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{
      --cream: #f4e09a;
      --ink: rgba(255,255,255,0.92);
      --ink-soft: rgba(255,255,255,0.80);
      --panel: rgba(0,0,0,0.18);
    }}
    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      color: var(--ink);
      font-family: Helvetica, Arial, sans-serif; /* <-- kaikki Helvetica */
      background:
        linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0.55)),
        url('/static/bg.jpg') center/cover no-repeat fixed;
      min-height: 100vh;
    }}

    .page {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .top {{
      padding: 28px 16px 8px;
      width: 100%;
      display: flex;
      justify-content: center;
    }}

    .crest {{
      width: 54px;
      height: 54px;
      border-radius: 999px;
      display: block;
      object-fit: contain;
      filter: drop-shadow(0 6px 18px rgba(0,0,0,0.35));
    }}

    .wrap {{
      width: 100%;
      max-width: 980px;
      padding: 16px;
      display: flex;
      justify-content: center;
    }}

    /* Tämä on se “musta palikka” kaikkien sivujen tekstien taakse */
    .content-panel {{
      width: 100%;
      background: linear-gradient(180deg, rgba(0,0,0,0.88), rgba(0,0,0,0.74));
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 28px;
      padding: 56px 64px;
      box-shadow:
        0 30px 80px rgba(0,0,0,0.70),
        inset 0 0 0 1px rgba(255,255,255,0.05);
      backdrop-filter: blur(2px);
      text-align: left;                 /* <-- leipäteksti aina vasemmalta */
    }}

    /* Otsikot myös Helveticaa + sama väri kuin muu teksti */
    h1, h2, h3 {{
      font-family: Helvetica, Arial, sans-serif;  /* <-- ei Garamond */
      margin: 0 0 12px 0;
      letter-spacing: 0.2px;
      color: var(--ink);                           /* <-- sama väri kuin muu */
    }}
    h1 {{ font-size: 44px; line-height: 1.1; font-weight: 800; }}
    h2 {{ font-size: 26px; line-height: 1.2; font-weight: 800; }}
    h3 {{ font-size: 18px; line-height: 1.25; font-weight: 800; }}

    .lead {{
      margin: 0 0 26px 0;
      max-width: 720px;
      color: var(--ink-soft);
      font-size: 16px;
      line-height: 1.6;
      text-align: left; /* <-- leipäteksti vasemmalle */
    }}

    /* CTA-napit saman levyisiksi kaikkialla */
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: var(--cream);
      color: #1b1b1b;
      border: none;
      padding: 14px 26px;
      border-radius: 999px;
      font-size: 15px;
      cursor: pointer;
      text-decoration: none;
      box-shadow: 0 12px 26px rgba(0,0,0,0.25);
      min-width: 220px;   /* <-- sama leveys kuin muilla CTA-napeilla */
    }}
    .btn:active {{ transform: translateY(1px); }}

    .survey {{
      width: 100%;
    }}

    .q {{
      margin: 14px 0 18px;
      padding: 14px 12px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(0,0,0,0.12);
    }}

    .q-title {{
      font-family: Helvetica, Arial, sans-serif;  /* <-- ei Garamond */
      font-size: 18px;
      font-weight: 800;
      margin: 0 0 10px;
      color: var(--ink);
    }}

    .opt {{
      display: flex;
      gap: 10px;
      align-items: flex-start;
      margin: 8px 0;
      color: var(--ink);
      font-size: 14px;
      line-height: 1.35;
    }}

    .opt input {{
      margin-top: 3px;
      transform: scale(1.05);
    }}

    .hint {{
      font-size: 12px;
      color: var(--ink-soft);
      margin-top: 8px;
    }}

    .actions {{
      padding: 10px 0 0;
      display: flex;
      justify-content: flex-start;
    }}

    .result-grid {{
      width: 100%;
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      align-items: start;
    }}

    @media (max-width: 860px) {{
      h1 {{ font-size: 34px; }}
      .result-grid {{ grid-template-columns: 1fr; }}
      .content-panel {{
        padding: 28px 18px;
        border-radius: 18px;
      }}
      .btn {{ min-width: 200px; }}
    }}

    .card {{
      background: rgba(0,0,0,0.12);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 18px;
      box-shadow: 0 18px 40px rgba(0,0,0,0.28);
    }}

    .meta {{
      color: var(--ink-soft);
      font-size: 14px;
      line-height: 1.4;
    }}

    .list {{
      margin: 10px 0 0;
      padding: 0;
      list-style: none;
    }}

    .list li {{
      margin: 6px 0;
      font-size: 14px;
      color: var(--ink);
    }}

    .sep {{
      height: 1px;
      background: rgba(255,255,255,0.10);
      margin: 18px 0;
    }}

    label {{
      display: block;
      font-size: 13px;
      color: var(--ink-soft);
      margin: 10px 0 6px;
    }}

    input[type="text"], input[type="email"], textarea {{
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid rgba(0,0,0,0.10);
      outline: none;
      font-family: Helvetica, Arial, sans-serif;
    }}

    textarea {{ min-height: 110px; resize: vertical; }}

    .backlink {{
      color: rgba(255,255,255,0.75);
      text-decoration: none;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="top">
      <img class="crest" src="/static/crest.png" alt="Logo" />
    </div>
    <div class="wrap">
      <div class="content-panel">
        {inner_html}
      </div>
    </div>
  </div>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def ui_landing():
    inner = f"""
    <div class="hero">
      <div class="content-panel" style="max-width:720px; margin:0 auto; text-align:left;">
        <h1 style="text-align:left;">Brändikone</h1>

        <p style="font-size:16px; line-height:1.6; text-align:left;">
          Edustamasi yrityksen brändin luominen on todellisuudessa melko helppoa. Sinun tarvitsee vain:
        </p>

        <p style="font-size:16px; line-height:1.6; text-align:left;">
          1. kuvitella yrityksenne henkilöhahmoksi, jollainen halusit lapsena olla<br>
          2. muuttaa yrityksenne ulkoasu, ääni ja toiminta vastaamaan kyseistä henkilöhahmoa
        </p>

        <div style="height:24px;"></div>

        <p style="font-size:16px; line-height:1.6; text-align:left;">
          Brändikoneen avulla selvität, miltä yrityksenne henkilöhahmon, eli brändin, kannattaa näyttää, viestiä ja toimia aikuisten yritysmaailmassa.
        </p>

        <div style="height:36px;"></div>

        <div style="text-align:center;">
          <a class="btn" href="/survey">Selvitä brändihahmo</a>
        </div>
      </div>
    </div>
    """
    return ui_shell("Brändikone", inner)




@app.get("/survey", response_class=HTMLResponse)
def ui_survey():
    html = []
    html.append("<div class='survey'>")
    html.append("<h2>Kysely</h2>")
    html.append("<p class='meta'>Vastaa valinnoilla. Kohtiin joissa lukee “Valitse kaksi”, voit valita kaksi.</p>")
    html.append("<form method='post' action='/ui-assess'>")

    for q in QUESTIONS:
        qid = q["id"]
        multi = q.get("multi_select", False)
        input_type = "checkbox" if multi else "radio"
        name = f"q{qid}" if not multi else f"q{qid}[]"

        html.append("<div class='q'>")
    if qid == 0:
        html.append(f"<div class='q-title'>{q['text']}</div>")
    else:
        html.append(f"<div class='q-title'>{qid}. {q['text']}</div>")


        for opt, label in q["options"].items():
            html.append(
                f"<label class='opt'>"
                f"<input type='{input_type}' name='{name}' value='{opt}'> "
                f"<span><b>{opt}</b> {label}</span>"
                f"</label>"
            )

        if multi:
            html.append("<div class='hint'>Valitse 2</div>")

        html.append("</div>")

    html.append("""
    <div class="actions">
      <button class="btn" type="submit">Näytä tulos</button>
    </div>
    """)

    html.append("</form>")
    html.append("</div>")

    return ui_shell("Kysely", "\n".join(html))

@app.post("/ui-assess", response_class=HTMLResponse)
async def ui_assess(request: Request):
    form = await request.form()
    # Luetaan ensimmäisen kysymyksen vastaus (sukupuoli)
# A = miehiä, B = naisia, C = molempia
audience = form.get("q0", "C")

# Päätetään kuvatiedoston pääte
# Jos valittiin "naisia", käytetään naisversiota (v2w.png)
# Muuten käytetään miesversiota (v2.png)
primary_suffix = "_v2w.png" if audience == "B" else "_v2.png"


parsed: List[Answer] = []
for q in QUESTIONS:
    qid = q["id"]
    multi = q.get("multi_select", False)

    if not multi:
        val = form.get(f"q{qid}")
        if val:
            parsed.append(Answer(question_id=qid, option=val))
    else:
        vals = form.getlist(f"q{qid}[]")
        for v in vals[:2]:
            parsed.append(Answer(question_id=qid, option=v))

    dim_scores = compute_dimensions(parsed)
    archetypes = score_archetypes(dim_scores)

    primary = archetypes[0]["key"]
    secondary = archetypes[1]["key"] if len(archetypes) > 1 else None
    shadow = archetypes[-1]["key"] if len(archetypes) > 2 else None

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]

    # UI-käännökset (nämä puuttuivat sinulta -> 500-virhe)
    primary_fi = t(primary)
    secondary_fi = t(secondary) if secondary else ""
    shadow_fi = t(shadow) if shadow else ""
    top_dims_fi = [t(d) for d in top_dims]
    dim_scores_fi = {t(k): v for k, v in dim_scores.items()}

    left = []
    left.append("<div class='card'>")
    left.append(f"<h2>Pääarkkityyppi: <span>{primary_fi}</span></h2>")
    left.append(
    f"<p class='archetype-caption' style='text-align: left;'>"
    f"{ARCHETYPE_DESCRIPTIONS.get(primary, '')}"
    f"</p>"
    )
    left.append("<div class='meta'>")
    left.append(f"Toissijainen: <b>{secondary_fi}</b><br>")
    left.append(f"Varjo: <b>{shadow_fi}</b><br><br>")
    left.append(f"Top-dimensiot: <b>{', '.join(top_dims_fi)}</b><br><br>")
    left.append("</div>")

    left.append("<div class='meta'><b>Ominaisuudet (0–100)</b></div>")
    left.append("<ul class='list'>")
    for k, v in sorted(dim_scores_fi.items(), key=lambda kv: kv[1], reverse=True):
        left.append(f"<li>{k}: {v:.1f}</li>")
    left.append("</ul>")

    left.append("<div class='sep'></div>")
    left.append("<h2>Haluatko tarkemmat ohjeet brändäykseen?</h2>")
    left.append("<p class='meta'>Täytä ja lähetä alta löytyvä lomake. Saat 24h sisällä sähköpostiisi yhteistyöehdotuksen.</p>")

    left.append("<form method='post' action='/ui-order'>")
    left.append("<input type='text' name='website' style='display:none'>")

    left.append("<label>Nimesi</label>")
    left.append("<input name='person_name' required type='text'>")

    left.append("<label>Sähköpostiosoitteesi</label>")
    left.append("<input name='person_email' required type='email'>")

    left.append("<label>Yrityksenne verkkosivuosoite</label>")
    left.append("<input name='company_name' required type='text'>")


    # hidden-inputit pidetään englanniksi (lähetys ja kuvat pysyy ehjinä)
    left.append(f"<input type='hidden' name='primary_archetype' value='{primary}'>")
    left.append(f"<input type='hidden' name='secondary_archetype' value='{secondary or ''}'>")
    left.append(f"<input type='hidden' name='shadow_archetype' value='{shadow or ''}'>")
    left.append(f"<input type='hidden' name='dimensions_json' value='{json.dumps(dim_scores)}'>")
    left.append(f"<input type='hidden' name='top_strengths_json' value='{json.dumps(top_dims)}'>")

    left.append("""
    <div class="actions">
      <button class="btn" type="submit">Lähetä</button>
    </div>
    """)

    left.append("</form>")
    left.append("</div>")


    right = []
    right.append(f"""
    <div class="primary-img">
      <img src="/static/archetypes/{primary.lower()}{primary_suffix}" alt="{primary}">
    </div>
    """)

    inner = f"""
<style>
  .result-panel {{
    background: linear-gradient(180deg, rgba(0,0,0,0.85), rgba(0,0,0,0.70));
    border-radius: 28px;
    padding: 56px 64px;
    width: 100%;
    max-width: 980px;
    margin: 0 auto;
    box-shadow:
      0 30px 80px rgba(0,0,0,0.7),
      inset 0 0 0 1px rgba(255,255,255,0.05);
  }}

  @media (max-width: 860px) {{
    .result-panel {{
      padding: 28px 18px;
      max-width: 100%;
    }}
  }}

  .result-stack {{
    display: flex;
    flex-direction: column;
    gap: 28px;
    width: 100%;
  }}

  .archetype-images {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 18px;
  }}

  .archetype-text {{
    width: 100%;
  }}

  .primary-img img {{
    width: 420px;
    height: 420px;
    object-fit: cover;
    border-radius: 24px;
    max-width: 100%;
  }}

  @media (max-width: 520px) {{
    .primary-img img {{
      width: 100%;
      height: auto;
    }}
  }}
</style>

<div class="result-panel">
  <div class="result-stack">

    <div class="archetype-images">
      {''.join(right)}
    </div>

    <div class="sep"></div>

    <div class="archetype-text">
      {''.join(left)}
    </div>

    <div style="width:100%; margin-top:14px;">
      <a class="backlink" href="/survey">&larr; Takaisin kyselyyn</a>
    </div>

  </div>
</div>
        """
        return ui_shell("Tulos", inner)



# ---------------------------
# ORDER (SendGrid) + UI submit handler
# ---------------------------

@app.post("/order")
def order(req: OrderRequest):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("MAIL_FROM")
    to_email = os.getenv("MAIL_TO")

    if not api_key or not from_email or not to_email:
        return {"ok": False, "error": "Puuttuu SENDGRID_API_KEY, MAIL_FROM tai MAIL_TO (Render > Environment Variables)."}

    subject = f"Uusi brändioppaan tilaus: {req.company_name} ({req.business_id})"

    body = f"""
UUSI TILAUS / BRÄNDINRAKENNUSOPAS

Yritys: {req.company_name}
Y-tunnus: {req.business_id}

Tilaaja: {req.person_name}
Sähköposti: {req.person_email}

Laskutustiedot:
{req.billing_details}

--- TULOKSET ---

Primary: {req.primary_archetype}
Secondary: {req.secondary_archetype}
Shadow: {req.shadow_archetype}

Top-vahvuudet: {", ".join(req.top_strengths)}

Dimensiot:
{req.dimensions}
""".strip()

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/ui-order", response_class=HTMLResponse)
async def ui_order(request: Request):
    form = await request.form()

    honeypot = (form.get("website") or "").strip()
    if honeypot:
        return ui_shell("Kiitos", "<div class='hero'><h2>Kiitos</h2></div>")

    try:
        payload = OrderRequest(
            company_name=(form.get("company_name") or "").strip(),
            business_id=(form.get("business_id") or "").strip(),
            person_name=(form.get("person_name") or "").strip(),
            person_email=(form.get("person_email") or "").strip(),
            billing_details=(form.get("billing_details") or "").strip(),
            primary_archetype=(form.get("primary_archetype") or "").strip(),
            secondary_archetype=(form.get("secondary_archetype") or "").strip() or None,
            shadow_archetype=(form.get("shadow_archetype") or "").strip() or None,
            dimensions=json.loads(form.get("dimensions_json") or "{}"),
            top_strengths=json.loads(form.get("top_strengths_json") or "[]"),
        )
    except Exception as e:
        inner = f"""
        <div class="card" style="width:100%;">
          <h2>Virhe</h2>
          <p class="meta">Lomakkeen tietoja ei saatu luettua.</p>
          <pre style="white-space:pre-wrap; color:rgba(255,255,255,0.85);">{e}</pre>
          <div style="margin-top:14px;">
            <a class="btn" href="/survey">Takaisin</a>
          </div>
        </div>
        """
        return ui_shell("Virhe", inner)

    res = order(payload)

    if isinstance(res, dict) and res.get("ok"):
        inner = """
        <div class="hero">
          <h1>Kiitos!</h1>
          <p class="lead">Tilaus on lähetetty.</p>
          <a class="btn" href="/">Etusivulle</a>
        </div>
        """
        return ui_shell("Kiitos", inner)

    inner = f"""
    <div class="card" style="width:100%;">
      <h2>Virhe</h2>
      <p class="meta">Tilausta ei saatu lähetettyä.</p>
      <pre style="white-space:pre-wrap; color:rgba(255,255,255,0.85);">{res}</pre>
      <div style="margin-top:14px;">
        <a class="btn" href="/survey">Takaisin</a>
      </div>
    </div>
    """
    return ui_shell("Virhe", inner)
