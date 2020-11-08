import re

cardinal_pattern = re.compile("\d+\.")
date_pattern = re.compile("(\d+)\.(\d+)\.(\d+)")

def date(year,month,day):
    return "%4d-%02d-%02d" % (year, month, day)

def times2int(times):
    times = times.replace(" ","")
    if times == '':
        return None
    if times == "JP" or times == "unbesetzt" or times == "entfällt" or times == "Jackpot" or times == '--':
        return 0
    else:
        try:
            return int(times.replace("x", "").replace(".",""))
        except:
            raise Exception(times)


def german_price2float(price):
    price = price.replace(" ", "")
    if price == '':
        return None
    if price == 'unbesetzt' or price == '--':
        return None
    return float(price.replace(".", "").replace(",", "."))

def month_day(day_month_str):
    day_month = [int(i) for i in day_month_str.split(".")[0:2]]
    day = day_month[0]
    month = day_month[1]
    return month,day

def dmy_date(dmy):
    return [int(s) for s in date_pattern.match(dmy).groups()]