for n in {12..21}
do 
  echo $n | eatthepie ticket-history | tail +4 > lotteries/$n.py
  echo $n | eatthepie game-info | tail +6 > lotteries/$n.json
done