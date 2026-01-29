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


# --- KÄÄNNÖSKARTTA ---

translations = {
    "Competence": "Ammattiosaaminen",
    "Integrity": "Luotettavuus / Suoraselkäisyys",
    "Authority": "Vaikutusvaltaisuus",
    "Sophistication": "Esteettisyys / Sivistyneisyys",
    "Vision": "Näkemys",
    "Discipline": "Järjestelmällisyys",
    "Boldness": "Rohkeus",
    "Warmth": "Lämpö",
    "Playfulness": "Leikkisyys",
    "Ruler": "Hallitsija",
    "Sage": "Viisas",
    "Hero": "Sankari",
    "Creator": "Luoja",
    "Explorer": "Tutkimusmatkailija",
    "Outlaw": "Kapinallinen",
    "Magician": "Taikuri",
    "Caregiver": "Hoivaaja",
    "Everyman": "Tavallinen jokamies/-nainen",
    "Lover": "Rakastaja",
    "Jester": "Narri / Viihdyttäjä",
    "Innocent": "Viaton",
}


def t(key: Optional[str]) -> str:
    if not key:
        return ""
    return translations.get(key, key)


# --- FASTAPI APP ---

app = FastAPI(title="Brand Archetype Demo", version="0.1")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


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

DIMENSIONS_FI = [t(d) for d in DIMENSIONS]

