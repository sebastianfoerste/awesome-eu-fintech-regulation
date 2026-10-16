"""Small client for CELLAR, the EU Publications Office's metadata service.

CELLAR's SPARQL endpoint records, for every EU act, its CELEX number, ELI, dates,
in-force flag and the act it is based on. Standard library only, so the workflows
need nothing beyond Python.
"""

import json
import re
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
USER_AGENT = "awesome-eu-fintech-regulation (+https://github.com/sebastianfoerste/awesome-eu-fintech-regulation)"

PREFIXES = """\
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX ann: <http://publications.europa.eu/ontology/annotation#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# The date-of-entry-into-force triples carry this pattern; the annotation says
# whether a date is the entry into force (EV) or a date of application (MA).
DATES_PATTERN = """\
    ?work cdm:resource_legal_date_entry-into-force ?date .
    OPTIONAL {
      ?annotation owl:annotatedSource ?work ;
                  owl:annotatedProperty cdm:resource_legal_date_entry-into-force ;
                  owl:annotatedTarget ?date .
      OPTIONAL { ?annotation ann:type_of_date ?date_type }
      OPTIONAL { ?annotation ann:comment_on_date ?date_comment }
    }"""

CELEX = re.compile(r"^3(?P<year>\d{4})(?P<kind>[RLD])(?P<number>\d{4,5})$")
ELI_KINDS = {"reg": "R", "dir": "L", "dec": "D"}
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def select(query, *, endpoint=ENDPOINT, timeout=60, attempts=3, wait=10):
    """Run a SPARQL SELECT and return its rows as {variable: value} dicts."""
    body = urllib.parse.urlencode({"query": query}).encode("ascii")
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    request = urllib.request.Request(endpoint, data=body, headers=headers)
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return bindings(json.load(response))
        except (OSError, ValueError) as error:
            if attempt == attempts:
                raise RuntimeError(f"CELLAR query failed after {attempts} attempts: {error}") from error
            time.sleep(wait)


def bindings(payload):
    return [{name: cell["value"] for name, cell in row.items()} for row in payload["results"]["bindings"]]


def date_kind(date_type, comment):
    """EV for entry into force, MA for application, MA/PART for partial application."""
    code = re.search(r"\{([A-Z/]+)\|", date_type or "")
    if not code:
        return ""
    if code[1] == "MA" and "{MA/PART|" in (comment or ""):
        return "MA/PART"
    return code[1]


def boolean(value):
    return {"1": "true", "true": "true", "0": "false", "false": "false"}.get(value, "")


def celex_from_eli(path):
    """reg_del/2025/1264 -> 32025R1264, for acts published from 2015 onwards."""
    match = re.match(r"^(?P<kind>reg|dir|dec)(?:_del|_impl)?/(?P<year>\d{4})/(?P<number>\d+)", path)
    if not match:
        return None
    return f"3{match['year']}{ELI_KINDS[match['kind']]}{int(match['number']):04d}"


def celex_from_citation(text):
    """'Regulation (EU) 2023/1114' -> 32023R1114; 'Directive 2014/65/EU' -> 32014L0065."""
    match = re.search(r"\b(?P<kind>Regulation|Directive|Decision)\s+(?:\((?:EU|EC|EU, Euratom)\)\s+)?"
                      r"(?P<old>No\s+)?(?P<first>\d+)/(?P<second>\d+)", text)
    if not match:
        return None
    kind = {"Regulation": "R", "Directive": "L", "Decision": "D"}[match["kind"]]
    year, number = match["first"], match["second"]
    if match["old"]:  # Regulation (EU) No 600/2014: number first, then year
        year, number = number, year
    if len(year) != 4:
        return None
    return f"3{year}{kind}{int(number):04d}"


def long_date(iso):
    """2025-10-23 -> 23 October 2025."""
    year, month, day = iso.split("-")
    return f"{int(day)} {MONTHS[int(month) - 1]} {year}"


def iso_date(text):
    """23 October 2025 -> 2025-10-23; ValueError if it is not a real date."""
    day, month, year = text.split()
    iso = f"{int(year):04d}-{MONTHS.index(month) + 1:02d}-{int(day):02d}"
    time.strptime(iso, "%Y-%m-%d")
    return iso
