import csv
from math import floor
from lotto import times2int, german_price2float, month_day, date, cardinal_pattern, date_pattern, dmy_date


def print_tippschein(numbers):
    for i in range(10):
        print("|", end="")
        for j in range(5):
            number = 5 * i + j + 1
            if number in numbers:
                print(f"{number:02d}", end="")
            else:
                print("  ", end="")
        print("|")


class GO(object):
    pass


class Base(object):
    def __init__(self, base):
        self.spiel_einsatz = base['spiel_einsatz']
        self.year = base['year']
        self.month = base['month']
        self.day = base['day']
        self.cat_hits = base['cat_hits']
        self.cat_single_pay = base['cat_single_pay']
        self.dn_5aus50 = base['dn_5aus50']
        if (self.year, self.month, self.day) >= (2014, 10, 10):
            self.dn_2aus10 = base['dn_2aus8_2aus10']
        else:
            self.dn_2aus8 = base['dn_2aus8_2aus10']


class Data(object):
    def __init__(self, d):
        self.year = d['year']
        self.month = d['month']
        self.day = d['day']
        self.cat_jackpot = d['cat_jackpot']
        self.cat_hits = d['cat_hits']
        self.spiel_einsatz = d['spiel_einsatz']
        self.single_spiel_einsatz = d['single_spiel_einsatz']
        self.cat_single_pay = d['cat_single_pay']
        self.teilnehmer = d['teilnehmer']
        self.current_accu = d['current_accu']
        self.cat_perc = d['cat_perc']
        self.base = d['base_object']


def iterate_base():
    file_prefix = '../data/sachsenlotto.de/eurojackpot/'

    for year in range(2012, 2018):
        with open(file_prefix + str(year) + '.csv') as f:
            r = csv.reader(f, delimiter=';')
            for row in r:
                kw = row[0]
                if not cardinal_pattern.fullmatch(kw):
                    continue
                day_month = row[1]
                month, day = month_day(day_month)
                week_day = row[2]
                dn_5aus50 = [int(n) for n in row[3:8]]
                dn_2aus8_2aus10 = [int(n) for n in row[8:10]]
                spiel_einsatz = german_price2float(row[10])
                categories = row[11:36]
                cat_hits = [times2int(categories[2 * i]) for i in range(int(len(categories) / 2))]
                cat_single_pay = [german_price2float(categories[2 * i + 1]) for i in range(int(len(categories) / 2))]
                yield Base(locals())

    with open(file_prefix + "EJ_ab_2019.csv", encoding='iso-8859-1') as f:
        r = csv.reader(f, delimiter=';')
        for row in r:
            if len(row) == 0:
                continue
            datum = row[0]
            if not date_pattern.fullmatch(datum):
                continue
            day, month, year = dmy_date(datum)

            dn_5aus50 = [int(n) for n in row[1:6]]
            dn_2aus8_2aus10 = [int(n) for n in row[6:8]]

            spiel_einsatz = german_price2float(row[8])
            categories = row[9:34]
            cat_hits = [times2int(categories[2 * i]) for i in range(int(len(categories) / 2))]
            cat_single_pay = [german_price2float(categories[2 * i + 1]) for i in range(int(len(categories) / 2))]
            yield Base(locals())


