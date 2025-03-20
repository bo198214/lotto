#!/bin/bash

eatthepie ticket-history $1 > lotteries/ticket-history-$1.json
eatthepie game-info      $1 > lotteries/game-info-$1.json
