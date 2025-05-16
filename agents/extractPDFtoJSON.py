import fitz  # PyMuPDF
import json
import re
import os
from pathlib import Path
from haystack import Document



def extract_section(text, start_marker, end_marker=None):
    start = text.find(start_marker)
    if start == -1:
        return ""
    if end_marker:
        end = text.find(end_marker, start)
        return text[start:end].strip() if end != -1 else text[start:].strip()
    return text[start:].strip()

def extract_field(text, label, following_label=None):
    pattern = rf"{label}\s*(.*?)(?=\n{following_label}|$)" if following_label else rf"{label}\s*(.*)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_detailed_chunks(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
#'wieland crm \n \n20. Mar. 2025 \nVisit Report \n \nAccount \n \nChocoLuxe GmbH \nParkstraße 33 / 86021 / Kassel / DE \nAccount ID                     50000762185 \nLast Visit                         26.Jan.2025 \nSBU                            Chocolate bars \nCustomer segment   - \nPayment terms   14 days after date of invoice, net \n \nDate \n26. Jan. 2025  \nLocation \nWerk Vöhringen \nSubject \nNeukunde ChocoLuxe – Projekt SchokoGigant \nOwner \nAndreas Becker \nAttendees \n- \nAndreas Becker (PR.CHOC) \n- \nAndreas Novak (Einkaufsabteilung; Abteilungsleiter) \n- \nLisa Reed (Einkaufsabteilung: Head of Supply Chain) \n- \nRafaela Costa \n- \nSven Eriksson (Einkaufsabteilung; Sachbearbeiter ID) \n- \nMiguel Petrov (Testing) \n \n \nVisit Type \nBusiness Initiation \n \n \nResult \n \n- Gemeinsame Realisierung SchokoGigant-Projekt vereinbart (Lohnröstung BestChocolate) \n- Kakaobeschaffung ab Mitte 2025 soll auf BestChocolate umgestellt werden  \n- Termin Besuch in Kassel zum allgemeinen Ausbau der Geschäftsbeziehung vereinbaren \n \n \n \n\nwieland crm \n \n20. Mar. 2025 \n \nExecutive Summary \n \n- Technische Hintergründe geklärt \n- Herausforderungen Anlieferungen (Online-Avisierung) geklärt \n- Standards bezüglich Ladungssicherung / Verpackung fixiert (ToDo Kunde) \n- Hochlauf + Start der Serien-Röstungen ab April 2025 vorgesehen \nReport \n \nBUSINESS SITUATION OF THE CUSTOMER AND GENERAL INFORMATION \n- Zuletzt zahlreiche Projekte in der Lebensmittelindustrie durch ChocoLuxe konkretisiert \n- Ausblick und Geschäftsverlauf nach herausfordernden Jahren wieder positiv \nMARKET ENVIRONMENT OF THE CUSTOMER \nDie ChokoLuxe GmbH mit Sitz in Kassel ist ein führender Hersteller von hochwertigen \nSchokoladenprodukten und bietet Lösungen für die Süßwarenindustrie. Das Unternehmen \nist auf die Entwicklung und Produktion von Groß-, Mittel- und Kleinserien von Schokoladen, \nsowie auf speziell veredelte Schokoladenprodukte spezialisiert.  \nDurch allgemein ansteigende Investitionen in die Lebensmittelindustrie und innovative \nSüßwaren erweitern sich die Einsatzfelder der Produkte.  \nAllgemeine Nachfrage aktuell sehr gut. \nDEMAND, GB´s SHARE OF DEMAND, COMPETITION \n- Kakaobeschaffung ChocoLuxe läuft aktuell im Schwerpunkt über Handel  \n- Parallele Geschäftsanbahnung Firma Faller (CH) als Zulieferer an ChocoLuxe (Kakao über \nBestChocolate) \nPOTENTIAL FOR FURTHER BUSINESS / NEW PROJECTS \n- Aktuelles Projekt für SchokoGigant-Konzern \n- Einsatz Schokoladenriegel für Großveranstaltungen (Investitions-Offensive für Events und \nFeiern) \n- Kakaobeschaffung lief zuletzt über Handel, Umstellung auf BestChocolate angestrebt \n(gesonderte Verhandlung) \n- Zulieferer Fa. Tramer + Fa. Schlinger werden gesondert kontaktiert \n(Update 20.02. Erste Auslieferung Schokoriegel an Fa. Tramer, Qualifizierung erfolgt) \n \n \n\nwieland crm \n \n20. Mar. 2025 \n \nCURRENT TOPICS \nChocoLuxe wünscht Lohn-Röstungen von Kakaobohnen für Schokoladenriegel (Endkunde \nSchokoGigant-Konzern) \nParameter und Qualifizierung nach erstem Röstvorgang erfolgreich bestanden \nFestgelegtes Programm "1h - 325°C" bringen gewünschten Effekt \nProjekt-Hochlauf ab April geplant, dann ca. 7 Röstungen pro Monat (DB3Ge pro Röstung \n1.900 €) \nProjekt-Rahmen für 2025: ca. 40 Röstungen // Laufzeit aktuell bis Ende 2026 geplant  \n \n1 Röstung = 12 Ausleitungen Variante 1 + 12 Ausleitungen Variante 2 \n \nUpdate 10.03.2025: Forecast + Time-Line wird finalisiert und an BestChocolate kurzfristig \nkommuniziert \nAuftrag für Röstung SchokoGigant erhalten - 2 Ofen-Ladungen = 40 Ausleitungen \n(11.03.2025) (Zwei Ausleitungstypen in gleicher Menge) \nDiese Röstungen gehören zur Phase 1 (Hochlauf Projekt) und sind nicht in angehängter \nTime-Line enthalten. \nFURTHER TOPICS / CUSTOMER SATISFACTION \nToDos: \n- Übermittlung der Anforderungen Ladungssicherung + Verpackung  \n- Fragestellungen + Anforderungen mit Kunden klären (erl. / Gesonderte Info an PR.CHOC)  \n \nMarket/Business Trends \n \nSurvey Name \nQuestion \nAnswer \nCustomer satisfaction \nQUALITY OF OUR PRODUCTS \nDELIVERY RELIABILITY \nSERVICE \nVery good \nVery good \nVery good \n \n \n\nwieland crm \n \n20. Mar. 2025 \n \n \nAttachment \n \nAlternative Title \nDocument Type \nVisit Report - ChocoLuxe GmbH – 26.01.2025.pdf \nZusammenfassung \nÜbersicht_Zeitplan_SchokoGigant.xlsx \nStandardanlage \n \n'
    chunks = {}