ARCHETYPE_DESCRIPTIONS = {
    "Ruler": """
    Hallitsija-brändiarkkityyppi edustaa järjestystä, kontrollia ja vastuullista johtajuutta. Se lupaa vakautta, selkeyttä ja laadukasta tuloksellisuutta. Hallitsija rakentaa luottamusta osoittamalla, että asiat ovat hallinnassa ja tavoitteet saavutetaan järjestelmällisesti ja määrätietoisesti. Visuaalisesti kyseinen brändiarkkityyppi nojaa selkeään hierarkiaan, ryhdikkääseen sommitteluun sekä arvokkuudesta, auktoriteetista ja kompetenssista viestiviin elementteihin.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy kontrollista, luotettavuudesta ja kyvystä ohjata kokonaisuuksia
    esim. johtaminen, konsultointi, valmentaminen tai mittavat riskipitoisuudeltaan korkeat hankinnat

    Ei sovi yrityksellenne:
    - jos tarjontanne keskiössä ovat vapaus, leikkisyys, kapinallisuus tai elämyksellisyys
    esim. viihde, luova itseilmaisu, nuorisobrändit ja kevyisiin lifestyle- ja hyvinvointikonsepteihin liittyvät tuotteet ja palvelut

    Tunnettuja Hallitsija-brändiarkkityypin edustajia:
    Rolex, Mercedes-Benz, IBM, Goldman Sachs ja McKinsey
    """,

    
    "Sage": """
    Viisas-brändiarkkityyppi lupaa ymmärrystä, selkeyttä ja perusteltua näkemystä. Kyseisen brändityypin missiona on auttaa ihmisiä hahmottamaan maailmaa tarkemmin, tekemään parempia päätöksiä ja perustamaan ajattelunsa tiedon varaan. Se nojaa rationaalisuuteen, kokemukseen ja luotettavuuteen viestien rauhallista asiantuntijuutta ilman tarvetta näyttävyydelle. Visuaalisesti se korostaa hillittyjä sävyjä, järjestystä, keskittymistä ja oppimista.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy ymmärryksestä, selkeydestä ja luotettavasta tiedosta 
    esim. koulutus-, tutkimus- ja asiantuntijapalvelut

    Ei sovi yrityksellenne:
    - jos tarjontanne keskiössä ovat viihteeseen, muotiin, impulssi- ja tunnepohjaiseen ostamiseen perustuvat kuluttajatuotteet

    Tunnettuja Viisas-brändiarkkityypin edustajia: 
    Britannica, TED, Harvard Business Review ja The Economist
    """,

    
    "Hero": """
    Sankari-brändiarkkityyppi lupaa voimaa, rohkeutta ja kykyä ylittää esteet. Sen missiona on aktivoida ihmiset toimintaan, vahvistaa heidän uskoaan omiin kykyihinsä ja ohjata kohti tavoitteiden saavuttamista. Sankari edustaa päättäväisyyttä, kurinalaisuutta ja sinnikkyyttä sekä viestii siitä, että menestys syntyy ponnistelun, vastuunoton ja sitkeyden kautta. Visuaalisesti se korostaa liikettä, energiaa, fyysistä ja henkistä voimaa sekä selkeää päämäärätietoista etenemistä.

    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu suorituskykyyn, itsensä kehittämiseen, kilpailullisuuteen ja tavoitteellisuuteen 
    esim. urheilu, fitness, personal training, valmennus, motivaatiosisällöt, suorituskyvyn seurantaan keskittyvät sovellukset ja tulosohjautuvat koulutusohjelmat

    Ei sovi yrityksellenne:
    - jos toimialallanne keskiössä ovat pehmeys, rauhoittuminen, introspektio tai esteettinen itseilmaisu
    esim. meditatiivinen hyvinvointi, luksuslifestyle, taidepainotteinen luovuus tai puhtaasti viihteellinen eskapismi

    Tunnettuja Sankari-brändiarkkityypin edustajia:
    Nike, Adidas, Red Bull, Under Armour ja CrossFit
    """,
    

    "Creator": """
    Luoja-brändiarkkityyppi lupaa uuden luomista, omaperäisyyttä ja kykyä muuttaa ideat konkreettisiksi tuotoksiksi. Sen missiona on rohkaista ihmisiä ilmaisemaan itseään, kehittämään omaa näkemystään ja rakentamaan jotakin aidosti uutta ja merkityksellistä. Mielikuvituksellisuutta ja rohkeaa uteliaisuutta suosiva Luoja viestii siitä, että arvo syntyy tekemisen, muotoilun ja jatkuvan kehittämisen kautta. Visuaalisesti se korostaa lämpimiä sävyjä, käsityön tuntua, luovaa prosessia ja inspiraation hetkeä, jossa idea muuttuu muodoksi.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy luovuudesta, suunnittelusta ja uuden rakentamisesta 
    esim. muotoilu, taide, käsityö, mainonta, brändäys, arkkitehtuuri, sisällöntuotanto, design-työkalut ja luovat koulutusohjelmat

    Ei sovi yrityksellenne:
    - jos toimialallanne korostuvat standardointi, tiukka sääntely, prosessien jäykkyys ja riskien minimointi 
    esim. rahoitus, vakuutusala, juridiikka tai vahvasti operatiivinen teollinen tuotanto

    Tunnettuja Luoja-brändiarkkityypin edustajia:
    Adobe, LEGO, Pixar, Apple, IDEO ja Etsy
    """,

    
    "Explorer": """
    Tutkimusmatkailija-brändiarkkityyppi lupaa vapautta, löytämistä ja mahdollisuuden kulkea omia polkuja. Sen missiona on rohkaista ihmisiä irtautumaan rutiineista, tutkimaan uutta ja laajentamaan omaa maailmankuvaansa kokemusten kautta. Tutkija edustaa itsenäisyyttä, uteliaisuutta ja avoimuutta. Se viestii siitä, että kasvu syntyy liikkeessä, kokeilun ja rajojen ylittämisen kautta. Visuaalisesti se korostaa luontoa, avaria tiloja, liikettä ja horisonttia kohti suuntaavaa katsetta.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy vapaudesta, tutkimisesta ja uusien kokemusten mahdollistamisesta 
    esim. matkailu, ulkoilu ja seikkailupalvelut, retkeilyvarusteet, lifestyle-brändit sekä koulutusohjelmat, jotka painottavat itsenäistä oppimista sekä henkilökohtaista kasvua tukevat palvelut

    Ei sovi yrityksellenne:
    - jos toimialanne keskiössä ovat tiukka kontrolli, hierarkia ja ennalta määritellyt prosessit 
    esim. rahoitus- ja vakuutusala, juridiikka tai vahvasti säännelty viranomaisviestintä

    Tunnettuja Tutkija-brändiarkkityypin edustajia:
    The North Face, Patagonia, National Geographic, Jeep, REI ja Lonely Planet
    """,

    
    "Outlaw": """
    Kapinallinen-brändiarkkityyppi lupaa vapautta, itsenäisyyttä ja rohkeutta rikkoa vallitsevia normeja. Sen missiona on kannustaa ihmisiä haastamaan auktoriteetit, kyseenalaistamaan totutut toimintamallit ja valitsemaan omat polkunsa ilman tarvetta hyväksynnälle. Kapinallinen edustaa voimaa, suoraselkäisyyttä ja tinkimätöntä asennetta sekä viestii siitä, että todellinen muutos syntyy uskalluksesta kulkea vastavirtaan. Visuaalisesti se korostaa kontrasteja, tummia sävyjä, intensiivisyyttä ja asennetta, joka huokuu riippumattomuutta ja voimaa.

    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu rohkeaan erottumiseen, normien haastamiseen ja yksilön identiteetin vahvistamiseen 
    esim. vaihtoehtomuoti, musiikki ja tapahtumat, lifestyle-brändit, haastajiksi asemoituvat startupit, sekä itsenäisyyttä ja vapautta korostavat valmennus- ja yhteisöpalvelut

    Ei sovi yrityksellenne:
    - jos toimialanne keskiössä on turvallisuus, sääntelyn noudattaminen, ennustettavuus ja institutionaalinen luottamus
    esim. pankit, vakuutusyhtiöt, julkinen sektori, terveydenhuollon kliiniset palvelut tai perinteinen koulutusjärjestelmä

    Tunnettuja Kapinallinen-brändiarkkityypin edustajia:
    Harley-Davidson, Diesel, Varusteleka
    """,

    
    "Magician": """
    Taikuri-brändiarkkityyppi lupaa muutosta, oivallusta ja kykyä nähdä mahdollisuuksia siellä missä muut näkevät rajoitteita. Sen missiona on auttaa ihmisiä ymmärtämään oma potentiaalinsa ja muuttamaan ajatteluaan, toimintaansa ja lopulta todellisuuttaan. Taikuri yhdistää visionäärisyyden, luovuuden ja järjestelmällisen ajattelun tavalla, joka tekee monimutkaisesta selkeää ja mahdottomasta saavutettavaa. Se viestii siitä, että todellinen voima syntyy ymmärryksestä ja kyvystä vaikuttaa asioiden kulkuun. Visuaalisesti Taikuri nojaa valoon, energiaan, kontrasteihin ja symboliikkaan, jotka viestivät muutoksesta, heräämisestä ja sisäisestä voimasta.

    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu muutokseen, oivalluksiin ja uusien mahdollisuuksien avaamiseen 
    esim. valmennus, coaching, itsensä kehittäminen, henkinen hyvinvointi, oppimisalustat, luovat teknologiat, AI-pohjaiset ratkaisut, brändistrategia ja innovaatiopalvelut

    Ei sovi yrityksellenne:
    - jos alallanne korostuvat puhdas rationaalisuus, ennustettavuus ja matalan riskin operatiivinen varmuus 
    esim. perinteinen pankkitoiminta, vakuutusala, juridiset palvelut, infrastruktuurihankkeet tai raskas teollisuus

    Tunnettuja Taikuri-brändiarkkityypin edustajia:
    Disney, Apple, Tesla, Google, Pixar, Mindvalley ja SpaceX.
    """,

    
    "Caregiver": """
    Hoivaaja-brändiarkkityyppi lupaa turvaa, huolenpitoa ja aitoa välittämistä. Sen missiona on tukea ihmisiä, vahvistaa heidän hyvinvointiaan ja luoda ympäristö, jossa jokainen voi tuntea olonsa turvalliseksi ja tarpeensa huomioiduiksi. Hoivaaja edustaa empatiaa, vastuullisuutta ja luotettavuutta sekä viestii siitä, että todellinen arvo syntyy toisten auttamisesta ja elämänlaadun parantamisesta. Visuaalisesti Hoivaaja nojaa pehmeisiin sävyihin, rauhalliseen tunnelmaan ja lämpimiin kohtaamisiin, jotka viestivät turvallisuudesta, läheisyydestä ja inhimillisyydestä.

    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu huolenpitoon, tukeen ja ihmisten hyvinvoinnin vahvistamiseen
    esim. terveys- ja hoivapalvelut, sosiaalipalvelut, perhe- ja lastenpalvelut, vanhustenhoito, hyvinvointialustat, tukipalvelut, koulutus ja yhteisölliset palvelut

    Ei sovi yrityksellenne:
    - jos alallanne korostuvat aggressiivinen kilpailu, kova suorituspaine tai vahvasti hierarkkinen vallankäyttö
    esim. rahoituspalvelut, korkean riskin sijoituspalvelut tai autoritääriseen johtajuuteen nojaavat organisaatiot

    Tunnettuja Hoivaaja-brändiarkkityypin edustajia:
    Johnson & Johnson, UNICEF, WWF, Dove ja Pampers
    """,

    
    "Everyman": """
    Tavallinen jokamies-brändiarkkityyppi lupaa aitoutta, läheisyyttä ja samaistuttavuutta. Sen missiona on tehdä elämästä helpompaa, rennompaa ja inhimillisempää muistuttamalla, että tavallinen arki ja yksinkertaiset ilot ovat arvokkaita. Jokamies edustaa rehellisyyttä, lämpöä ja käytännöllisyyttä. Se viestii siitä, että hyvä elämä syntyy yhteydestä toisiin ihmisiin ja tasapainosta arjen keskellä. Visuaalisesti Jokamies nojaa luonnollisiin sävyihin, pehmeään valoon ja arkisiin tilanteisiin, jotka tuntuvat tutuilta ja turvallisilta.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy lähestyttävyydestä, yhteisöllisyydestä ja arjen helpottamisesta 
    esim. vähittäiskauppa, kuluttajapalvelut, asuminen, perhepalvelut, yhteisöalustat, hyvinvointipalvelut ja työelämän peruspalvelut

    Ei sovi yrityksellenne:
    - jos alallanne korostuvat eksklusiivisuus, elitismi tai voimakas erottautuminen 
    esim. luksusbrändit

    Tunnettuja Tavallinen jokamies -brändiarkkityypin edustajia:
    IKEA, IKEA Food, Target, H&M, Dove, Airbnb ja Coca-Cola.
    """,

    
    "Lover": """
    Rakastaja-brändiarkkityyppi lupaa läheisyyttä, intohimoa ja syvää emotionaalista yhteyttä. Sen missiona on vahvistaa ihmisten kykyä kokea rakkautta, kauneutta ja merkityksellisiä ihmissuhteita sekä tuoda elämään enemmän nautintoa, lämpöä ja aitoa läsnäoloa. Rakastaja edustaa sensitiivisyyttä, esteettisyyttä ja emotionaalista avoimuutta. Se viestii siitä, että elämä on tarkoitettu koettavaksi kokonaisvaltaisesti ja tunteella. Visuaalisesti Rakastaja nojaa pehmeisiin sävyihin, lämpimään valoon, kosketukseen ja katseisiin, jotka viestivät vetovoimasta, läheisyydestä ja romantiikasta.

    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu hedonismiin 
    esim. muoti, kosmetiikka, hajuvedet, korut, sisustus, matkailu, ravintolat ja tapahtumat

    Ei sovi yrityksellenne:
    - jos alallanne korostuu tekninen rationaalisuus ja kylmä tehokkuus
    esim. raskas teollisuus, teknologia-ala, juridiset palvelut tai viranomaisviestintä

    Tunnettuja Rakastaja-brändiarkkityypin edustajia:
    Chanel, Dior, Victoria’s Secret
    """,
    

    "Jester": """
    Narri-brändiarkkityyppi lupaa iloa, keveyttä ja vapautta ottaa elämä vähemmän vakavasti. Sen missiona on tuoda arkeen huumoria, naurua ja leikkimielisyyttä sekä muistuttaa, että nautinto, spontaanius ja hetkessä eläminen ovat olennaisia osia hyvää elämää. Visuaalisesti Narri nojaa kirkkaisiin väreihin, liikkeeseen, yllätyksellisyyteen ja energiseen ilmeeseen, joka herättää välittömästi hyvän mielen.

    Sopii yrityksellenne:
    - jos tuottamanne arvo syntyy viihteen, huumorin ja elämyksellisyyden kautta 
    esim. tapahtumat, pelit, mainonta, viihdepalvelut, lasten tuotteet, juoma- ja elintarvikebrändit sekä yhteisölliset elämyspalvelut

    Ei sovi yrityksellenne:
    - jos toimialanne keskiössä on vakavien, auktoriteettien ja riskipitoisten asioiden parissa toimiville yrityksille 
    esim. rahoitus, juridiikka, terveydenhuollon kriittiset palvelut, turvallisuusala tai strateginen yritysjohtaminen

    Tunnettuja Narri-brändiarkkityypin edustajia:
    Old Spice, M&M’s, Ben & Jerry’s, TikTok, Dollar Shave Club ja Skittles
    """,

    
    "Innocent": """
    Viaton-brändiarkkityyppi lupaa toivoa, keveyttä ja yksinkertaisen onnen tunnetta. Sen missiona on tuoda elämään rauhaa, optimismia ja uskoa siihen, että hyvä on mahdollista ja lähellä. Se edustaa rehellisyyttä, lempeyttä ja vilpittömyyttä sekä viestii siitä, että elämä voi olla turvallista, kaunista ja tasapainoista. Visuaalisesti Viaton nojaa vaaleisiin sävyihin, pehmeään valoon, luonnollisuuteen ja rauhallisiin hetkiin, jotka huokuvat puhtautta ja harmoniaa.
    Sopii yrityksellenne:
    - jos tuottamanne arvo perustuu hyvinvointiin ja positiivisuuteen
    esim. terveys ja hyvinvointi, mindfulness ja stressinhallinta, lifestyle-brändit, lasten ja perheiden palvelut sekä eettiset ja kestävät brändit

    Ei sovi yrityksellenne:
    - jos toimialallanne korostuvat kyynisyys, provokaatio, aggressiivinen kilpailu tai monimutkainen valtapeli
    esim. finanssiala, poliittinen vaikuttaminen tai kapinallisuuteen nojaavat alakulttuuribrändit

    Tunnettuja Viaton-brändiarkkityypin edustajia:
    Dove, Innocent Drinks, The Body Shop 
    """

}