def iterate_data():
    cat_jackpot = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    cat_gewinn_ausschuettung = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    current_accu = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    booster_fond = 0
    last_booster_fond = 0
    for base_object in iterate_base():
        base = base_object.__dict__
        spiel_einsatz = base['spiel_einsatz']
        year = base['year']
        month = base['month']
        day = base['day']
        cat_hits = base['cat_hits']
        cat_single_pay = base['cat_single_pay']

        gesamt_gewinn_ausschuettung = spiel_einsatz / 2  # 20.1
        # 12 categories plus booster
        single_spiel_einsatz = 2.0  # 2EUR
        if (year, month, day) >= (2014, 10, 10):
            cat_perc = [0.36, 0.085, 0.03, 0.01, 0.009, 0.007, 0.006, 0.031, 0.03, 0.043, 0.078, 0.191, 0.12]  # 20.4
        else:
            cat_perc = [0.22, 0.05, 0.013, 0.012, 0.0095, 0.006, 0.0085, 0.041, 0.0345, 0.036, 0.12, 0.2295, 0.22]

        teilnehmer = spiel_einsatz / single_spiel_einsatz
        cat_gewinn_ausschuettung = [cat_perc[j] * gesamt_gewinn_ausschuettung for j in range(13)]
        booster_fond += cat_gewinn_ausschuettung[12]  # 20.2
        calc_single_pay = [0.0 for j in range(12)]

        cat_jackpot = [cat_jackpot[j] + cat_gewinn_ausschuettung[j] for j in range(12)]
        current_accu = [current_accu[j] + 1 for j in range(12)]

        # 20.15
        if last_booster_fond > 20000000:
            d = last_booster_fond - 20000000
            cat_jackpot[0] += d
            booster_fond -= d
            # print(f"Transferred {d} to current jackpot")

        # 20.10
        # 20.14
        if cat_jackpot[0] < 10000000:
            booster_fond -= 10000000 - cat_jackpot[0]
            cat_jackpot[0] = 10000000

        if (year, month, day) >= (2014, 10, 10):
            # 20.12
            if cat_jackpot[0] > 90000000:
                cat_jackpot[1] += cat_jackpot[0] - 90000000
                cat_jackpot[0] = 90000000
            if cat_jackpot[1] > 90000000:
                j_has_gewinn = min([j for j in range(2, 12) if cat_hits[j] > 0])
                cat_jackpot[j_has_gewinn] += cat_jackpot[1] - 900000000
                cat_jackpot[1] = 900000000
        else:
            if current_accu[0] == 13 and cat_hits[0] == 0:
                for j in range(1, 12):
                    if cat_hits[j] > 0:
                        break
                cat_jackpot[j] += cat_jackpot[0]
                cat_jackpot[0] = 0

        for j in range(12):
            if cat_hits[j] == 0:
                calc_single_pay[j] = None
            else:
                calc_single_pay[j] = cat_jackpot[j] / cat_hits[j]

        # print([None if x is None else floor(x*10)/10 for x in single_gewinn_ausschuettung])
        # 20.9
        sga_indexes = [i for i in range(12) if calc_single_pay[i] is not None]
        straight = True
        for i in range(len(sga_indexes)):
            for j in range(i + 1, len(sga_indexes)):
                m = sga_indexes[i]
                k = sga_indexes[j]
                if calc_single_pay[k] > calc_single_pay[m]:
                    straight = False
                    affected = sga_indexes[i:j + 1]
                    sga = sum([cat_jackpot[m] for m in affected]) / sum([cat_hits[m] for m in affected])

                    for l in affected:
                        calc_single_pay[l] = sga

        # 20.10 rounding
        for j in range(12):
            if calc_single_pay[j] is not None:
                sga0 = calc_single_pay[j]
                sga = floor(sga0 * 10) / 10
                sga_diff = sga0 - sga
                booster_fond += sga_diff * cat_hits[j]
                calc_single_pay[j] = sga

        single_pay_diff = [
            None if calc_single_pay[j] is None else
            cat_single_pay[j] - calc_single_pay[j] for j in range(12)]
        cat_pay_diff = [
            None if calc_single_pay[j] is None else
            cat_hits[j] * (cat_single_pay[j] - calc_single_pay[j]) for j in range(12)
        ]

        # print(date(year, month, day),
        #       "%2d" % (current_accu[0]),
        #       "%12.2f" % booster_fond,
        #       "%12.2f" % cat_jackpot[0],
        #       cat_single_pay,
        #       end='')
        # if sum([fabs(x) for x in single_pay_diff if x is not None]) > 0:
        #     print(*[None if x is None else "%.2f" % x for x in cat_pay_diff])
        # else:
        #     print()

        yield Data(locals())

        for j in range(12):
            if cat_hits[j] > 0:
                cat_jackpot[j] = 0
                current_accu[j] = 0
        last_booster_fond = booster_fond


