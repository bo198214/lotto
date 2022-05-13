import argparse
import re
import csv
from math import floor, fabs

from lotto import times2int, german_price2float, month_day

parser = argparse.ArgumentParser(description='Read Lotto Numbers from year')

# parser.add_argument('year', help='The year of the data')

args = parser.parse_args()

cardinal_pattern = re.compile("\d+\.")


def time_out():
    return "%4d-%02d-%02d" % (year, month, day)



def print_tippschein(numbers):
    for i in range(7):
        print("|",end="")
        for j in range(7):
            if 7 * i + j + 1 in numbers:
                print("x",end="")
            else:
                print(" ",end="")
        print("|")
# prices:
# : 0.5 DM
# : 1 DM
# since 49/1991: 1.5 DM
# since 01.01.2002: 0.75 EUR, nur Superzahl
# since 01.05.2013: 1 EUR, Zusatzzahl+Superzahl
# since 23.09.2020: 1.20 EUR

# year = int(args.year)


def adjust_cat_perc_nojackpot(cat_perc, category_hits, single_limit):
    if category_hits[0] == 0:
        cat_perc[1] += cat_perc[0]
        cat_perc[0] = 0.0
    # elif category_hits[0] == 0 and category_hits[1] == 0:
    #     cat_perc[2] += cat_perc[0] + cat_perc[1]
    else:
        if single_limit is None:  # since (1985,6,1)
            pass
            # sc = (cat_perc[1] + cat_perc[0])
            # rp = cat_perc[0] / sc
            # a = max(category_hits[0] / (category_hits[0] + category_hits[1]), rp)
            # cat_perc[0] = sc * a
            # cat_perc[1] = sc * (1 - a)
        else:
            if (year, month, day) >= (1962, 10, 7):
                # cat[1] is a real category
                if cat_perc[0] * spiel_einsatz / category_hits[0] > single_limit:
                    cat_perc[0] = single_limit * category_hits[0] / spiel_einsatz
                    cat_perc[1] = 0.0
                else:
                    sc = (cat_perc[1] + cat_perc[0])
                    rp = cat_perc[0] / sc
                    a = max(category_hits[0] / (category_hits[0] + category_hits[1]), rp)
                    cat_perc[0] = sc * a
                    cat_perc[1] = sc * (1 - a)
            elif (year, month, day) >= (1956, 10, 21):
                # limit sinlge_pay is 5000000, cat[1] is replacement if cat[0] has 0 hits or above 500000
                cat0 = cat_perc[0] + cat_perc[1]
                if cat0 * spiel_einsatz / category_hits[0] > single_limit:
                    cat_perc[0] = single_limit * category_hits[0] / spiel_einsatz
                else:
                    cat_perc[0] = cat0
                    cat_perc[1] = 0.0
            elif (year, month, day) >= (1956, 6, 17):
                if category_hits[1] == 0:
                    cat_perc[0] += cat_perc[1]
                    cat_perc[1] = 0.0

    return cat_perc


def adjust_cat_perc(cat_perc,category_hits):
    if category_hits[0] > 0:
        if category_hits[1] == 0:
            cat_perc[0] += cat_perc[1]
            cat_perc[1] = 0.0
        else:
            if (year, month, day) >= (2013, 5, 4):
                pass
            sc = (cat_perc[1] + cat_perc[0])
            rp = cat_perc[0] / sc
            cat0_ratio = category_hits[0] / (category_hits[0] + category_hits[1])
            cond = cat0_ratio >= rp
            if year >= 1992:
                cond = category_hits[0]/category_hits[1] in [1/2,1/1]
            if year >= 1993:
                cond = category_hits[0]*1 > category_hits[1]*1
            if year >= 1994:
                cond = cat0_ratio >= rp
            if cond:
                a = cat0_ratio
                cat_perc[0] = sc * a
                cat_perc[1] = sc * (1 - a)
    return cat_perc