ARCHETYPES: Dict[str, Dict[str, float]] = {
    "Ruler": {
        "Authority": 0.95, "Discipline": 0.85, "Competence": 0.80,
        "Integrity": 0.60, "Sophistication": 0.55, "Boldness": 0.45,
        "Vision": 0.25, "Warmth": 0.15, "Playfulness": 0.05,
    },
    "Sage": {
        "Competence": 0.95, "Integrity": 0.80, "Vision": 0.65,
        "Discipline": 0.45, "Authority": 0.40, "Sophistication": 0.35,
        "Warmth": 0.20, "Boldness": 0.15, "Playfulness": 0.05,
    },
    "Hero": {
        "Boldness": 0.90, "Competence": 0.80, "Discipline": 0.70,
        "Integrity": 0.45, "Authority": 0.40, "Vision": 0.40,
        "Warmth": 0.20, "Sophistication": 0.15, "Playfulness": 0.05,
    },
    "Creator": {
        "Vision": 0.75, "Sophistication": 0.50, "Playfulness": 0.40,
        "Boldness": 0.35, "Competence": 0.25, "Integrity": 0.15,
        "Warmth": 0.15, "Authority": 0.05, "Discipline": 0.05,
    },
    "Explorer": {
        "Vision": 0.78, "Boldness": 0.73, "Competence": 0.55,
        "Integrity": 0.35, "Playfulness": 0.30, "Sophistication": 0.25,
        "Warmth": 0.20, "Discipline": 0.20, "Authority": 0.10,
    },
    "Outlaw": {
        "Boldness": 0.95, "Vision": 0.65, "Integrity": 0.45,
        "Competence": 0.45, "Authority": 0.25, "Playfulness": 0.15,
        "Sophistication": 0.10, "Warmth": 0.10, "Discipline": 0.05,
    },
    "Magician": {
        "Vision": 0.90, "Competence": 0.30, "Authority": 0.40,
        "Sophistication": 0.60, "Integrity": 0.20, "Boldness": 0.50,
        "Warmth": 0.20, "Playfulness": 0.15, "Discipline": 0.20,
    },
    "Caregiver": {
        "Warmth": 0.95, "Integrity": 0.80, "Discipline": 0.45,
        "Competence": 0.45, "Playfulness": 0.15, "Vision": 0.20,
        "Authority": 0.10, "Sophistication": 0.15, "Boldness": 0.10,
    },
    "Everyman": {
        "Warmth": 0.70, "Integrity": 0.70, "Competence": 0.50,
        "Playfulness": 0.30, "Discipline": 0.30, "Vision": 0.20,
        "Boldness": 0.15, "Authority": 0.10, "Sophistication": 0.10,
    },
    "Lover": {
        "Sophistication": 0.85, "Warmth": 0.70, "Playfulness": 0.40,
        "Integrity": 0.35, "Boldness": 0.25, "Competence": 0.25,
        "Vision": 0.20, "Authority": 0.10, "Discipline": 0.10,
    },
    "Jester": {
        "Playfulness": 0.95, "Warmth": 0.55, "Boldness": 0.35,
        "Vision": 0.25, "Competence": 0.20, "Integrity": 0.20,
        "Sophistication": 0.15, "Authority": 0.05, "Discipline": 0.05,
    },
    "Innocent": {
        "Integrity": 0.85, "Warmth": 0.70, "Discipline": 0.50,
        "Competence": 0.35, "Playfulness": 0.20, "Vision": 0.20,
        "Sophistication": 0.20, "Boldness": 0.10, "Authority": 0.10,
    },
}
    ARCHETYPE_IMAGES = {
    "Ruler": {
        "male": "/static/archetypes/ruler_v2.png",
        "female": "/static/archetypes/ruler_v2w.png",
        "neutral": "/static/archetypes/ruler_v2.png",
    },
    "Sage": {
        "male": "/static/archetypes/sage_v2.png",
        "female": "/static/archetypes/sage_v2w.png",
        "neutral": "/static/archetypes/sage_v2.png",
    },
    "Hero": {
        "male": "/static/archetypes/hero_v2.png",
        "female": "/static/archetypes/hero_v2w.png",
        "neutral": "/static/archetypes/hero_v2.png",
    },
    "Creator": {
        "male": "/static/archetypes/creator_v2.png",
        "female": "/static/archetypes/creator_v2w.png",
        "neutral": "/static/archetypes/creator_v2.png",
    },
    "Explorer": {
        "male": "/static/archetypes/explorer_v2.png",
        "female": "/static/archetypes/explorer_v2w.png",
        "neutral": "/static/archetypes/explorer_v2.png",
    },
    "Outlaw": {
        "male": "/static/archetypes/outlaw_v2.png",
        "female": "/static/archetypes/outlaw_v2w.png",
        "neutral": "/static/archetypes/outlaw_v2.png",
    },
    "Magician": {
        "male": "/static/archetypes/magician_v2.png",
        "female": "/static/archetypes/magician_v2w.png",
        "neutral": "/static/archetypes/magician_v2.png",
    },
    "Caregiver": {
        "male": "/static/archetypes/caregiver_v2.png",
        "female": "/static/archetypes/caregiver_v2w.png",
        "neutral": "/static/archetypes/caregiver_v2.png",
    },
    "Everyman": {
        "male": "/static/archetypes/everyman_v2.png",
        "female": "/static/archetypes/everyman_v2w.png",
        "neutral": "/static/archetypes/everyman_v2.png",
    },
    "Lover": {
        "male": "/static/archetypes/lover_v2.png",
        "female": "/static/archetypes/lover_v2w.png",
        "neutral": "/static/archetypes/lover_v2.png",
    },
    "Jester": {
        "male": "/static/archetypes/jester_v2.png",
        "female": "/static/archetypes/jester_v2w.png",
        "neutral": "/static/archetypes/jester_v2.png",
    },   
   "Innocent": {
        "male": "/static/archetypes/innocent_v2.png",
        "female": "/static/archetypes/innocent_v2w.png",
        "neutral": "/static/archetypes/innocent_v2.png",
    },
}
        
