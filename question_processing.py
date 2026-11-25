import json
import re
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent

ALIAS_FILE = BASE_DIR / "alias.json"

ANSWER_TYPES = {
    "PERSON": "PER",
    "LOCATION": "LOC",
    "DATE": "DATE",
    "NUMBER": "NUM",
    "ORGANIZATION": "ORG",
    "RESOURCE": "RESOURCE",
    "REASON": "REASON",
    "MANNER": "MANNER",
    "DESCRIPTION": "DESCRIPTION",
    "OTHER": "MISC",
    "UNKNOWN": "UNKNOWN"
}

def load_alias():
    with open(ALIAS_FILE, "r", encoding="utf-8") as file:
        alias = json.load(file)

    return alias



from datetime import date

def normalize_question(question, alias=None):
    if alias is None:
        alias = load_alias()

    question = question.lower()
    question = re.sub(r"\s+", " ", question).strip()

    for old, new in sorted(
        alias.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = r"(?<!\w)" + re.escape(old) + r"(?!\w)"
        question = re.sub(pattern, new, question)

    bulan = {
        "01": "januari",
        "02": "februari",
        "03": "maret",
        "04": "april",
        "05": "mei",
        "06": "juni",
        "07": "juli",
        "08": "agustus",
        "09": "september",
        "10": "oktober",
        "11": "november",
        "12": "desember"
    }

    def format_tanggal(tahun, angka_bulan, tanggal):
        try:
            tanggal_valid = date(
                int(tahun),
                int(angka_bulan),
                int(tanggal)
            )

            return (
                f"{tanggal_valid.day} "
                f"{bulan[tanggal_valid.strftime('%m')]} "
                f"{tanggal_valid.year}"
            )

        except ValueError:
            return None

    def ganti_iso(match):
        hasil = format_tanggal(
            match.group(1),
            match.group(2),
            match.group(3)
        )

        return hasil if hasil else match.group(0)

    question = re.sub(
        r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)",
        ganti_iso,
        question
    )

    def ganti_tanggal(match):
        hasil = format_tanggal(
            match.group(3),
            match.group(2),
            match.group(1)
        )

        return hasil if hasil else match.group(0)

    question = re.sub(
        r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)",
        ganti_tanggal,
        question
    )

    bulan_inggris = {
        "jan": "01",
        "january": "01",
        "feb": "02",
        "february": "02",
        "mar": "03",
        "march": "03",
        "apr": "04",
        "april": "04",
        "may": "05",
        "jun": "06",
        "june": "06",
        "jul": "07",
        "july": "07",
        "aug": "08",
        "august": "08",
        "sep": "09",
        "sept": "09",
        "september": "09",
        "oct": "10",
        "october": "10",
        "nov": "11",
        "november": "11",
        "dec": "12",
        "december": "12"
    }

    def ganti_bulan_inggris(match):
        angka_bulan = bulan_inggris[match.group(2)]

        hasil = format_tanggal(
            match.group(3),
            angka_bulan,
            match.group(1)
        )

        return hasil if hasil else match.group(0)

    pola_bulan = "|".join(
        sorted(bulan_inggris.keys(), key=len, reverse=True)
    )

    question = re.sub(
        rf"\b(\d{{1,2}})\s+({pola_bulan})\s+(\d{{4}})\b",
        ganti_bulan_inggris,
        question
    )

    return question


def classify_question(question, alias=None):
    question = normalize_question(question, alias)
    question = question.lower().strip()

    if re.search(
        r"\b(tokoh|orang|pemimpin|presiden|menteri)\s+manakah\b",
        question
    ):
        return "SIAPA"

    elif re.search(
        r"\b(?:ke|di|dari)\s+"
        r"(?:kota|tempat|daerah|wilayah|lokasi)\s+manakah\b",
        question
    ):
        return "DI_MANA"

    elif re.search(
        r"\b(?:pada|sejak|hingga|sampai)?\s*"
        r"(tahun|tanggal|bulan|hari|masa|periode)\s+manakah\b",
        question
    ):
        return "KAPAN"

    elif re.search(r"\b(siapa|siapakah)\b", question):
        return "SIAPA"

    elif re.search(
        r"\b(dimana|dimanakah|"
        r"di\s+(?:\w+\s+)?mana(?:kah)?|"
        r"ke\s+(?:\w+\s+)?mana(?:kah)?|"
        r"dari\s+(?:\w+\s+)?mana(?:kah)?)\b",
        question
    ):
        return "DI_MANA"

    elif re.search(
        r"\b(kapan|sejak kapan|sampai kapan|"
        r"tanggal berapa|tahun berapa|bulan apa)\b",
        question
    ):
        return "KAPAN"

    elif re.search(
        r"\b(mengapa|kenapa|apa alasan|"
        r"atas dasar apa|untuk apa sebabnya)\b",
        question
    ):
        return "MENGAPA"

    elif re.search(
        r"\b(bagaimana|bagaimanakah|"
        r"dengan cara apa|melalui cara apa)\b",
        question
    ):
        return "BAGAIMANA"

    elif re.search(
        r"\b(berapa|berapakah|berapa banyak|"
        r"berapa jumlah|berapa besar|berapa nilai)\b",
        question
    ):
        return "BERAPA"

    elif re.search(r"\b(yang mana|manakah)\b", question):
        return "YANG_MANA"

    elif re.search(r"\b(apa|apakah)\b", question):
        return "APA"

    else:
        return "UNKNOWN"

def detect_answer_type(question, alias=None):
    question_type = classify_question(question, alias)

    answer_type_mapping = {
        "SIAPA": "PER",
        "DI_MANA": "LOC",
        "KAPAN": "DATE",
        "BERAPA": "NUM",
        "APA": "MISC",
        "MENGAPA": "REASON",
        "BAGAIMANA": "DESCRIPTION",
        "YANG_MANA": "MISC"
    }

    return answer_type_mapping.get(question_type, "UNKNOWN")

def process_question(question, alias=None):
    normalized_question = normalize_question(question, alias)
    question_type = classify_question(normalized_question, alias)
    answer_type = detect_answer_type(normalized_question, alias)

    return {
        "original_question": question,
        "normalized_question": normalized_question,
        "question_type": question_type,
        "answer_type": answer_type
    }