#'Wieland crm \n \n04. Mar. 2025 \nVisit Report \n \nAccount  \nCHOCO AG  \nBlumberg 51 – 56 / 5041 MC Den Haag / NL \nAccount ID                             4000067895 \nLast Visit                                 14.09.2024 \nSBU                               Großhändler Schokoriegel \nCustomer Segment           A3 \nPayment Terms      30 days after date of invoice, net \n \nDate \n25. Feb. 2025 \nLocation \nDen Haag \nSubject \nGemeinsame Kundenbesuche (Van White, ABC, KAKAO); Status mehrerer \nThemen \nOwner \nMats Müller \nAttendees  \n- \nMats Müller (PR.CHOC) \n- \nAndreas Mayer (Produktmanager) \n- \nHans van der Tri (Verkaufsabteilung, Abteilungs-/Berichtsleiter) \n- \nSven van Hey (Verkaufsabteilung, Sachbearbeiter AB) \n- \nBrian Kert (Einkaufsabteilung) \n- \nPatrizia Wörtz (Teamleiter/Meister) \n \n  Customer Support \n \n \n \n \nResult \n \nNachdem die aktuell laufenden Projekte abgeschlossen sind und mit den jüngsten Informationen \nvon der Schokoladenmesse in Frankfurt, werden wir eine Strategie und Vorgehensweise erarbeiten, \nwelche es möglich machen sollten, die Kunden der EGF anzugehen. CHOCO AG ist bereits heute \ngewillt Crispy als zweite Marke mit in Ihr Lagerprogramm aufzunehmen um EGF Bestandskunden \nbesser abwerben zu können und im zweiten Schritt die Marke Creamy dort einzuführen. \nExecutive Summary \n \nAuf dieser Reise wurden mehrere Kunden besucht, nachdem wir unseren Kunden Anfang Februar \ninformiert haben, dass CHOCO AG und BestChocolate nun enger zusammenarbeiten. Die \nZusammenarbeit wurde durchwegs positiv aufgenommen und die Kunden erfreuten sich an den \nneuen Möglichkeiten, wie z.B. Lagerhaltung, verkürzte Lieferzeiten und kleinere Liefermengen. \n \nVisit Type \n\nWieland crm \n \n04. Mar. 2025 \nReport \n \nBUSINESS SITUATION OF THE CUSTOMER AND GENERAL INFORMATION \nKAKAO:  \nIst bereits ein Kunde von CHOCO AG mit Mayer Schokoriegeln, wir haben Creamy vorgestellt und \ndie Belieferung in Zukunft besprochen. KAKAO ist vom Produkt und der Idee der Nachhaltigkeit \nangetan und wird sich im Nachgang mit CHOCO AG  über die Konditionen und einen potenziellen \nWechsel unterhalten. \nVan White: \nVan White ist heute bereits Kunde bei CHOCO AG für weiße Schokoriegel und dunkle Schokoriegel. \nBestChocolate lieferte bisher immer Crispy Qualität (ca. 60 Jato). Der Gesamtbedarf an Vollmilch \nSchokoriegeln betrug 2024 rund 160to, davon werden 80to via Firma Walter von SchokoTraum \nbezogen. Mit der Einführung von Creamy und der Abkündigung mehrerer Lagerabmessungen an \nCrispy, hat sich D.F. still auf den Weg gemacht mit EGF Gespräche zu führen und auch schon eine \nerste Bestellung im Februar dort platziert. Beim Besuch haben wir unseren Unmut gezeigt, dass wir \nals jahrelange Partner und Lieferanten weder über den Unmut des Markenwechseln unseres \nLagerprogrammes informiert wurden, noch ein drohender Wechsel zu EGF mit entsprechender \nNachbesserungsmöglichkeit angesprochen wurde. Der Kunde bedauert dies, jedoch seien die EGF \nPreise deutlich günstiger und zudem gehöre D.F. nun einem Einkaufsverband für Schokoriegeln an \n(AKB Group) welcher Beziehungen zu EGF unterhält (Konzernbonus). Als nächster Schritt wird \nCHOCO AG ein Angebot an Van White unterbreiten (Crispy, Creamy inklusive Lagerhaltung) \nwelches auf den Gesamtbedarf von 160to abzielt, mit dem Minimalziel die Mengen bei \nBestChocolate zu halten. Ein weiteres Treffen auf der Schokoladenmesse wurde vereinbart. \nABC \nDas Treffen mit ABC fand am Standort von CHOCO AG in Den Haag statt. ABC ist ein Neukunde für \nCHOCO AG welcher heute seine Vollmilch Schokoriegel (rund 40 JaTo) von SchokoTraum bezieht. \nDie Abmessungen teilen sich auf in 22x1,1 und 28x1,2 in weichen Riegel, leider liegt uns aktuell \nkeine KIWA Zertifizierung der 28mm weichen Riegel vor, daher wird mit Nachdruck an einer \nZulassung der Abmessung gearbeitet. Falls dies nicht gelingt, werden die Riegel weiter von \nSchokoTraum bezogen bis CHOCO AG/BestChocolate lieferfähig ist. \nDEMAND, GB´s SHARE OF DEMAND, COMPETITION \nDer Gesamtmarkt an Schokoriegeln in Holland liegt bei rund 4.000 to. CHOCO AG vertreibt rund \n2.000 to, SchokoTraum wird auf 600 to geschätzt, die restlichen 1.400 to werden bei der EGF \ngesehen. EGF hat einen Außendienstmitarbeiter in NL. Hauptabnehmer von EGF sind sicherlich die \nbekannten Großhändler (Pflüger, Bar Family und Thomas‘) \nCURRENT TOPICS \nReklamation EasyChoc, AG: \nCHOCO AG hätte gerne den aktuellen Lagerbestand (rund 11,5to) an kundenspezifischen Riegeln \nfür den Endkunden EasyChoc kontrolliert und nachgereinigt, nachdem der Endkunde bereits 2 \nChargen aus dieser Lieferung reklamiert hatte. \n\nWieland crm \n \n04. Mar. 2025 \nVegane Riegel Spot Geschäft nach Südamerika: \nCHOCO AG unterhält Kontakte nach Südamerika und vertreibt dort seit diesem Jahr auch unsere \nVeganen Riegel. Aktuell laufen rund 15to Aufträge aus Lager. Für eine bessere \nLagernachdisponierung wurden die geschätzten Bedarfe für 2025 je Druckstufe eingeholt (60Jato \ngesamt). \nKurzlängen Interschoko: \nSven betreut Interschoko auf Seiten CHOCO AG und hat kürzlich die Jahresanfrage über 360 to \nKurzlängen erhalten. Wir haben in der Zwischenzeit ein Angebot abgegeben und die Rückmeldung \nvon Seitens Interschoko steht Stand heute noch aus. \nMarket/Business Trends \n \nSurvey Name \nQuestion \nAnswer \nCustomer satisfaction \nQUALITY OF OUR PRODUCT \nVery good \n \nDELIVERY RELIABILITY \nRather good \n \nSERVICE  \nVery good \n \nDemands \n \nDivision \nProduct Grp \nProduct \nType \nQuantity \nBestChocolate \nPR.CHOC \nBars \nChocolate bars \nwhite \n150.000,00 kg \n0,00% \nPR.CHOC \nBars \nChocolate bars \nmilk \n1.000.000,00 kg \n50,00% \nPR.CHOC \nBars \nChocolate bars \ncaramel \n500.000,00 kg \n0,00% \nPR.CHOC \nBars \nChocolate bars \ndark \n60.000,00 kg \n0,00% \n \n'
    # Extract individual fields
    chunks["Metadata"] = text.split("Visit Report")[0].strip()
    chunks["Account Info"] = extract_field(text, "Account", "Account ID")
    chunks["Account ID"] = extract_field(text, "Account ID", "Last Visit")
    chunks["Last Visit"] = extract_field(text, "Last Visit", "SBU")
    chunks["SBU"] = extract_field(text, "SBU", ["Customer Segment", "Payment Terms"])
    chunks["Customer Segment"] = extract_field(text, "Customer Segment", "Payment Terms")
    chunks["Payment Terms"] = extract_field(text, "Payment terms", "Date")
    chunks["Date"] = extract_field(text, "Date", "Location")
    chunks["Location"] = extract_field(text, "Location", "Subject")
    chunks["Subject"] = extract_field(text, "Subject", "Owner")
    chunks["Owner"] = extract_field(text, "Owner", "Attendees")
    chunks["Attendees"] = extract_field(text, "Attendees", "Visit Type")
    chunks["Visit Type"] = extract_field(text, "Visit Type", "Result")

    # Extract block sections
    chunks["Result"] = extract_section(text, "Result", "Executive Summary")
    chunks["Executive Summary"] = extract_section(text, "Executive Summary", "Report")
    chunks["Business Situation"] = extract_section(text, "BUSINESS SITUATION OF THE CUSTOMER AND GENERAL INFORMATION", "MARKET ENVIRONMENT OF THE CUSTOMER")
    chunks["MARKET ENVIRONMENT"] = extract_section(text, "MARKET ENVIRONMENT OF THE CUSTOMER", "DEMAND, GB´s SHARE OF DEMAND, COMPETITION")

    chunks["Demand Info"] = extract_section(text, "DEMAND, GB´s SHARE OF DEMAND, COMPETITION", "POTENTIAL FOR FURTHER BUSINESS / NEW PROJECTS")
    chunks["POTENTIAL"] = extract_section(text, "POTENTIAL FOR FURTHER BUSINESS / NEW PROJECTS", "CURRENT TOPICS")
    chunks["Current Topics"] = extract_section(text, "CURRENT TOPICS", "FURTHER TOPICS / CUSTOMER SATISFACTION")
    chunks["Further Topics"] = extract_section(text, "FURTHER TOPICS / CUSTOMER SATISFACTION", "Market/Business Trends")
    chunks["Market Trends"] = extract_section(text, "Market/Business Trends", "Demands")
    chunks["Demands"] = extract_section(text, "Demands", None)
    print(text)
    return chunks