::contentReference[oaicite:0]{index=0}

}
for name, profile in ARCHETYPES.items():
    total = sum(profile.values())
    for k in profile:
        profile[k] = profile[k] / total

INDUSTRY_QID = 99

INDUSTRY_OPTION_TAGS = {
    "A": {"leadership", "consulting", "b2b"},
    "B": {"education", "research", "expert"},
    "C": {"creative", "design", "branding"},
    "D": {"care", "health", "wellness"},
    "E": {"consumer", "retail", "everyday"},
    "F": {"entertainment", "events", "youth"},
    "G": {"travel", "outdoor", "adventure"},
    "H": {"tech", "ai", "innovation"},
    "I": {"finance", "legal", "regulated"},
    "J": {"industrial", "infrastructure", "regulated"},
}

def compute_industry_tags(answers) -> set:
    answers_map = {}
    for a in answers:
        qid = getattr(a, "question_id", None)
        opt = getattr(a, "option", None)
        if qid is not None:
            answers_map[qid] = opt

    opt = answers_map.get(INDUSTRY_QID)
    if not opt:
        return set()

    return set(INDUSTRY_OPTION_TAGS.get(opt, set()))




# Arkkityyppien sopii ja ei sovi tagit
ARCHETYPE_INDUSTRY_RULES = {
    "Ruler": {
        "fit": {"leadership", "consulting", "b2b", "procurement", "regulated"},
        "nofit": {"entertainment", "creative", "youth", "lifestyle", "wellness"},
    },
    "Sage": {
        "fit": {"education", "research", "expert"},
        "nofit": {"entertainment", "fashion", "impulse", "hedonistic", "consumer"},
    },
    "Hero": {
        "fit": {"sport", "fitness", "coaching", "performance", "training"},
        "nofit": {"meditative", "luxury", "art", "entertainment"},
    },
    "Creator": {
        "fit": {"creative", "design", "branding", "advertising", "architecture", "content"},
        "nofit": {"finance", "legal", "industrial", "infrastructure", "regulated"},
    },
    "Explorer": {
        "fit": {"travel", "outdoor", "adventure", "lifestyle", "growth"},
        "nofit": {"finance", "legal", "regulated", "authority_comms"},
    },
    "Outlaw": {
        "fit": {"alternative", "music", "events", "challenger", "startup", "freedom"},
        "nofit": {"finance", "public", "clinical_health", "traditional_education", "regulated"},
    },
    "Magician": {
        "fit": {"coaching", "learning", "innovation", "ai", "tech", "branding"},
        "nofit": {"finance", "legal", "industrial", "infrastructure", "regulated"},
    },
    "Caregiver": {
        "fit": {"care", "health", "social", "family", "community", "education"},
        "nofit": {"finance", "high_risk_investing", "authoritarian"},
    },
    "Everyman": {
        "fit": {"retail", "consumer", "housing", "family", "community", "everyday", "wellness"},
        "nofit": {"luxury"},
    },
    "Lover": {
        "fit": {"fashion", "beauty", "fragrance", "jewelry", "interior", "travel", "restaurants", "events"},
        "nofit": {"industrial", "legal", "authority_comms", "regulated", "heavy_tech"},
    },
    "Jester": {
        "fit": {"events", "games", "advertising", "entertainment", "kids", "food", "community"},
        "nofit": {"finance", "legal", "critical_health", "security", "strategic_leadership"},
    },
    "Innocent": {
        "fit": {"health", "wellness", "mindfulness", "family", "ethical", "sustainable", "lifestyle"},
        "nofit": {"finance", "politics", "outlaw_subculture"},
    },
}

def industry_fit(archetype_name, industry_tags):
    if not industry_tags:
        return 0.5
    rules = ARCHETYPE_INDUSTRY_RULES.get(archetype_name, {})
    fit_tags = rules.get("fit", set())
    nofit_tags = rules.get("nofit", set())

    score = 0.5

    hits_fit = len(industry_tags & fit_tags)
    if hits_fit:
        score += 0.25 * hits_fit
        if score > 1.0:
            score = 1.0

    hits_nofit = len(industry_tags & nofit_tags)
    for _ in range(hits_nofit):
        score *= 0.2

    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0
    return score

