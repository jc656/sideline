# Sideline — context doc

Hand this to another session that needs to reason about youth flag football
substitution strategy. It describes what the app does and exactly how it decides
things, so strategy advice can build on it instead of guessing.

Live app: https://jc656.github.io/sideline/ — source: github.com/jc656/sideline
Single self-contained `sideline.html` (plain ES5, no framework, no build, no
backend) plus a service worker, manifest and icons. All data is local to one
phone's browser storage. Installed to the iPhone home screen; used on the
sideline during games.

## The setting

- 3rd grade rec flag football, 12 kids on the roster, 6 on the field.
- One coach taps the phone during the game. One assistant may take over through a
  handoff link (a baton pass, not live sync).
- Halves are about 25 minutes, clock-ish, not strictly managed.
- Rec league. Fair playing time matters; rule compliance does not. Do not propose
  features for league minimum-play rules.

## Core data (one object `S`, persisted to localStorage as `fb:state`)

| Field | Meaning |
|---|---|
| `roster` | `[{num, name, qb}]` — jersey number, up to 4-letter name, QB-eligible flag |
| `present` | jersey numbers checked in today |
| `field` | who is on the field right now |
| `stats` | `{num: {off, def}}` — snaps this game, offense and defense counted separately |
| `entry` / `exit` | monotonic tick when a kid last entered / left the field |
| `tick` | the monotonic counter behind `entry` and `exit` |
| `qbs` / `qbNow` | snaps taken at QB per kid / who is taking snaps right now |
| `half`, `clock`, `halfLen` | half number, rough clock state, half length (25 min) |
| `mode`, `down`, `play`, `since` | offense/defense, down, plays this game, plays since last swap |
| `us`, `them`, `pat` | score, and whether the extra-point row is showing |

Finished games are archived separately (`fb:season`): per-kid stats, QB snaps,
score, starters, names, game number.

## Settings and defaults

| Setting | Default | Range |
|---|---|---|
| `fieldSize` | 6 | hard-coded, shrinks if fewer kids show up |
| `subSize` — swapped at a time | 3 | 1–6 |
| `interval` — swap every N | 4 | 1–12 |
| `trigger` — count in | plays | plays or possessions |
| `rotation` | sequence | sequence or catchup |
| `gapLimit` — fairness flag | 6 | 2–20 |
| `halfLen` | 25 min | — |
| `weeks` | 8 game slots | 1–20 |

## The rotation algorithm

Every swap suggestion is `{inL, outL}` of equal length, where
`k = min(subSize, bench size, field size)`.

**Who comes OFF** (both modes, identical):
sort the field by most total snaps first; ties break to whoever entered earliest.
Take the first `k`.

**Who goes ON:**

- `sequence` (default): bench sorted by **longest time off the field** —
  ascending `exit` tick, ties by jersey number. A kid who has never played has
  `exit = 0`, so they go in before anyone who has already had a shift.
- `catchup`: bench sorted by **fewest total snaps**, ties by jersey number.

**Important history:** "sequence" originally picked the next bench kid by jersey
number *after the last kid who entered*. That broke whenever starters were not
consecutive numbers. With starters 1,2,3,10,11,12 it pulled 10,11,12 off at play
8 and sent them straight back in at play 12. Replacing jersey adjacency with
bench wait time fixed it and made the cycle stable for any starting six. Do not
suggest going back to jersey-order-next; it is a known bug, not a design choice.

**QB guard (`keepQb`), applied after the lists are built:** if no QB-eligible kid
would remain on the field, first swap the longest-waiting eligible QB in (taking
the slot of the last non-QB in `inL`); if the bench has none, keep an eligible QB
on the field by pulling them out of `outL` and taking the next
most-played kid instead.

**Backfill (`fillField`)** uses the same ordering when the field is short (a kid
leaves, a late arrival, a roster change), preferring an eligible QB if the field
would otherwise have none.

### Measured behavior (simulated, 12 kids, 6 on, swap 3 every 4 plays, 36 plays)

- Consecutive starters: everyone lands on 16–20 snaps. Perfectly even would be 18.
- Split starters (1,2,3,10,11,12): also 16–20, settling into four fixed groups
  that cycle — 1,2,3 → 4,5,6 → 7,8,9 → 10,11,12.