# for each categories how many correct numbers in 5, how many correct number in 2
cat_pairs = [  # TODO: is it valid also before (2014, 10, 10)?
    (5, 2), (5, 1), (5, 0),
    (4, 2), (4, 1), (4, 0),
    (3, 2), (2, 2), (3, 1),
    (3, 0), (1, 2), (2, 1)
]
cat_index = {
    (5, 2): 0, (5, 1): 1, (5, 0): 2,
    (4, 2): 3, (4, 1): 4, (4, 0): 5,
    (3, 2): 6, (2, 2): 7, (3, 1): 8,
    (3, 0): 9, (1, 2): 10, (2, 1): 11
}

# the probability for each category
cat_p = [1 / 95344200, 1 / 5959013, 1 / 3405150, 1 / 423752, 1 / 26485, 1 / 15134, 1 / 9631, 1 / 672, 1 / 602, 1 / 344,
         1 / 128, 1 / 42]
# probability of having 5 correct from 5, 4 correct from 5, 3 correct from 5 ...
p5 = [1 / 2118760, 225 / 2118760, 9900 / 2118760]

p_10_2 = 1 / 45


def main3():
    for do in iterate_data():
        d = do.__dict__
        year = d['year']
        month = d['month']
        day = d['day']
        cat_jackpot = d['cat_jackpot']
        cat_hits = d['cat_hits']
        spiel_einsatz = d['spiel_einsatz']
        single_spiel_einsatz = d['single_spiel_einsatz']
        cat_perc = d['cat_perc']
        cat_single_pay = d['cat_single_pay']
        teilnehmer = d['teilnehmer']
        current_accu = d['current_accu']
        base = d['base']

        hits5 = [
            cat_hits[cat_index[5, 2]] + cat_hits[cat_index[5, 1]] + cat_hits[cat_index[5, 0]],
            cat_hits[cat_index[4, 2]] + cat_hits[cat_index[4, 1]] + cat_hits[cat_index[4, 0]],
            cat_hits[cat_index[3, 2]] + cat_hits[cat_index[3, 1]] + cat_hits[cat_index[3, 0]],
        ]
        dev5 = [ hits5[i] / (teilnehmer * p5[i]) for i in len(hits5)]
        roi1 = cat_jackpot[0] * cat_p[0] / single_spiel_einsatz + sum([cat_perc[i] / 2 for i in range(1, 12)])
        roi2 = sum([cat_jackpot[i] / max(1, cat_hits[i]) / single_spiel_einsatz * cat_p[i] for i in range(12)])
        # assuming cat_jackpot[i] = cat_perc[i]/2 * spiel_einsatz
        # and cat_hits[i] = teilnehmer*cat_p[i]
        # cat_jackpot[i]/cat_hits[i]/2.0*cat_p[i] = cat_perc[i]*spiel_einsatz/2/teilnehmer/2.0 = cat_perc[i]/2
        # print(date(year,month,day),"%2d" % (current_accu[0]),"%9d"%cat_jackpot[0],
        #      "%.1f" % (cat_jackpot[0]/spiel_einsatz),
        #      "%.1f" % roi1, "%.1f" % roi2)
        # print(date(year,month,day),*['%.3f'%(cat_hits[i]/(teilnehmer*cat_p[i])) for i in range(12)])

        if max(dev5) > 2:
            print(date(year, month, day), dev5)
            print_tippschein(base.dn_5aus50)


def einzelzahlen_p():
    occurence = {}
    for n in range(1, 51):
        occurence[n] = 0
    assumed = 0
    for do in iterate_data():
        assumed += do.teilnehmer * cat_p[0]
        for n in do.base.dn_5aus50:
            occurence[n] += do.cat_hits[0]
    factors = [occurence[n] / assumed for n in range(1, 51)]
    print(*['%.3f' % f for f in factors])


