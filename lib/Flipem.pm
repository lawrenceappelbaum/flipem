package	Flipem;
require		Exporter;

our @ISA		= qw(Exporter);
our @EXPORT	=
	qw(@board $C $U updateBoard boardFull calcscores);
our $VERSION	= 0.10;
		
use strict;
use warnings;

### GAME LOGIC DATA ###

# Public Data

our @board = (
	[ 0, 0, 0, 0, 0, 0, 0, 0 ],
	[ 0, 0, 0, 0, 0, 0, 0, 0 ],
	[ 0, 0, 0, 0, 0, 0, 0, 0 ],
	[ 0, 0, 0, 1, 2, 0, 0, 0 ],
	[ 0, 0, 0, 2, 1, 0, 0, 0 ],
	[ 0, 0, 0, 0, 0, 0, 0, 0 ],
	[ 0, 0, 0, 0, 0, 0, 0, 0 ],
	[ 0, 0, 0, 0, 0, 0, 0, 0 ] );

our $C = 1;  # Computer
our $U = 2;  # User

### GAME LOGIC FUNCTIONS ###

# Public Functions

# Update the board.
sub updateBoard {
	my $newBoard = shift;
	for my $i (0 .. 7) {
		for my $j (0 .. 7) {
			$board[$i][$j] = $newBoard->[$i][$j];
		}
	}
}

# Are all squares are filled?
sub boardFull {
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			if ($board[$i][$j] == 0) {
				return 0;
			}
		}
	}
	return 1;
}

# Calculate scores.
sub calcscores {
	my $cs = 0;
	my $us = 0;
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			if ($board[$i][$j] == $C) {$cs++}
			elsif ($board[$i][$j] == $U) {$us++}
		}
	}
	return $cs, $us;
}

1;
