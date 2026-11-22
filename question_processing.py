import json
import re
from pathlib import Path

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
    
    def ganti_tanggal(match):
        tanggal = str(int(match.group(1)))
        angka_bulan = match.group(2).zfill(2)
        tahun = match.group(3)

        if angka_bulan not in bulan:
            return match.group(0)

        return f"{tanggal} {bulan[angka_bulan]} {tahun}"

    question = re.sub(
        r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)",
        ganti_tanggal,
        question
    )

    return question


def classify_question(question, alias=None):
    question = normalize_question(question, alias)
    question = question.lower().strip()

    if re.search(r"\b(siapa|siapakah)\b", question):
        return "SIAPA"

    elif re.search(
        r"\b(dimana|dimanakah|"
        r"di\s+(?:\w+\s+)?mana(?:kah)?|"
        r"ke\s+(?:\w+\s+)?mana(?:kah)?|"
        r"dari\s+(?:\w+\s+)?mana(?:kah)?|"
        r"manakah)\b",
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


