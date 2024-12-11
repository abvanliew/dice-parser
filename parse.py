import polars, re
from polars import DataFrame, scan_csv
from io import StringIO
from enum import Enum

class ParseState( Enum ):
  NEW_ENTRY = 0
  PROCESS_ROW = 1

def stat_col_names( _: list[str] ) -> list[str]:
  return [ "roll_name", "mean", "std_dv", "min", "max" ]

def prob_col_names( _: list[str] ) -> list[str]:
  return [ "result", "chance" ]

def to_frame( *rows, prob_cols = False ) -> DataFrame:
  return scan_csv(
    StringIO( "".join( rows ) ),
    has_header = prob_cols,
    with_column_names = prob_col_names if prob_cols else stat_col_names,
  ).collect()

def cross_joiner( roll_name: str ) -> DataFrame:
  modifier = 0
  steps = 0
  if re.match( "4d6", roll_name ):
    steps = 1
  elif re.match( "5d6", roll_name ):
    steps = 2
  elif re.match( "6d6", roll_name ):
    steps = 3
  if re.match( "^.*highest.*$", roll_name ):
    modifier = 1
  elif re.match( "^.*lowest.*$", roll_name ):
    modifier = -1
  return polars.from_dict( {
    "roll_name": roll_name,
    "modifier": modifier,
    "steps": steps,
  } )

def parse_from_anydice( filepath: str ) -> tuple[ DataFrame, DataFrame ]:
  probabilities = []
  stats = []
  with open( filepath, "r" ) as file_io:
    current_state = ParseState.NEW_ENTRY
    name = None
    csv = []
    for line in file_io:
      match ( current_state, line == "\n" ):
        case ( ParseState.NEW_ENTRY, _ ):
          stat_frame = to_frame( line )
          stats.append( stat_frame )
          name = stat_frame.item( 0, "roll_name" )
          current_state = ParseState.PROCESS_ROW
        case ( ParseState.PROCESS_ROW, False ):
          csv.append( line )
        case ( ParseState.PROCESS_ROW, True ):
          new_probs = to_frame( *csv, prob_cols = True )
          new_probs = new_probs.join( cross_joiner( name ), how = "cross" )
          probabilities.append( new_probs )
          current_state = ParseState.NEW_ENTRY
          csv = []
  return ( polars.concat( probabilities ), polars.concat( stats ).sort( "mean" ) )

( prob, stats ) = parse_from_anydice( "data.csv" )
prob.write_csv( "prob.csv" )
stats.write_csv( "stats.csv" )