def process():
    global JP
    global jp_accu
    if (year, month, day) >= (2020, 9, 23):
        single_spiel_einsatz = 1.2
    elif (year, week) >= (2013, 18):  # ?ab 4. Mai
        single_spiel_einsatz = 1.0
    elif year >= 2002:
        single_spiel_einsatz = 0.75  # EUR
    elif (year, week) >= (1999, 20):  # ?
        single_spiel_einsatz = 1.5
    elif (year, month, day) >= (1991, 12, 14):
        single_spiel_einsatz = 1.25  # DM
    elif (year, week) >= (1984, 18):  # nach 28.4.?
        single_spiel_einsatz = 1.0  # DM
    elif (year, week) >= (1981, 27):
        single_spiel_einsatz = 0.5
    else:
        single_spiel_einsatz = 0.5  # DM

    teilnehmer = spiel_einsatz / single_spiel_einsatz
    if not teilnehmer-floor(teilnehmer) < 0.0000001:
        print("Warning:",time_out(), str(spiel_einsatz) + "/" + str(single_spiel_einsatz) + "=" + str(teilnehmer))

    auszahlungen = sum([category_hits[i] * category_single_pay[i] for i in range(len(categories) // 2)])

    if (year, week) >= (1999, 20):
        cat0_prob = 1/139838160
        hits = [
            category_hits[0] +  # 6 Richtige und Superzahl
            category_hits[1],  # 6 Richtige
            category_hits[2] +  # 5 Richtige und Zusatzzahl
            category_hits[3],  # 5 Richtige
            category_hits[4] +  # 4 Richtige und Zusatzzahl *
            category_hits[5],  # 4 Richtige
            category_hits[6] +  # 3 Richtige und Zusatzzahl
            category_hits[7]  # 3 Richtige
        ]
    elif (year, month, day) >= (1991, 12, 7):
        cat0_prob = 1/139838160
        hits = [
            category_hits[0] +  # 6 Richtige und Superzahl *
            category_hits[1],  # 6 Richtige
            category_hits[2] +  # 5 Richtige und Zusatzzahl
            category_hits[3],  # 5 Richtige
            category_hits[4],  # 4 Richtige
            category_hits[5] +  # 3 Richtige und Zusatzzahl *
            category_hits[6]  # 3 Richtige
        ]
    elif (year, week) >= (1956, 37):
        cat0_prob = 1/13983816
        hits = [
            category_hits[0],  # 6 Treffer
            category_hits[1] +  # 5 Treffer + Zusatzzahl *
            category_hits[2],  # 5 Treffer
            category_hits[3],  # 4 Treffer
            category_hits[4]  # 3 Treffer
        ]
    else:  # before 1956
        cat0_prob = 1/13983816
        hits = [
            category_hits[0],  # 6 Treffer
            category_hits[1],  # 5 Treffer
            category_hits[2],  # 4 Treffer
            category_hits[3]   # 3 Treffer
        ]

    if (year, month, day) >= (1985, 6, 1):
        single_limit = None  # means no upper bound to single payouts
    elif (year, month, day) >= (1981, 7, 11):
        single_limit = 3000000
    elif (year, month, day) >= (1974, 7, 6):
        single_limit = 1500000
    # elif (year, month, day) >= (1974, 7, 11):
    #     single_limit = 1500000
    else:
        single_limit = 500000

    cat_perc = None
    if (year,month,day) >= (2013,5,4):
        cat_perc = adjust_cat_perc([0.128/2, 0.10/2, 0.05/2, 0.15/2, 0.05/2, 0.1/2, 0.1/2, 0.45/2, 5.0], category_hits)
    elif (year,month,day) >= (2003,8,16):
        cat_perc = adjust_cat_perc([0.05, 0.04, 0.025, 0.065, 0.01, 0.05,  0.04,  0.22], category_hits)
    elif (year,month,day) >= (1999,23,1):
        cat_perc = adjust_cat_perc([0.03, 0.04, 0.025, 0.065, 0.01, 0.055, 0.055, 0.22], category_hits)
    elif (year,month,day) >= (1997,10,11):
        cat_perc = adjust_cat_perc([0.03, 0.05, 0.03, 0.1, 0.1, 0.07, 0.12], category_hits)
    elif (year,month,day) >= (1992,1,4):
        cat_perc = adjust_cat_perc([0.02, 0.06, 0.03, 0.1, 0.1, 0.07, 0.12], category_hits)
    elif (year,month,day) >= (1985,6,1):
        cat_perc = adjust_cat_perc([0.075, 0.0375, 0.1125, 0.1125, 0.16], category_hits)
    elif (year,month,day) >= (1974,7,6):
        cat_perc = adjust_cat_perc_nojackpot([0.075, 0.0375, 0.1125, 0.1125, 0.16], category_hits, single_limit)
    elif (year,month,day) >= (1956,6,17):
        cat_perc = adjust_cat_perc_nojackpot([0.1, 0.025, 0.125, 0.125, 0.125], category_hits, single_limit)
    else:
        cat_perc = adjust_cat_perc_nojackpot([0.125, 0.125, 0.125, 0.125], category_hits, single_limit)

    has_jp = False
    if (year,month,day) >= (1985,6,1):
        has_jp = True

    calculated_category_pay = cat_perc[0] * spiel_einsatz
    jp_added = 0
    if category_hits[0] == 0 and has_jp:
        # single pay contains the new jackpot
        current_jackpot = category_single_pay[0]
        current_accu = jp_accu + 1
        if current_jackpot > 0:
            jp_added = current_jackpot - JP
        else:
            jp_added = category_single_pay[1] -JP
        d = jp_added - calculated_category_pay
        jp_accu += 1
        if ((year,month,day) < (2020,9,23) and jp_accu == 13) or ((year,month,day) >= (2020,9,23) and JP >= 45000000):
            assert current_jackpot == 0
            JP = 0
            jp_accu = 0
        else:
            JP = current_jackpot
    if category_hits[0] == 0 and not has_jp:
        d = 0
        JP = 0
    if category_hits[0] > 0:
        current_jackpot = category_hits[0] * category_single_pay[0]
        current_accu = jp_accu + 1
        jp_added = current_jackpot - JP
        d = (jp_added - calculated_category_pay)/category_hits[0]
        JP = 0
        jp_accu = 0

    if False and category_hits[0] > 0 and floor(fabs(d)) > 0:
        print(time_out(),
              "%.4f" % (auszahlungen / spiel_einsatz),
              "*" if floor(fabs(d/category_hits[0])) > 0 else '',
              str(category_hits[0])+("A" if JP_before else " ") if category_hits[0] else category_hits[0],category_hits[1],
              "%.2f"%d)
        print(*[int(x) for x in category_hits])
        print("%.7f"%(jp_added/spiel_einsatz),*["%.7f"%(category_hits[i] * category_single_pay[i] / spiel_einsatz) for i in range(1,len(category_hits))])
        #print(*["%.7f"%x for x in cat_perc])
        print(*["%.5f"%x for x in cat_perc])
        print(*["%.2f"%x for x in category_single_pay])
        print(*["%.2f"%(cat_perc[i]*spiel_einsatz/category_hits[i] if category_hits[i] else 0.0) for i in range(len(cat_perc)) ])

    ratios = [hits[i] / teilnehmer / avg_ratios[i] for i in range(4)]
    #print("%4d-%02d-%02d" % (year, month, day),["%.2f"%r for r in ratios])
    # if max(ratios) < .8 and (year,month,day) > (1962,9,30):
    #     print("%4d-%2d-%d"%(year,month,day), "%.4f"%(auszahlungen/spiel_einsatz),
    #         sorted(drawn_numbers),
    #         ["%.1f" % r for r in ratios],hits,category_hits)
    #     print_tippschein(drawn_numbers)
    if has_jp:
        print(time_out(), "%.1f"%(cat0_prob*1000000000), "%2.0f"%(category_hits[0]), "%4.1f"%(current_jackpot/jp_added), "%2d"%current_accu,
              "%9.0f"%teilnehmer, "%.1f"%jp_added, "%.1f"%current_jackpot)


max_ratios = [0, 0, 0, 0]
min_ratios = [1000, 1000, 1000, 1000]

JP = 0
jp_accu = 1
for year in range(1955,2013):
    with open('../data/lotto-hessen.de/6aus49/' + str(year) + '.csv') as f:
        r = csv.reader(f, delimiter=';')
        found_start = False
        for row in r:
            week_str = row[0]

            if year >= 2000:   # Mittwochs-ziehung startet 2000
                week_day = row[2]
                if not cardinal_pattern.fullmatch(week_str):
                    if not week_day == "SA":
                        continue
                drawn_numbers = row[3:9]

                if week_day == "SA" and week_str == "":
                    week_str = prev_row[0]

                ziehung = week_str + week_day
            else:
                if not cardinal_pattern.fullmatch(week_str):
                    continue
                drawn_numbers = row[2:8]
                ziehung = week_str

            day_month_str = row[1]
            month,day = month_day(day_month_str)
            zusatz_zahl = row[8]

            drawn_numbers = [int(i) for i in drawn_numbers]
            avg_ratios = [
                1/13983816,                  # 6 Treffer
                (6+252)/13983816,            # 5 Treffer
                (630 + 12915)/13983816,      # 4 Treffer
                (17220 + 229600) / 13983816  # 3 Treffer
            ]

            week = int(week_str.replace('.', ''))

            if year >= 2000:
                sei = 11
            elif year >= 1991:  # Superzahl kam hinzu
                superzahl = row[9]
                sei = 10
            elif year >= 1956:
                sei = 9
                if (year, week) >= (1956, 37):
                    zusatz_zahl = row[8]
            else:
                sei = 9  # SpielEinsatzIndex

            categories = row[sei+1:]
            while categories[len(categories)-1] == '':
                del categories[len(categories)-1]
            start_index = 0
            while True:
                try:
                    i = categories.index('',start_index)
                    if categories[i+1] == '':  # last element is not empty, hence i is not the last element
                        del categories[i+1]
                        del categories[i]
                        start_index = i+2
                    else:
                        start_index = i+1
                except ValueError:
                    break
            assert len(categories) % 2 == 0, str(year) + ":" + str(day_month_str) + ":" + str(categories) + "sei: " + str(sei)
            for i in range(int(len(categories)/2)):
                if year < 1992:
                    assert "x" in categories[2*i], categories[2*i]
                categories[2*i] = times2int(categories[2*i])
                categories[2*i+1] = german_price2float(categories[2*i+1])
            category_hits = [categories[2*i] for i in range(int(len(categories)/2))]
            category_single_pay = [categories[2*i+1] for i in range(int(len(categories)/2))]
            try:
                spiel_einsatz = german_price2float(row[sei])
            except:
                print(row)
                raise

            try:
                process()
            except Exception as e:
                print("Error at:", time_out(),e)
                raise

            JP_before = JP
            prev_row = row
            prev_category_hits = category_hits

with open('../data/lotto-hessen.de/6aus49/2015-2020.txt') as f:
    r = csv.reader(f, delimiter="\t")
    first_row = True
    for row in r:
        try:
            if first_row:
                first_row = False
                continue
            week_day = row[0]
            day = int(row[1])
            month = int(row[2])
            year = int(row[3])
            drawn_numbers = [int(i) for i in row[4:10]]
            zusatz_zahl = None
            if row[10].strip():
                zusatz_zahl = int(row[10])
            superzahl = int(row[11])
            spiel_einsatz = german_price2float(row[12])
            category_single_pay = [ german_price2float(row[13+2*i]) for i in range(9)]
            category_hits = [ times2int(row[13+2*i+1]) for i in range(9)]

            process()

            JP_before = JP
            prev_category_hits = category_hits
        except Exception as e:
            print("Error at:", time_out(),e)
            raise

