import re

cardinal_pattern = re.compile("\d+\.")

def date(year,month,day):
    return "%4d-%02d-%02d" % (year, month, day)

def times2int(times):
    times = times.replace(" ","")
    if times == '':
        return None
    if times == "JP" or times == "unbesetzt" or times == "entfällt" or times == "Jackpot":
        return 0
    else:
        try:
            return int(times.replace("x", "").replace(".",""))
        except:
            raise Exception(times)


def german_price2float(price):
    if price == '':
        return None
    if price == 'unbesetzt':
        return None
    return float(price.replace(".", "").replace(",", "."))

def month_day(day_month_str):
    day_month = [int(i) for i in day_month_str.split(".")[0:2]]
    day = day_month[0]
    month = day_month[1]
    return month,day