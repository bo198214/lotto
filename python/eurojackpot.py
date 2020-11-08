import argparse
import re
import csv
from math import floor, fabs
from lotto import times2int, german_price2float, month_day, date, cardinal_pattern

cat_jackpot = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cat_gewinn_ausschuettung = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
current_accu = [0,0,0,0, 0,0,0,0, 0,0,0,0]

booster_fond = 0
last_booster_fond = 0

for year in range(2012,2018):
    with open('../data/sachsenlotto.de/eurojackpot/' + str(year) + '.csv') as f:
        r = csv.reader(f, delimiter=';')
        for row in r:
            KW = row[0]
            if not cardinal_pattern.fullmatch(KW):
                continue
            day_month = row[1]
            month,day = month_day(day_month)
            week_day = row[2]
            dn_5aus50 = row[3:7]
            dn_2aus8 = row[8:9]
            spiel_einsatz = german_price2float(row[10])
            gesamt_gewinn_ausschuettung = spiel_einsatz / 2  #20.1
            categories = row[11:36]
            cat_hits = [times2int(categories[2 * i]) for i in range(int(len(categories) / 2))]
            cat_single_pay = [german_price2float(categories[2 * i + 1]) for i in range(int(len(categories) / 2))]

            #12 categories
            #5,2
            #5,1
            #5,0
            #4,2
            #4,1
            #4,0
            #3,2
            #3,1
            #3,0
            #2,2
            #2,1
            #2,0
            #12 categories plus booster
            if (year,month,day) >= (2014,10,10):
                cat_perc = [0.36,0.085,0.03,0.01,0.009,0.007,0.006,0.031,0.03,0.043,0.078,0.191,  0.12] #20.4
            else:
                cat_perc = [0.22,0.05,0.013,0.012,0.0095,0.006,0.0085,0.041,0.0345,0.036,0.12,0.2295,  0.22]

            cat_gewinn_ausschuettung = [cat_perc[j] * gesamt_gewinn_ausschuettung for j in range(13)]
            booster_fond += cat_gewinn_ausschuettung[12] #20.2
            calc_single_pay = [0.0 for j in range(12)]

            cat_jackpot = [cat_jackpot[j] + cat_gewinn_ausschuettung[j] for j in range(12)]
            jackpot_from_cat = [
                None if cat_single_pay[j] is None else
                cat_single_pay[j] * cat_hits[j] - cat_gewinn_ausschuettung[j] for j in range(12)]
            current_accu = [ current_accu[j] + 1 for j in range(12)]

            #20.15
            if  last_booster_fond > 20000000:
                d = last_booster_fond - 20000000
                cat_jackpot[0] += d
                booster_fond   -= d
                #print(f"Transferred {d} to current jackpot")

            #20.10
            #20.14
            if  cat_jackpot[0]   < 10000000:
                booster_fond -= 10000000 - cat_jackpot[0]
                cat_jackpot[0]   = 10000000

            if (year, month, day) >= (2014, 10, 10):
                #20.12
                if  cat_jackpot[0] > 90000000:
                    cat_jackpot[1] += cat_jackpot[0] - 90000000
                    cat_jackpot[0] = 90000000
                if  cat_jackpot[1] > 90000000:
                    j_has_gewinn = min([j for j in range(2,12) if cat_hits[j] > 0])
                    cat_jackpot[j_has_gewinn] += cat_jackpot[1] - 900000000
                    cat_jackpot[1] = 900000000
            else:
                if current_accu[0] == 13 and cat_hits[0] == 0:
                    for j in range(1,12):
                        if cat_hits[j] > 0:
                            break
                    cat_jackpot[j] += cat_jackpot[0]
                    cat_jackpot[0] = 0


            for j in range(12):
                if cat_hits[j] == 0:
                    calc_single_pay[j] = None
                else:
                    calc_single_pay[j] = cat_jackpot[j] / cat_hits[j]

            #print([None if x is None else floor(x*10)/10 for x in single_gewinn_ausschuettung])
            #20.9
            sga_indexes = [i for i in range(12) if calc_single_pay[i] is not None]
            straight = True
            for i in range(len(sga_indexes)):
                for j in range(i+1,len(sga_indexes)):
                    m = sga_indexes[i]
                    k = sga_indexes[j]
                    if calc_single_pay[k] > calc_single_pay[m]:
                        straight = False
                        slice = sga_indexes[i:j+1]
                        sga = sum([cat_jackpot[m] for m in slice]) / sum([cat_hits[m] for m in slice])

                        for l in slice:
                            calc_single_pay[l] = sga

            #20.10 rounding
            for j in range(12):
                if calc_single_pay[j] is not None:
                    sga0 = calc_single_pay[j]
                    sga = floor(sga0 * 10) / 10
                    sga_diff =  sga0 - sga
                    booster_fond += sga_diff * cat_hits[j]
                    calc_single_pay[j] = sga

            single_pay_diff = [
                None if cat_single_pay[j] is None else
                cat_single_pay[j] - calc_single_pay[j] for j in range(12)]
            cat_pay_diff = [
                None if cat_single_pay[j] is None else
                cat_hits[j]*(cat_single_pay[j] - calc_single_pay[j]) for j in range(12)
            ]
            # if single_pay_diff[0] is not None and single_pay_diff[0] > 0:
            #     #Adjust booster fond
            #     #last booster fond was single_pay_diff above 200000000
            #     #hence this booster fond is 20000000 plus that was added from last to this
            #     booster_fond -= cat_pay_diff[0]
            #     print(f"Adjusted boosterfond to {booster_fond}")



            #assert sum(cat_gewinn_ausschuettung)+0.12*gesamt_gewinn_ausschuettung == gesamt_gewinn_ausschuettung, str(sum(cat_gewinn_ausschuettung)+0.12*gesamt_gewinn_ausschuettung) + "!=" + str(gesamt_gewinn_ausschuettung)

            #sum([category_hits[i]*category_single_pay[i] for i in len(range(category_hits))])
            # calc_perc = [
            #     None if cat_single_pay[j] is None else
            #     cat_single_pay[j] * cat_hits[j] / gesamt_gewinn_ausschuettung for j in range(12)
            # ]
            # if straight: print("straight")
            # print(*[None if x is None else "%.3f"%x for x in calc_perc])
            print(date(year, month, day),
                  "%2d" % (current_accu[0]),
                  "%12.2f" % booster_fond,
                  "%12.2f" % cat_jackpot[0],
                  cat_single_pay,
                  end='')
            if sum([fabs(x) for x in single_pay_diff if x is not None]) > 0:
                print(*[None if x is None else "%.2f" % x for x in cat_pay_diff])
            else:
                print()

            for j in range(12):
                if cat_hits[j] > 0:
                    cat_jackpot[j] = 0
                    current_accu[j] = 0
            last_booster_fond = booster_fond
