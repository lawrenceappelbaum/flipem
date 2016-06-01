package Flipem::Move;

our $VERSION	= 0.20;
		
use strict;
use warnings;

use Flipem 0.10 qw($C $U);

# Class Data
my @STRATEGY = (					# Strategy matrix
	[ 9, 1, 8, 7, 7, 8, 1, 9 ],
	[ 1, 0, 3, 2, 2, 3, 0, 1 ],
	[ 8, 3, 5, 4, 4, 5, 3, 8 ],
	[ 7, 2, 4, 0, 0, 4, 2, 7 ],
	[ 7, 2, 4, 0, 0, 4, 2, 7 ],
	[ 8, 3, 5, 4, 4, 5, 3, 8 ],
	[ 1, 0, 3, 2, 2, 3, 0, 1 ],
	[ 9, 1, 8, 7, 7, 8, 1, 9 ] );

# Object Data
sub new {
	my $invocant = shift;
	my $callersBoard = shift;
	my $class = ref($invocant) || $invocant;
	my $self = { 
		board		=> [ ],					# Copy of caller's Board
		player	=> shift,				# Player, $C or $U
		STRAT	=> \@STRATEGY,	# Strategy matrix
		score		=> [ ],					# 8x8 of potential move scores
		flips		=> [ ]					# 8x8 of lists of potential squares to flip
	};
	# Make our own copy of the board.
	for my $i (0 .. 7) {
		for my $j (0 .. 7) {
			$self->{board}[$i][$j] = $callersBoard->[$i][$j];
		}
	}
	bless($self, $class);
	return($self);
}

# Determine best move.
sub bestMove {
	my $self = shift;

	my $besti;
	my $bestj;
	my $beststrategy;
	my $bestscore;

	# Determine score for each valid/legal move.
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			$self->tryOneMove($i, $j);
			if ($self->{score}[$i][$j] > 0) {
#				print "move: $collet[$j]$rownum[$i] ", 
#				"Strat=$STRAT[$i][$j] ",
#				"Score=$score[$i][$j]\n";
			}
		}
	}

	# Determine best stategy of all valid/legal/scorable squares.
	$beststrategy = -1;
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			if ($self->{score}[$i][$j] > 0) {     
				if ($self->{STRAT}[$i][$j] > $beststrategy) {
					$beststrategy = $self->{STRAT}[$i][$j];
				}
			}
		}
	}
#	print "move strategy=$beststrategy i=$besti j=$bestj\n";

	# Pick highest score of all squares with best strategy.
	$besti = -1;  # in case all scores are zero
	$bestj = -1;
	$bestscore = 0;
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			if ($self->{STRAT}[$i][$j] == $beststrategy) {
				if ($self->{score}[$i][$j] > $bestscore) {
					$bestscore = $self->{score}[$i][$j];
					$besti = $i;
					$bestj = $j;
				}
			}
		}
	}

	return $besti, $bestj, $bestscore;
}

# Try 1 square-move for Computer or User.
# Populate score[r][c] with number of flips.
# Populate flips[r][c] with array of squares to flip.
# Return potential score.
sub tryOneMove {
	my $self	= shift;
	my $r		= shift;
	my $c		= shift;
	my $opponent = ($self->{player} == $C) ? $U : $C;
	my $tempscore;
	my @tempflips;

	$self->{score}[$r][$c] = 0;
	$#{$self->{flips}[$r][$c]} = -1;

	if ($self->{board}[$r][$c] == 0) {  # must be on empty square
		for (my $di = -1; $di <= 1; $di++) {  # left/right
			for (my $dj = -1; $dj <= 1; $dj++) {  # up/down
				unless (($di == 0) && ($dj == 0)) {  # degen dir
					$tempscore = 0;
					undef @tempflips;
					my $i = $r + $di;
					my $j = $c + $dj;
					# Immediate neighbor must be Opponent's square.
					if ( ($i >= 0) && ($i <= 7) &&
						 ($j >= 0) && ($j <= 7) &&
						($self->{board}[$i][$j] == $opponent) ) {
						while ( ($i >= 0) && ($i <= 7) &&
								   ($j >= 0) && ($j <= 7) ) {
							if ($self->{board}[$i][$j] == $opponent) {
								$tempscore++;
								push @tempflips, ($i, $j);
							}
							# No score in this direction if hit Empty square.
							elsif ($self->{board}[$i][$j] == 0) {
								last; }
							# Eventually hit a Player's square.
							elsif ($self->{board}[$i][$j] == $self->{player}) {
								$self->{score}[$r][$c] += $tempscore;
								push @{$self->{flips}[$r][$c]}, @tempflips;
								last;
							}
							$i += $di;
							$j += $dj;
						}
					}
				}
			}
		}
	}
#	print "trymove: score=$score[$r][$c]\n";
	return $self->{score}[$r][$c];
}

# Can the player move at all?
sub canMove {
	my $self = shift;
	
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			if ($self->tryOneMove($i, $j))
				{ return 1 }
		}
	}
	return 0;
}

# 8 x 8 matrix of all possible moves the player can make.
sub getMoves {
	my $self = shift;
	my @moves;
	
	for my $i (0 .. 7) {
		for my $j (0 .. 7) {
			$moves[$i][$j] = $self->tryOneMove($i, $j) ? 1 : 0;
		}
	}
	return \@moves;
}

# Flip squares on board for selected row/col move.
# Uses $flips[row][col]. Call tryOneMove or bestMove first.
sub flipMove {
	my $self	= shift;
	my $row	= shift;
	my $col		= shift;

	$self->{board}[$row][$col] = $self->{player};
	while ( @{ $self->{flips}[$row][$col] } ) {
		$self->{board}[ shift @{ $self->{flips}[$row][$col] } ]
							 [ shift @{ $self->{flips}[$row][$col] } ]
			= $self->{player};
	}
	return $self->{board};
}

1;