QUESTIONS = [
    {"id": 0, "text": "Onko yrityksenne asiakkaista suurin osa", "options": {"A": "miehiä", "B": "naisia", "C": "molempia yhtä paljon"}},
    {"id": 1, "text": "Jos joudumme valitsemaan, haluamme että brändimme tuntuu enemmän:", "options": {"A": "Yritysten tehokkaalta työkalulta", "B": "Yritysten strategiselta suunnannäyttäjältä", "C": "Yksilöiden arkea helpottavalta kumppanilta", "D": "Yksilöiden identiteettiä vahvistavalta ilmiöltä"}},
    {"id": 2, "text": "Haluamme brändimme painottuvan enemmän:", "options": {"A": "Suorituskykyyn ja tuloksiin", "B": "Kokemukseen ja vuorovaikutukseen", "C": "Ajatteluun ja asiantuntijuuteen", "D": "Tunnesuhteeseen ja merkitykseen"}},
    {"id": 3, "text": "Kun joku kohtaa meidät, haluamme hänen ensisijaisesti kokevan:", "options": {"A": "Luottamusta organisaatioomme", "B": "Vetovoimaa tuotteeseemme/palveluumme", "C": "Kiinnostusta aatemaailmaamme kohtaan", "D": "Yhteyttä persoonaan"}},
    {"id": 4, "text": "Haluamme mieluummin, että meistä sanotaan:", "options": {"A": "Toimii aina.", "B": "Tuntuu paremmalta kuin muut.", "C": "Näyttää paremmalta kuin muut.", "D": "Ajattelee pidemmälle kuin muut."}},
    {"id": 5, "text": "Kun asiakas valitsee meidät, hänen pitäisi ensisijaisesti tuntea:", "options": {"A": "Turvaa", "B": "Ylpeyttä", "C": "Innostusta", "D": "Rauhaa"}},
    {"id": 6, "text": "Haluamme brändimme olevan mieluummin:", "options": {"A": "Auktoriteetti", "B": "Kumppani", "C": "Haastaja", "D": "Suunnannäyttäjä"}},
    {"id": 7, "text": "Valitsemme mieluummin sen:", "options": {"A": "että kaikki eivät pidä meistä", "B": "että olemme helposti lähestyttäviä", "C": "että herätämme keskustelua", "D": "että koemme harvoin vastustusta"}},
    {"id": 8, "text": "Yrityksemme on tarkoitus ennemmin:", "options": {"A": "määritellä oikea tapa", "B": "rikkoa vanha tapa", "C": "yhdistää molemmat", "D": "ohittaa koko keskustelu"}},
    {"id": 9, "text": "Valitsemme mieluummin, että ratkaisumme on:", "options": {"A": "tyylikäs", "B": "nopea", "C": "älykäs", "D": "turvallinen"}},
    {"id": 10, "text": "Haluamme yrityksemme vaikuttavan eniten:", "options": {"A": "lämpimältä", "B": "itsevarmalta", "C": "älykkäältä", "D": "ylevältä"}},
    {"id": 11, "text": "Yrityksemme tavoiteltu suhtautuminen sääntöihin:", "options": {"A": "Noudatamme niitä", "B": "Luomme niitä", "C": "Muutamme niitä", "D": "Rikomme niitä tarvittaessa"}},
    {"id": 12, "text": "Jos brändimme olisi henkilö, hän olisi ennemmin:", "options": {"A": "johtaja", "B": "ajattelija", "C": "ystävä", "D": "visionääri"}},
    {"id": 13, "text": "Haluamme että asiakkaamme muistavat meistä ensisijaisesti:", "options": {"A": "mitä me saimme aikaan", "B": "minkälaisia tunteita me herätimme", "C": "miten vaikutimme heidän ajattelutapaansa", "D": "miten uskalsimme toimia tyylillämme"}},
    {"id": 14, "text": "Valitsemme yrityksenä mieluummin:", "options": {"A": "ennustettavuuden", "B": "hallitun riskin", "C": "rohkean aseman", "D": "epämukavan erottumisen"}},
    {"id": 15, "text": "Haluamme yrityksemme toimivan ennen kaikkea:", "options": {"A": "vakauden lähteenä", "B": "muutoksen kiihdyttäjänä", "C": "turvan rakentajana", "D": "nautinnon mahdollistajana"}},

    {"id": 16, "text": "Yrityksemme haluaa olla ennen kaikkea:", "options": {"A": "Vaikutusvaltainen", "B": "Lämminhenkinen", "C": "Rohkea", "D": "Älykäs"}},
    {"id": 17, "text": "Yrityksemme estetiikka on meille:", "options": {"A": "Toissijaista", "B": "Mukavaa mutta ei kriittistä", "C": "Tärkeää", "D": "Keskeinen kilpailuetu"}},
    {"id": 18, "text": "Mieluummin meidät tunnetaan siitä, että olemme:", "options": {"A": "Turvallinen valinta", "B": "Inspiroiva valinta", "C": "Rohkea vaihtoehto", "D": "Älykäs suunnannäyttäjä"}},
    {"id": 19, "text": "Yrityksemme voima perustuu eniten:", "options": {"A": "Luottamukseen", "B": "Tunteeseen", "C": "Ideoihin", "D": "Rohkeuteen"}},
    {"id": 20, "text": "Jos jokin pitää uhrata, luovumme mieluummin:", "options": {"A": "Nopeudesta", "B": "Massasuosiosta", "C": "Mukavuudesta", "D": "Varovaisuudesta"}},
    {"id": 21, "text": "Mieluummin olemme:", "options": {"A": "Kapea ja terävä", "B": "Laaja ja turvallinen", "C": "Provosoiva", "D": "Helposti pidettävä"}},
    {"id": 22, "text": "Yritykselle vaarallisin asia olisi:", "options": {"A": "Tylsyys", "B": "Turvallisuushakuisuus", "C": "Sieluttomuus", "D": "Yltiöpäinen varovaisuus"}},
    {"id": 23, "text": "Jos jokin arvo täytyy tiputtaa, tiputamme ennemmin:", "options": {"A": "Mukavuuden", "B": "Pehmeyden", "C": "Suosion", "D": "Varman päälle pelaamisen"}},

    {"id": 24, "text": "Haluamme, että asiakas:", "options": {"A": "kuuntelee meitä", "B": "kunnioittaa meitä", "C": "luottaa meihin", "D": "toimii mallimme mukaisesti"}},
    {"id": 25, "text": "Haluamme yrityksemme olevan eniten:", "options": {"A": "ratkaisu", "B": "ajatus", "C": "kokemus", "D": "ilmiö"}},
    {"id": 26, "text": "Jos yritystämme täytyy kuvata yhdellä lauseella, valitsemme mieluiten:", "options": {"A": "Turvallinen ja vahva.", "B": "Rohkea ja erottuva.", "C": "Lämmin ja inhimillinen.", "D": "Älykäs ja näkemyksellinen."}},
    {"id": 27, "text": "Minkä haluat asiakkaan tuntevan ensikohtaamisessa brändisi kanssa?", "options": {"A": "Luottamusta ja turvallisuutta", "B": "Innostusta ja iloa", "C": "Vetovoimaa ja haluttavuutta", "D": "Kunnioitusta ja arvostusta"}},
    {"id": 28, "text": "Miten haluat brändisi näyttäytyvän suhteessa asiakkaaseen?", "options": {"A": "Läheisenä ja välittävänä", "B": "Tasavertaisena ja helposti lähestyttävänä", "C": "Leikkisänä ja piristävänä", "D": "Esteettisenä ja tunnepitoisena"}},
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
    10: {"A": {"Warmth": 0.8, "Integrity": 0.4}, "B": {"Authority": 0.7, "Discipline": 0.4}, "C": {"Competence": 0.8, "Vision": 0.3}, "D": {"Authority": 0.7, "Sophistication": 0.3}},
    11: {"A": {"Discipline": 0.7, "Integrity": 0.4}, "B": {"Authority": 0.8, "Competence": 0.4}, "C": {"Vision": 0.7, "Warmth": 0.4}, "D": {"Boldness": 0.8, "Playfulness": 0.3}},
    12: {"A": {"Authority": 0.7, "Discipline": 0.4}, "B": {"Competence": 0.7, "Integrity": 0.4}, "C": {"Warmth": 0.7, "Integrity": 0.3}, "D": {"Vision": 0.8, "Boldness": 0.4}},
    13: {"A": {"Competence": 0.7, "Discipline": 0.4}, "B": {"Warmth": 0.7, "Playfulness": 0.3}, "C": {"Vision": 0.7, "Integrity": 0.4}, "D": {"Boldness": 0.7, "Sophistication": 0.3}},
    14: {"A": {"Discipline": 0.8, "Integrity": 0.4}, "B": {"Competence": 0.6, "Vision": 0.4}, "C": {"Boldness": 0.8, "Vision": 0.4}, "D": {"Playfulness": 0.6, "Sophistication": 0.4}},
    15: {"A": {"Authority": 0.7, "Integrity": 0.4}, "B": {"Vision": 0.8, "Boldness": 0.4}, "C": {"Warmth": 0.7, "Integrity": 0.4}, "D": {"Sophistication": 0.8, "Playfulness": 0.4}},

    16: {"A": {"Authority": 0.7, "Competence": 0.4}, "B": {"Warmth": 0.7, "Integrity": 0.4}, "C": {"Boldness": 0.7, "Vision": 0.4}, "D": {"Competence": 0.7, "Vision": 0.4}},
    17: {"A": {"Discipline": 0.6, "Integrity": 0.3}, "B": {"Integrity": 0.5, "Warmth": 0.3}, "C": {"Sophistication": 0.6, "Competence": 0.3}, "D": {"Sophistication": 0.7, "Vision": 0.3}},
    18: {"A": {"Integrity": 0.7, "Discipline": 0.4}, "B": {"Vision": 0.7, "Warmth": 0.4}, "C": {"Boldness": 0.7, "Playfulness": 0.3}, "D": {"Competence": 0.7, "Vision": 0.4}},
    19: {"A": {"Integrity": 0.7, "Competence": 0.4}, "B": {"Warmth": 0.7, "Sophistication": 0.3}, "C": {"Vision": 0.7, "Competence": 0.4}, "D": {"Boldness": 0.7, "Authority": 0.3}},
    20: {"A": {"Integrity": 0.7, "Discipline": 0.4}, "B": {"Sophistication": 0.6, "Vision": 0.4}, "C": {"Boldness": 0.6, "Discipline": 0.4}, "D": {"Boldness": 0.7, "Vision": 0.4}},
    21: {"A": {"Vision": 0.6, "Competence": 0.4}, "B": {"Warmth": 0.6, "Integrity": 0.4}, "C": {"Boldness": 0.6, "Playfulness": 0.4}, "D": {"Warmth": 0.6, "Playfulness": 0.4}},
    22: {"A": {"Playfulness": 0.6, "Vision": 0.4}, "B": {"Boldness": 0.6, "Vision": 0.4}, "C": {"Warmth": 0.6, "Integrity": 0.4}, "D": {"Discipline": 0.6, "Integrity": 0.4}},
    23: {"A": {"Discipline": 0.7, "Competence": 0.3}, "B": {"Authority": 0.6, "Discipline": 0.4}, "C": {"Sophistication": 0.6, "Vision": 0.4}, "D": {"Boldness": 0.7, "Vision": 0.4}},

    24: {"A": {"Authority": 0.7, "Competence": 0.4}, "B": {"Authority": 0.7, "Sophistication": 0.3}, "C": {"Integrity": 0.8, "Competence": 0.3}, "D": {"Authority": 0.7, "Discipline": 0.4}},
    25: {"A": {"Competence": 0.7, "Integrity": 0.4}, "B": {"Vision": 0.7, "Competence": 0.4}, "C": {"Warmth": 0.6, "Playfulness": 0.4}, "D": {"Boldness": 0.7, "Vision": 0.4}},
    26: {"A": {"Integrity": 0.7, "Authority": 0.4}, "B": {"Boldness": 0.7, "Vision": 0.4}, "C": {"Warmth": 0.7, "Integrity": 0.4}, "D": {"Competence": 0.7, "Vision": 0.4}},
    27: {"A": {"Integrity": 0.7, "Discipline": 0.4}, "B": {"Playfulness": 0.7, "Boldness": 0.4}, "C": {"Sophistication": 0.7, "Warmth": 0.4}, "D": {"Authority": 0.7, "Competence": 0.4}},
    28: {"A": {"Warmth": 0.7, "Integrity": 0.4}, "B": {"Warmth": 0.6, "Integrity": 0.4}, "C": {"Playfulness": 0.7, "Warmth": 0.4}, "D": {"Sophistication": 0.7, "Warmth": 0.4}},
}


