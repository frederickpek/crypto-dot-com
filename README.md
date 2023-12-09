# crypto-dot-com
Asynchronous crypto.com position service.

Made to run `lambda_function.py` on AWS Lambda to send exchange balance and open orders data to telegram.

```
 07 December 2023, 21:00 PM

ccy   notional       qty    pct
USD $32,832.38 32,832.38 74.12%
ETH  $6,028.84      2.67 13.61%
BTC  $5,180.66      0.12 11.70%
SOL    $248.06      3.85  0.56%

Exch Balance:    $44,294.85
 Sgd Balance:    $59,360.57

┤
┤  ╭╮
┤  ││
┼──╯╰╮
┤    │
┤    │                          ╭
┤    │        ╭╮                │
┤    │        ││                │
┤    ╰╮ ╭╮ ╭─╮│╰─╮     ╭─╮╭╮  ╭─╯
┤     │╭╯│ │ ╰╯  │     │ ╰╯│╭╮│
┤     ╰╯ ╰╮│     │ ╭───╯   ││╰╯
┤         ╰╯     ╰╮│       ╰╯
┤                 ││
┤                 ╰╯
   30    24    18    12    6
$42,737.01 - $45,212.10 (5.79%)

ccy      price  5m  1h   6h  24h
SOL     $64.39 0.1 0.3  1.6  1.6
ETH  $2,255.11 0.2 0.8 -0.2 -0.4
BTC $43,392.26 0.2 0.5 -1.1 -1.5

Open Orders
   inst side    qty limit price
SOL-USD  BUY 529.00 62.00 64.41

[Finished in 2.478s]
```
