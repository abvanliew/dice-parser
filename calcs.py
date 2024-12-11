import polars

def to_roll( index: int, count: int ) -> list[int]:
  roll = []
  for _ in range( count - 1 ):
    ( index, mod ) = divmod( index, 6 )
    roll.append( mod + 1 )
  roll.append( index + 1 )
  return roll

def result_counts( roll: list[int] ) -> dict:
  results = {}
  for die in roll:
    results[die] = results.get( die, 0 ) + 1
  return results

def lowest_three( roll: list[int] ) -> list[int]:
  return sorted(roll)[:3]

def set_chances( dice_count: int, lowest: bool = False ) -> tuple[dict,dict]:
  doubles = {}
  triples = {}
  total_count = pow( 6, dice_count )
  for i in range( total_count ):
    roll = to_roll( i, dice_count )
    if lowest:
      roll = lowest_three( roll )
    roll_counts = result_counts( roll )
    for key, value in roll_counts.items():
      if value >= 2:
        doubles[key] = doubles.get( key, 0 ) + 1
      if value >= 3:
        triples[key] = triples.get( key, 0 ) + 1
  for ( key, count ) in doubles.items():
    doubles[key] = 100.0 * count / total_count
  for ( key, count ) in triples.items():
    triples[key] = 100.0 * count / total_count
  return (doubles, triples)

def crit_chance_triples( triple_chances: dict ) -> list[float]:
  crit_chance = []
  sum = 0
  for die in range( 6, 1, -1 ):
    sum += triple_chances.get( die, 0 )
    crit_chance.append( sum )
  return crit_chance

def crit_chance_double_six( double_chances: dict ) -> list[float]:
  return [ double_chances.get( 6, 0 ) ]

crit_data = { "crit_on_at_least": [ "dbl 6", "6", "5", "4", "3", "2" ] }
for i in range( 7 ):
  lowest = i < 3
  dice_count = 6 - i if lowest else i
  ( doubles, triples ) = set_chances( dice_count, lowest )
  crit_data[f"{i-3}"] = crit_chance_double_six( doubles ) + crit_chance_triples( triples )

crit_frame = polars.from_dict( crit_data )
crit_frame.write_csv( "crit.csv" )