REC_ARCHETYPE = {
    "Ruler": {
        "tone": [
            "Puhu standardeista ja periaatteista, älä trendeistä.",
            "Viesti määrätietoisesti, vältä selittelyä.",
        ],
        "proof": [
            "sertifikaatit/auditoinnit, referenssit ja suosittelut",
            "kirjalliset palvelulupaukset, reagoinnin vasteajat ja riskinpoistomekanismit",
        ],
        "visuaalinen ulkoasu": [
            "järjestelmällinen, selkeä ja pelkistetty",
        ],
        "cx": [
            "ennustettava eteneminen, selkeä omistajuus, organisoitu ongelmanratkaisu",
        ],
        "bounds": [
            "Karsi asiakkuudet, joissa periaatteita ei kunnioiteta.",
        ],
    },

    "Sage": {
        "tone": [
            "Opeta ja määrittele; tee päätöksenteko helpoksi.",
        ],
        "proof": [
            "data, benchmarkit, menetelmät ja perustelut.",
        ],
        "design": [
            "selkeä informaatioarkkitehtuuri, havainnollistavat kaaviot",
        ],
        "cx": [
            "dokumentaatio ja jatkuva oppiminen",
        ],
        "bounds": [
            "Vältä maalailevaa hype-kieltä, pysy todennettavassa.",
        ],
    },

    "Hero": {
        "tone": [
            "Haasta ja kannusta, puhu voittamisesta ja vaikeista valinnoista.",
        ],
        "proof": [
            "ennen–jälkeen-tulokset, faktinen data, voitoiksi käännnetyt haastavat yhteistyöt",
        ],
        "design": [
            "selkeä ja jämäkkä, visuaalisesti energinen mutta hallittu",
        ],
        "cx": [
            "nopea reagointi, selkeät lupaukset ja tiukka toteutus",
        ],
        "bounds": [
            "Älä pehmennä ydinhaastetta miellyttämisen takia.",
        ],
    },

    "Creator": {
        "tone": [
            "Puhu luomisesta, kokeilusta ja omaperäisyydestä, vältä geneeristä ja rutiineita ylentävää kieltä.",
            "Käytä kieltä, joka kutsuu osallistumaan ja rakentamaan yhdessä.",
        ],
        "proof": [
            "ennen–jälkeen-näytteet, prototyypit ja konseptit",
            "prosessin läpinäkyvyys: miten ideat syntyvät ja jalostuvat.",
        ],
        "design": [
            "erottuva, tunnistettava visuaalinen kieli",
            "Näytä tekeminen: luonnokset, variaatiot ja järjestelmät.",
        ],
        "cx": [
            "käytännössä kehittyvä toimitus: nopeat luonnokset ja palautekierrokset",
            "vakioidut yhteiskehittämisen formaatit",
        ],
        "bounds": [
            "Älä rajaa ja standardoi luovuutta hengiltä.",
        ],
    },

    "Explorer": {
        "tone": [
            "Korosta vapautta ja uusia mahdollisuuksia.",
            "Puhu uteliaisuudesta ja oppimisesta.",
        ],
        "proof": [
            "tutkimus, testit ja näkyvät pilotit",
            "Yhteistyöt, joissa on avattu uusia markkinoita tai kanavia.",
        ],
        "design": [
            "tilava ja liikkeestä vihjaava rakenne",
            "Navigaatio, joka rohkaisee tutkimaan.",
        ],
        "cx": [
            "selkeä ja syväluotaava tutkailu ennen päätöksiä",
            "nopea kokeilukapasiteetti ja oppien dokumentointi",
        ],
        "bounds": [
            "Älä lukitse asiakasta yhteen ratkaisuun liian aikaisin.",
        ],
    },

    "Outlaw": {
        "tone": [
            "Sano ääneen, mikä nykyisessä mallissa on pielessä.",
            "Ole suorapuheinen ja kantaaottava.",
        ],
        "proof": [
            "Yhteistyöt, joissa vanhojen tapojen rikkominen on muuttunut menestykseksi.",
            "selkeät rajaukset ja kompromissien näkyväksi tekeminen",
        ],
        "design": [
            "terävä kontrasti ja vahva typografinen hierarkia",
        ],
        "cx": [
            "nopeat päätökset ja suora yhteys tekijöihin",
        ],
        "bounds": [
            "Älä laimenna sanomaa miellyttämisen vuoksi.",
        ],
    },

    "Magician": {
        "tone": [
            "Puhu muuttumisesta ja muutoksesta.",
            "Käytä rauhallista, varmaa kieltä ilman hypeä.",
        ],
        "proof": [
            "Demot ja visualisoinnit, jotka näyttävät muutoksen.",
            "Selkeä menetelmä, jolla muutos tehdään toistettavasti.",
        ],
        "design": [
            "muutoskaaren visualisointi ennen–jälkeen.",
        ],
        "cx": [
            "selkeää ja oivalluttavaa",
        ],
        "bounds": [
            "Älä lupaa ihmeitä ilman mitattavaa vaikutusta.",
        ],
    },

    "Caregiver": {
        "tone": [
            "Puhu turvasta, tuesta ja kuormituksen vähentämisestä.",
        ],
        "proof": [
            "asiakastyytyväisyys, palvelutuottamisen vasteajat ja palvelulupaukset",
        ],
        "design": [
            "rauhallinen, selkeä ja helposti luettava ilme",
        ],
        "cx": [
            "ennakoiva tuki ja selkeä vastuunjako",
        ],
        "bounds": [
            "Älä ota asiakkuuksia, joissa yhteistyö ei ole aitoa tai joita ette halua auttaa.",
        ],
    },

    "Everyman": {
        "tone": [
            "Puhu arkisesti, ole reilu ja hyvä tyyppi.",
        ],
        "proof": [
            "monipuoliset asiakasreferenssit ja laadullisen vakauden korostaminen",
        ],
        "design": [
            "tutunomainen ennustettava ukoasu ja rakenne",
        ],
        "cx": [
            "matalat riskit, helppo käyttöönotto",
        ],
        "bounds": [
            "Älä yritä olla premium tai kapinallinen samaan aikaan.",
        ],
    },

    "Lover": {
        "tone": [
            "Korosta estetiikkaa, nautintoa ja tunnetta.",
        ],
        "proof": [
            "näyttävät ja korkealaatuiset asiakasyhteistyöt ja asiakaspalaute.",
        ],
        "design": [
            "premium-henkisyys",
        ],
        "cx": [
            "henkilökohtainen ja huolellinen palvelukokemus",
        ],
        "bounds": [
            "Älä kiirehdi tai alihinnoittele laatulupausta.",
        ],
    },

    "Jester": {
        "tone": [
            "kevyt, nokkela ja inhimillinen",
        ],
        "proof": [
            "Esimerkit, joissa huumori on tuottanut tulosta.",
        ],
        "design": [
            "selkeä perusrakenne hallitulla yllätystwistillä",
        ],
        "cx": [
            "helppo vuorovaikutus ja nopea reagointi",
        ],
        "bounds": [
            "Älä käytä huumoria herkissä tilanteissa.",
        ],
    },

    "Innocent": {
        "tone": [
            "Puhu helppoudesta, turvallisuudesta ja mielenrauhasta.",
        ],
        "proof": [
            "standardit, takuut ja virheettömyysluvut",
        ],
        "design": [
            "pelkistetty, tilava ja valoisa visuaalinen kieli",
        ],
        "cx": [
            "opastettu ja ohjattu polku, sekä selkeät tarkistusvaiheet.",
        ],
        "bounds": [
            "Älä tee tarjouksesta monimutkaista.",
        ],
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


class Answer(BaseModel):
    question_id: int
    option: str


class AssessRequest(BaseModel):
    answers: List[Answer]
    respondent_label: Optional[str] = None


class OrderRequest(BaseModel):
    company_name: str
    business_id: str = ""
    person_name: str
    person_email: str
    billing_details: str = ""
    primary_archetype: str
    secondary_archetype: Optional[str] = None
    shadow_archetype: Optional[str] = None
    dimensions: Dict[str, float]
    top_strengths: List[str]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def compute_dimensions(answers: List[Answer]) -> Dict[str, float]:
    raw = {d: 0.0 for d in DIMENSIONS}
    den = {d: 0.0 for d in DIMENSIONS}

    for a in answers:
        # q0 = sukupuoli, ei vaikuta dimensioihin
        if a.question_id == 0:
            continue

        qmap = WEIGHTS.get(a.question_id, {})
        w = qmap.get(a.option, {})

        for d, val in w.items():
            v = float(val)
            raw[d] += v
            den[d] += abs(v)

    # dimensiokohtainen normalisointi (-1 … 1)
    norm = {}
    for d in DIMENSIONS:
        norm[d] = (raw[d] / den[d]) if den[d] > 0 else 0.0

    # skaalaus 0–100
    out = {}
    for d, v in norm.items():
        out[d] = (v + 1.0) / 2.0 * 100.0

    return out





    # normalisointi 0–100
    out: Dict[str, float] = {}
    for d, v in raw.items():
        lo, hi = -10.0, 10.0
        vv = max(lo, min(hi, v))
        out[d] = (vv - lo) / (hi - lo) * 100.0
    return out


# 2) MUUTA score_archetypes näin
# Etsi funktio def score_archetypes(...): ja muuta allekirjoitus ja sim lasku.

def score_archetypes(dim_scores_0_100: Dict[str, float], industry_tags: set) -> List[Dict[str, Any]]:
    dim_scores = {k: float(v) / 100.0 for k, v in dim_scores_0_100.items()}

    scores = []
    for name, proto in ARCHETYPES.items():
        proto_vec = [float(proto.get(d, 0.0)) for d in DIMENSIONS]
        user_vec = [float(dim_scores.get(d, 0.0)) for d in DIMENSIONS]

        sim = cosine_similarity(user_vec, proto_vec)

        fit = industry_fit(name, industry_tags)
        sim = sim * (0.9 + 0.1 * fit)

        scores.append({"key": name, "similarity": sim, "label": t(name), "fit": fit})

    scores.sort(key=lambda x: x["similarity"], reverse=True)
    return scores



def make_recommendations(primary: str, top_dims: List[str]) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []

    arch = REC_ARCHETYPE.get(primary, {})
    if arch:
        recs.append({"title": "Äänensävy (Tone of Voice)", "items": arch.get("tone", [])})
        recs.append({"title": "Osaamisen todistaminen", "items": arch.get("proof", [])})
        recs.append({"title": "Visuaalinen viestintä", "items": arch.get("design", [])})
        recs.append({"title": "Asiakaskokemustekijät", "items": arch.get("cx", [])})
        recs.append({"title": "Rajojen määrittely", "items": arch.get("bounds", [])})

    return recs


    # for d in top_dims:
    #     items = REC_DIMENSION.get(d, [])
    #     if items:
    #         recs.append({"title": f"Tarkennus: {d}", "items": items})



@app.get("/questions")
def get_questions():
    return QUESTIONS


@app.post("/assess")
def assess(req: AssessRequest):
    parsed = req.answers
    dim_scores = compute_dimensions(parsed)
    industry_tags = compute_industry_tags(parsed)
    archetypes = score_archetypes(dim_scores, industry_tags)


    primary = archetypes[0]["key"] if archetypes else ""
    secondary = archetypes[1]["key"] if len(archetypes) > 1 else None
    shadow = archetypes[-1]["key"] if len(archetypes) > 2 else None

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]
    recs = make_recommendations(primary, top_dims)
    low_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1])[:2]]

    recs = make_recommendations(primary, top_dims)

    return {
        "primary_archetype": t(primary),
        "secondary_archetype": t(secondary),
        "shadow_archetype": t(shadow),
        "dimensions": {t(k): v for k, v in dim_scores.items()},
        "archetypes": archetypes[:5],  # sisältää myös label-kentän
        "top_strengths": [t(d) for d in top_dims],
        "conscious_lows": [t(d) for d in low_dims],
        "recommendations": recs,
    }


