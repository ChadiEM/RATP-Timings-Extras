LEN_TIME = 3

MAPPING_TEXT = {
    "Train a l'approche": "APR",
    "Train a quai": "QAI",
    "Train retarde": "RET",
    "A l'approche": "APR",
    "A l'arret": "ARR",
    "Train arrete": "TAR",
    "": "NAV",
    "NAV": "NAV",
    "UNC": "UNC"
}


def get_timings(returned_page_data):
    first_destination = returned_page_data[0]
    first_time = returned_page_data[1]
    first_time_parsed = lcd_friendly(first_time)

    second_time = returned_page_data[3]
    second_time_parsed = lcd_friendly(second_time)

    if first_time == "ARRET NON DESSERVI" and second_time == "MANIFESTATION":
        return TimingIssue("NDS - Manifestation")
    elif first_time == "INTERROMPU" and second_time == "MANIFESTATION":
        return TimingIssue("INT - Manifestation")
    elif first_time == "ARRET NON DESSERVI":
        return TimingIssue("NDS")
    elif first_time == "DEVIATION" and second_time == "ARRET NON DESSERVI":
        return TimingIssue("NDS - Deviation")
    elif first_time == "SERVICE TERMINE" or first_time == "TERMINE" or second_time == "TERMINE":
        return TimingIssue("Termine")
    elif first_time == "SERVICE NON COMMENCE" or first_time == "NON COMMENCE" or second_time == "NON COMMENCE":
        return TimingIssue("Non commence")
    elif first_time == "INFO INDISPO ...." and second_time == "INFO INDISPO ....":
        return TimingIssue("Indisponible")

    if second_time == "DERNIER PASSAGE":
        second_time_parsed = "DER"
    elif second_time == "PREMIER PASSAGE":
        second_time_parsed = "PRE"

    first_destination = friendly_destination(first_destination)

    return RegularTimings(first_destination, first_time_parsed, second_time_parsed)


def friendly_destination(text):
    text = text.replace("Porte de", "P.")
    text = text.replace("Porte d'", "P. ")
    text = text.replace("Pont de", "P.")
    text = text.replace("Pont du", "P.")
    text = text.replace("Mairie de", "M.")
    text = text.replace("Mairie d'", "M. ")
    text = text.replace("Saint", "St")
    return text


def lcd_friendly(text):
    if text in MAPPING_TEXT:
        return MAPPING_TEXT[text]
    elif text.find("mn") != -1:
        return text.replace(" mn", "m").zfill(LEN_TIME)
    else:
        return "??m"


class RegularTimings:
    def __init__(self, first_destination, first_timing, second_timing):
        self.first_destination = first_destination
        self.first_timing = first_timing
        self.second_timing = second_timing


class TimingIssue:
    def __init__(self, message):
        self.message = message
