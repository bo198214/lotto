#We have N Players
#Each bets on a number of the dice
#And wins all the money divided by the number of other players with the right bet


import random

def simple_jackpot():
    N = 10

    wallets = [0 for i in range(N)]
    pool = 0
    events_num = 2
    decuction_factor = 0.1

    for count in range(1,10000):
        random.seed()

        bets = [ random.randint(1,events_num) for i in range(N) ]
        stakes = [5] + [ 1 for i in range(1,N)]

        pool += sum(stakes)*(1-decuction_factor)
        wallets = [wallets[i] - stakes[i] for i in range(N)]

        draw = random.randint(1,events_num)

        winners = [ i for i in range(N) if bets[i] == draw ]
        if len(winners) > 0:
            single_payout = pool / len(winners)
            pool = 0
        else:
            single_payout = 0

        for i in winners:
            wallets[i] += single_payout
        #print("%8.2f"%(sum(wallets)),["%8.2f"%(x/count) for x in wallets])
        print("%8.2f"%(sum(wallets)),"%8.2f"%sum([(x/count) for x in wallets]))

def fixed_payout():
    events_num = 6
    single_payout = 7

    wallet = 0

    for count in range(1, 10000):
        random.seed()

        wallet -= 1

        bet = random.randint(1, events_num)
        draw = random.randint(1, events_num)

        if bet == draw:
            wallet += single_payout

        print("%3d"%count,"%3f"%(wallet/count))

simple_jackpot()