#!/bin/bash

for n in {13..22}
do 
  eatthepie ticket-history $n > lotteries/ticket-history-$n.json
  eatthepie game-info      $n > lotteries/game-info-$n.json
done