# crypto-dot-com
Asynchronous Crypto.com position service.

Made to run `lambda_function.py` on AWS Lambda to send exchange balance and open orders data to telegram.

```
 July 2023, 21:25 PM

 ccy  notional  5m   1h   6h  24h
COMP $7,127.11 0.2  0.1  2.3  2.7
 LTC $3,408.05 0.3 -0.1  0.5  1.2
 BCH   $868.08 0.0 -0.2  1.3  1.8
 USD   $804.04
USDT   $487.80 0.0  0.0 -0.0 -0.0

Exch Balance: $12,695.63

┤
┤                             ╭─╮
┤                          ╭──╯ ╰
┤                          │
┤    ╭╮                 ╭╮ │
┼╮   │╰╮                ││╭╯
┤│  ╭╯ │                │││
┤╰╮ │  ╰─╮              │╰╯
┤ ╰╮│    │╭──╮          │
┤  ││    ││  ╰╮         │
┤  ╰╯    ╰╯   │         │
┤             ╰╮       ╭╯
┤              ╰──╮╭╮╭─╯
┤                 ╰╯╰╯
   30    24    18    12    6
Min: $12,212.80
Max: $12,730.63

Open Orders
    inst side   qty  limit  price
 BCH-USD SELL 3.480 290.00 249.43
COMP-USD SELL 11.90  84.00  73.32
COMP-USD SELL 17.64  85.00  73.32
COMP-USD SELL 29.06  86.00  73.32
COMP-USD SELL 38.47  88.00  73.32

[Finished in 0.945s]
```