def calc_ranking_set():
    ranking_set = {}
    for data in iterate_data():
        o = GO()
        o.dn_5aus50 = sorted(data.base.dn_5aus50)
        if not hasattr(data.base,'dn_2aus10'):
            continue
        o.dn_2aus10 = sorted(data.base.dn_2aus10)
        o.hit_ratio = [data.base.cat_hits[i] / data.teilnehmer for i in range(12)]
        o.hit_ratio_factor = [o.hit_ratio[i] / cat_p[i] for i in range(12)]
        o.date = (data.base.year,data.base.month,data.base.day)
        key = tuple(o.dn_5aus50+o.dn_2aus10)
        # TODO, what if we have duplicate key?
        ranking_set[key] = o
    return ranking_set


ranking_set = calc_ranking_set()


def cats(key1,key2):
    #counts the number of the intersections
    return \
        len(set(key1[0:5]).intersection(set(key2[0:5]))),\
        len(set(key1[5:7]).intersection(set(key2[5:7])))


cat_perc = [0.36, 0.085, 0.03, 0.01, 0.009, 0.007, 0.006, 0.031, 0.03, 0.043, 0.078, 0.191, 0.12]  # 20.4
cat_perc2 = [ x/2 for x in cat_perc]


def rank(key):
    #theoretically we go over all keys that intersect in cat with the given key
    #and add up their cat hit probability/ratio
    #as we dont have the cat hit p for all keys, we want to to focus on the keys
    #that we have information about, i.e. the ones from the ranking_set
    #so we consider the other ones having the average cat hit p (cat_p)
    #as the number of all keys K that intersect in cat is 1/cat_p[cat]
    #say we have S samples in ranking_set, then the sum is
    # sum(hit_p[k],K)=(K-S)*cat_p[cat] + sum(hit_p[s],S)
    # = 1-S*cat_p[cat] + sum(hit_p[s],S)
    # = 1 - sum(hit_p[s]-cat_p[cat],S)
    s = [1.0 for i in cat_pairs]
    for rkey in ranking_set:
        cat_pair = cats(key, rkey)
        if cat_pair in cat_pairs:
            ci = cat_index[cat_pair]
            s[ci] -= ranking_set[rkey].hit_ratio[ci] - cat_p[ci]
    return s


def all_keys():
    from itertools import combinations
    for n5 in combinations(range(1,51),5):
        for n2 in combinations(range(1,11),2):
            yield n5+n2


def sorted_ranking_list():
    ranking_list = list(ranking_set.keys())
    ranking_list.sort(key=lambda key: list(reversed(ranking_set[key].hit_ratio_factor)))

    for key in ranking_list:
        o = ranking_set[key]
        print(*["%2d"%z for z in o.dn_5aus50],'|',
              *["%2d"%z for z in o.dn_2aus10],'|',
              *["%.3f" % x for x in o.hit_ratio_factor],
              o.date)


def lp0(l,f):
    print(end='',*[f%x for x in l])
def lp(l,f):
    print(*[f%x for x in l])


if __name__ == "__main__":
    from timeit import default_timer as timer

    start = timer()
    tc = 0
    for key in all_keys():
        tc +=1
    end = timer()
    print(tc,"Took:",end-start)
    start = timer()
    tc = 0
    for key in all_keys():
        tc +=1
    end = timer()
    print(tc,"Took:",end-start)
    #ak.sort(key=lambda k:rank(k)[11])
    count = 0
    for key in all_keys():
        if count > 100:
            break
        if rank(key)[11] < 0.9:
            count += 1
            print(key,end='')
            lp0(rank(key),"%.3f")
            if key in ranking_set:
                lp0(ranking_set[key].hit_ratio_factor,"%.3f")
            print()