- A kid arriving mid-game is absorbed and the cycle re-stabilizes.
- 11 kids (bench of 5, swapping 3) cannot divide evenly, so groups reshuffle every
  cycle and the spread widens to 16–24. No ordering rule fixes that; it is
  arithmetic.
- Real game data: 36 plays, kids played 16–20 snaps each.

## The QB model — two separate concepts

1. **Eligible (`roster[].qb`)** — set once per season on the Team tab. Advisory
   only. It drives the `keepQb` guard and the auto-pick default. It never blocks
   anyone.
2. **Taking snaps (`qbNow`)** — exactly one kid on the field. Auto-picked at the
   start of each offensive possession as the eligible on-field kid with the
   **fewest QB snaps** (ties: fewer total snaps, then lower jersey). If no
   eligible kid is on the field, it picks from everyone on the field. The coach
   can tap any on-field kid in the QB row to override.

Each offensive snap increments `qbs[qbNow]`.

**Known tension:** with only one eligible QB, the guard keeps that kid on the
field nearly every play — simulated 32 of 36 snaps, while others fell to 12. With
two or more eligible, the cost disappears (16–20 spread, same as no QB rule). The
app warns when only one eligible QB is checked in.

## Fairness warning

A kid is flagged (red chip and red count) when `behindBy(n) >= limit`, where
`behindBy` is leader snaps minus theirs, and the limit is
`max(gapLimit, naturalGap)`.

`naturalGap = ceil(bench size / subSize) * interval + 2` for the plays trigger,
0 for possessions.

The point: following the rotation perfectly still opens a gap, because a group
sits out while the leaders keep playing. With 12/6/3 every 4 plays that natural
gap is 8, so the app flags at 10 rather than the raw setting of 6. Before this,
the warning fired constantly during normal, correct rotation. The warning is also
suppressed until the rotation has reached everyone at least once.

The warning is relative to the leader, never an absolute minimum. An absolute
minimum nagged for the whole first quarter and was deliberately removed.

## Play recording

- One big PLAY RAN button per snap. Offense and defense snaps counted separately
  for every kid on the field.
- On 4th down, PLAY RAN asks what happened: first down, touchdown, or turnover on
  downs. Nothing is recorded until an outcome is picked.
- Touchdown: 6 points, then the extra-point row (1 / 2 / no good); the PAT counts
  as a snap and then possession flips.
- First down resets the down but deliberately does **not** reset the swap counter.
- Undo is in-memory only and clears on reload.

## Halves and clock

- Rough 25-minute countdown per half, started and paused by hand, based on
  wall-clock time so it survives the phone sleeping. It never gates anything.
- "Start the second half" resets the clock and swap counter and switches the
  rotation to `catchup`, so second-half subs even out playing time.

## Season and handoff

- Fixed slots (default 8). Each is open, live or final. Game numbers come from the
  slot, so playing out of order and deleting games both work.
- Handoff encodes the live game into a base64 URL fragment to text to another
  coach, who takes over. Past games are dropped from the payload if it would
  exceed about 1700 characters. Takeover merges saved games by id.
- JSON backup export/import of everything; CSV export of per-kid per-game rows.

## Constraints to respect when proposing strategy or features

- No backend, no accounts, no analytics, no live multi-phone sync.
- One file, no build step, no npm runtime dependencies.
- Must work offline once loaded.
- Field size stays hard-coded at 6 unless asked.
- Playing time is per game. There is no per-half quota.
- The coach is holding a phone during a live game. Anything requiring more than a
  tap or two per play will not get used.

## Open questions a strategy session could help with

- Best `subSize` / `interval` pairing for a 25-minute half with roughly 36–40
  plays, given that swaps interrupt drives.
- Whether a kid should ever come off mid-drive, and whether the possessions
  trigger is the better default.
- How to balance QB snaps against total playing time when only two kids can throw.
- Whether second-half catch-up should be automatic (it is now) or suggested.
- Starting-six selection: currently random (with an eligible QB forced in) or
  hand-picked. A smarter rule could consider last game's snaps.
