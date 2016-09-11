#    if (time[0] == "ARRET NON DESSERVI" or time[0] == "MANIFESTATION"):
#        reason = time[2]
#        time = ["", "", "", ""]
#        time[1] = reason
#        time[3] = reason

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
    first_time = lcd_friendly(returned_page_data[1])

    second_destination = returned_page_data[2]
    second_time = lcd_friendly(returned_page_data[3])

    if first_destination == "ARRET NON DESSERVI":
        return TimingIssue("NDS")
    elif first_destination == "DEVIATION" and second_destination == "ARRET NON DESSERVI":
        return TimingIssue("NDS - Deviation")
    elif first_destination == "SERVICE TERMINE" or first_destination == "TERMINE" or second_destination == "TERMINE":
        return TimingIssue("Termine")
    elif first_destination == "SERVICE NON COMMENCE" or first_destination == "NON COMMENCE" or second_destination == "NON COMMENCE":
        return TimingIssue("Non commence")
    elif first_destination == "INFO INDISPO ...." and second_destination == "INFO INDISPO ....":
        return TimingIssue("Indisponible")

    if second_destination == "DERNIER PASSAGE":
        second_time = "DER"
    elif second_destination == "PREMIER PASSAGE":
        second_time = "PRE"

    first_destination = friendly_destination(first_destination)

    return RegularTimings(first_destination, first_time, second_time)


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