# ---------------------------
# UI
# ---------------------------

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
      font-family: Helvetica, Arial, sans-serif;
      background:
        linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0.55)),
        url('/static/bg_2.jpg') center/cover no-repeat fixed;
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
    .rec-list {{
      margin: 6px 0 20px;     /* ylös tiiviimpi, alas enemmän ilmaa */
      padding-left: 18px;    
      list-style: disc;      
    }}

    .rec-list li {{
      margin: 6px 0;
      font-size: 14px;
      color: var(--ink);
    }}

    /* Väli seuraavan suositusotsikon (meta) yläpuolelle */
    .rec-list + .meta {{
      margin-top: 12px;
    }}

    /* Väli viimeisen suosituksen jälkeen ennen seuraavaa erotinta */
    .rec-list + .sep {{
      margin-top: 20px;
    }}


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
      text-align: left;
    }}
    h1, h2, h3 {{
      font-family: Helvetica, Arial, sans-serif;
      margin: 0 0 12px 0;
      letter-spacing: 0.2px;
      color: var(--ink);
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
      text-align: left;
    }}
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
      min-width: 220px;
    }}
    .btn:active {{ transform: translateY(1px); }}
    .survey {{ width: 100%; }}
    .q {{
      margin: 14px 0 18px;
      padding: 14px 12px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(0,0,0,0.12);
    }}
    .q-title {{
      font-family: Helvetica, Arial, sans-serif;
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
    @media (max-width: 860px) {{
      h1 {{ font-size: 34px; }}
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
      margin: 4px 0;
      font-size: 14px;
      color: var(--ink);
    }}
    .sep {{
      height: 1px;
      background: rgba(255,255,255,0.10);
      margin: 36px 0;
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
    .img-block {{
      margin: 10px 0 18px;
    }}

    .img-block img {{
      width: 100%;
      max-width: 720px;
      height: auto;
      border-radius: 14px;
      display: block;
      border: 1px solid rgba(255,255,255,0.10);
      box-shadow: 0 18px 40px rgba(0,0,0,0.28);
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
    inner = """
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
          Brändikoneen avulla selvität, miltä yrityksenne brändityypin kannattaa näyttää, viestiä ja toimia aikuisten yritysmaailmassa.
        </p>

        <div style="height:36px;"></div>

        <div style="text-align:center;">
          <a class="btn" href="/survey">Selvitä brändityyppinne</a>
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
    html.append("<form id='surveyForm' method='post' action='/ui-assess'>")


    for q in QUESTIONS:
        qid = q["id"]
        multi = q.get("multi_select", False)
        input_type = "checkbox" if multi else "radio"
        name = f"q{qid}" if not multi else f"q{qid}[]"

        # Kursiivi vain kysymyksille 4 ja 20
        italic = (qid in (4, 20))

        html.append("<div class='q'>")

        # Otsikko: q0 ilman numerointia, muut numerolla
        if qid == 0:
            html.append(f"<div class='q-title'>{q['text']}</div>")
        else:
            html.append(f"<div class='q-title'>{qid}. {q['text']}</div>")

        for opt, label in q["options"].items():
            text = f"<em>{label}</em>" if italic else label
            html.append(
                f"<label class='opt'>"
                f"<input type='{input_type}' name='{name}' value='{opt}'> "
                f"<span><b>{opt}</b> {text}</span>"
                f"</label>"
            )

        if multi:
            html.append("<div class='hint'>Valitse 2</div>")

        html.append("</div>")  # <-- tämä sulkee yhden kysymyslaatikon JOKA kierroksella

    html.append("""
        <div id="missingNotice" style="display:none; color:#ff4d4d; font-weight:700; margin:0 0 12px 0;">
        </div>

        <div class="actions">
          <button class="btn" type="submit">Näytä tulos</button>
        </div>
    """)
    html.append("""
    <script>
    document.getElementById("surveyForm").addEventListener("submit", function(e) {
        const notice = document.getElementById("missingNotice");
        const questions = document.querySelectorAll(".q");
        let missing = false;

        questions.forEach(q => {
            const inputs = q.querySelectorAll("input");
            const checked = Array.from(inputs).some(i => i.checked);
            if (!checked) {
                missing = true;
            }
        });

        if (missing) {
            e.preventDefault();
            notice.style.display = "block";
            notice.innerText = "Täytä kaikki kysymykset ennen tuloksiin siirtymistä.";
                notice.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    });
    </script>
    """)


    html.append("</form>")
    html.append("</div>")

    return ui_shell("Kysely", "\n".join(html))


@app.post("/ui-assess", response_class=HTMLResponse)
async def ui_assess(request: Request):
    form = await request.form()

    # A = miehiä, B = naisia, C = molempia
    audience = form.get("q0", "C")
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

    answered_ids = {a.question_id for a in parsed}
    required_ids = {q["id"] for q in QUESTIONS if q["id"] != 99}

    missing = required_ids - answered_ids
    if missing:
        return ui_shell(
            "Virhe",
            "<p style='color:#ff4444; font-weight:700;'>Vastaa kaikkiin kysymyksiin ennen tulosten näyttämistä.</p>"
    )




    dim_scores = compute_dimensions(parsed)
    industry_tags = compute_industry_tags(parsed)
    archetypes = score_archetypes(dim_scores, industry_tags)



    primary = archetypes[0]["key"] if archetypes else ""
    secondary = archetypes[1]["key"] if len(archetypes) > 1 else None
    shadow = archetypes[-1]["key"] if len(archetypes) > 2 else None

    top_dims = [k for k, _ in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]]

    primary_fi = t(primary)
    secondary_fi = t(secondary)
    shadow_fi = t(shadow)
    top_dims_fi = [t(d) for d in top_dims]
    dim_scores_fi = {t(k): v for k, v in dim_scores.items()}

    left: List[str] = []
    left.append("<div class='card'>")
    left.append(f"<h2>Pääarkkityyppi: <span>{primary_fi}</span></h2>")
    left.append(
        f"<p class='archetype-caption' style='text-align:left;'>"
        f"{ARCHETYPE_DESCRIPTIONS.get(primary, '')}"
        f"</p>"
    )
    left.append("<div class='meta'>")
    left.append(f"Toissijainen: <b>{secondary_fi}</b><br>")
    left.append(f"Varjo: <b>{shadow_fi}</b><br><br>")
    left.append(f"Huippuominaisuudet: <b>{', '.join(top_dims_fi)}</b><br><br>")
    left.append("</div>")

    # Ominaisuudet
    left.append("<div class='meta'><b>Ominaisuudet (0–100)</b></div>")
    left.append("<ul class='list'>")
    for k, v in sorted(dim_scores_fi.items(), key=lambda kv: kv[1], reverse=True):
        left.append(f"<li>{k}: {v:.1f}</li>")
    left.append("</ul>")

    # Suositukset (ilman pääotsikkoa), samaan korttiin ominaisuuksien jälkeen
    recs = make_recommendations(primary, top_dims)

    if recs:
        left.append("<div class='sep'></div>")

        for block in recs:
            title = block.get("title", "").strip()
            items = block.get("items", [])

            if title:
                # Sama “meta”-tyyli kuin ominaisuuksissa, ei h2/h3
                left.append(f"<div class='meta' style='margin-top:14px;'><b>{title}</b></div>")

            if items:
                # Suosituksille oma listaluokka, jotta pallurat saadaan näkyviin
                left.append("<ul class='rec-list'>")
                for item in items:
                    left.append(f"<li>{item}</li>")
                left.append("</ul>")
                
        # --- Brändiarkkityypin perusväripaletti + websivu-esimerkki ---
    # Kuvien nimet: /static/archetypes/{primary_lower}_cp.png ja /static/archetypes/{primary_lower}_ws.png
    # Esim: ruler_cp.png, ruler_ws.png

    primary_lower = primary.lower()

    left.append("<div class='sep'></div>")
    left.append("<div class='meta'><b>Ehdotus brändiarkkityypin perusväripaletiksi</b></div>")

    left.append(
        f"<div class='img-block'>"
        f"  <img src='/static/archetypes/{primary_lower}_cp.png' "
        f"       alt='{primary} color palette' loading='lazy'>"
        f"</div>"
    )

    left.append("<div class='meta'><b>Esimerkki värien hyödyntämisestä verkkosivulla</b></div>")

    left.append(
        f"<div class='img-block'>"
        f"  <img src='/static/archetypes/{primary_lower}_ws.png' "
        f"       alt='{primary} website example' loading='lazy'>"
        f"</div>"
    )


    left.append("<div class='sep'></div>")
    left.append("<h2>Huolitko apua ammattilaiselta?</h2>")

    left.append("<p class='meta'>Jos vastasit myöntävästi, ja koet tarvitsevasi apua yrityksenne brändäyksessä, markkinointiviestinnässä tai luovassa ideoinnissa, täytä ja lähetä alla oleva lomake. Otamme sinuun yhteyttä sähköpostitse 24h sisällä.</p>")

    left.append("<form method='post' action='/ui-order'>")
    left.append("<input type='text' name='website' style='display:none'>")

    left.append("<label>Nimesi</label>")
    left.append("<input name='person_name' required type='text'>")

    left.append("<label>Sähköpostiosoitteesi</label>")
    left.append("<input name='person_email' required type='email'>")

    left.append("<label>Yrityksenne verkkosivuosoite</label>")
    left.append("<input name='company_name' required type='text'>")

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

    right: List[str] = []
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

    <div class="archetype-text" style="white-space: pre-line; font-size: 16px;">
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

    subject = f"Uusi brändioppaan tilaus: {req.company_name} ({req.business_id})".strip()

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