### Utils ###
def listFromJson(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # data is a dict

    # Convert dict values to a list (e.g., all chunks)
    chunks_list = [f"{key} : {value}" for key, value in data.items()]
    return chunks_list

def extract_text_from_JSON(path):
    # Load the JSON file
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # This will be a dictionary

    # Convert to a single concatenated string (including keys)
    concatenated_string = "\n\n".join(
        f"{key}:\n{value}" for key, value in data.items())
    return concatenated_string


def loadChunksFromJson(directory: str = "data/reports/json") -> list[Document]:
    directory = "data/reports/json"
    docs = []
    for path in Path(directory).iterdir():
        if not path.is_file():
            continue
        """    
        raw = (
            extract_text_from_JSON(str(path))
            if path.suffix.lower() == ".json"
            else path.read_text(encoding="utf-8", errors="ignore")
        )

        # split on blank lines (paragraphs)
        paras = [p.strip() for p in raw.split("\",") if p.strip()]
        for para in paras:
            docs.append(Document(content=para, meta={"source": path.name}))
        """
        chunksFromJson = listFromJson(str(path))    
        for itemFromJson in chunksFromJson:
            docs.append(Document(content=itemFromJson, meta={"source": path.name}))
            
    return docs

def main():
    #pdf_path = os.path.join("..", "data","reports", "VisitReport_Fantasiefirma.pdf")
    pdf_path = "D:\BVC-Project/data/reports/Visit Report_4.pdf"  # Adjust path if needed
    chunks = extract_detailed_chunks(pdf_path)

    # Save to JSON
    with open("./data/reports/visit_report_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("✅ Data saved to visit_report_chunks.json")
    return returnAsString()
    
# Run this part
if __name__ == "__main__":
    main()
