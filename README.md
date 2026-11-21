[![the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/miologalo/passport-invented-spread/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/miologalo/passport-invented-spread/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

An invented passport spread for the **Republic of Zembla** — a country that
does not exist — drawn entirely in code for make.fun's "The Passport Page of
a Country That Isn't There" bounty ($50 in USDC).

## The document

The holder is **Elena Mara Korvin**, born 12 May 1991 in Onhava, Zembla.
Her passport (No. ZB0048217) was issued 14 Mar 2024 in Onhava and expires
13 Mar 2034. The spread shows:

- **Data page** — crowned coat of arms (star over three waves), bilingual
  Zemblan/English fields, a drawn portrait, the holder's signature, and a
  machine-readable zone with correct ICAO 9303 check digits.
- **Visa page** — a Kingdom of Thule visa (single entry, 01 Sep – 30 Nov
  2025), Arcadia arrival/departure stamps (02 / 18 Jun 2024), a round
  Republic of Karnia transit stamp (11 May 2025), and a Thule entry stamp
  (09 Sep 2025, inside the visa's validity). Every stamp falls after the
  passport's issue date and before its expiry.
- **The telling detail** — a red endorsement: *"NOT VALID FOR TRAVEL TO THE
  NORTHERN MARCHES"*, with a 40-krona fee stamp. The Northern Marches are
  closed to holders of this passport.

## How it works

`main.py` (Python 3.13, Pillow only) draws the whole spread
programmatically — paper, guilloché security print, arms, portrait, stamps
and the MRZ — and writes `entry.png` (1024×1024 PNG, ~203 KB, under the
1 MiB cap) to `/output/entry.png` when `/output` exists, otherwise next to
itself. No network, no copied-in image; two runs are byte-identical.

## License

MIT. See LICENSE.
