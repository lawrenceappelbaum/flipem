#! /usr/bin/perl

use strict;
use warnings;

use Flipem			0.10;
use Flipem::Move	0.10;

### USER INTERFACE DATA ###

my @header = (
   "-------------------------------------\n",
   "|   | A | B | C | D | E | F | G | H |\n",
   "|---+---+---+---+---+---+---+---+---|\n" );
my @collet = ("A", "B", "C", "D", "E", "F", "G", "H");
my @rownum = ("1", "2", "3", "4", "5", "6", "7", "8");
my @piece = (" ", "C", "U");  # piece to display on board
my @prevboard;  # board before previous move


### USER INTERFACE FUNCTIONS ###

sub printboard {
   my $r = $_[0];
   my $c = $_[1];
   my $n;
   my $b;

   print $header[0];
   print $header[1];
   for (my $i = 0; $i <= 7; $i++)
   {
      print $header[2];
      $n = $i + 1;
      print "| $n ";
      for (my $j = 0; $j <= 7; $j++)
      {
         if (($i == $r) && ($j == $c)) {
            $b = "*"; }
         elsif ($board[$i][$j] != $prevboard[$i][$j]) {
            $b = "-"; }
         else { $b = " "; }
         print "|$b$piece[$board[$i][$j]]$b";
      }
      print "|\n";
   }
   print $header[0];

   for (my $i = 0; $i <= 7; $i++) {
      for (my $j = 0; $j <= 7; $j++) {
         $prevboard[$i][$j] = $board[$i][$j];
      }
   }
}

sub printboard_first_time {
   for (my $i = 0; $i <= 7; $i++) {
      for (my $j = 0; $j <= 7; $j++) {
         $prevboard[$i][$j] = $board[$i][$j];
      }
   }
   printboard(-1, -1);
}

sub printGameOver {
	(my $cs, my $us) = calcscores;
	if ($cs > $us) {
		print "Game Over: Computer Won!\n";
		print "Score: Computer $cs, You $us.\n";
	}
	elsif ($cs < $us) {
		print "Game Over: You Won!\n";
		print "Score: You $us, Computer $cs.\n";
	}
	else {
		print "Game Over: You Tied!\n";
		print "Score: Computer $cs, You $us.\n";
	}
}


# Determine and perform Computer Move.
sub computerMove {
	my $compMove = new Flipem::Move(\@board, $C);
	my $row;
	my $col;
	my $score;
	
	# Pretend Computer is thinking.
	{
		# display string without linefeed
		local $| = 1;  # $AUTOFLUSH = 1
		print "\nComputer thinking . . .";
	}
	sleep 2;
	print "\n";

	# Can the Computer move at all?
	if ($compMove->canMove) {
		# Determine Computer Move.
		($row, $col, my $score) = $compMove->bestMove;
		
		# Perform Computer Move.
		updateBoard($compMove->flipMove($row, $col));
		print "\nComputer's move was ",
				"$collet[$col]$rownum[$row]:\n";
		printboard($row, $col);
		return 1;
	}
	else {
		print "Computer cannot move!\n";
		return 0;
	}
}

# Input and perform User move.
sub usermove {
	my $us = shift; # user input string, passed only maybe on first move
	my $userMove = new Flipem::Move(\@board, $U);
	my $ur;
	my $uc;
	my $userscore;

	if ($userMove->canMove) {
		unless ($us) { # Input by game() for first move.
			# Input user move.
			print "\nYour move (A1, B2, etc.): ";
			$us = <>;
		}
		while (1) {
			if (($uc, $ur) = $us =~ /([a-hA-H]).*([1-8])/) {
				$uc =~ tr/a-hA-H/0-70-7/;
				$ur =~ tr/1-8/0-7/;
            	if ($userscore = $userMove->tryOneMove($ur, $uc)) {
					last;
				}
				else {
					print "\nSorry, that's not a legal move.\n";
					next;
				}
			}
			elsif ($us =~ /pass/) { return 0 } # Debug
			else {
				print "\nSorry, that's not a valid move.\n";
				print "Valid moves are from A1 to H8.\n";
				next;
			}   
		}
		continue {
			print "\nTry again (A1, B2, etc.): ";
			$us = <>;
		}

		# Perform user move.
		updateBoard($userMove->flipMove($ur, $uc));
		print "\nYour move was $collet[$uc]$rownum[$ur]:\n";
		printboard($ur, $uc);
		return $userscore;
	}
	else {
		print "You cannot move!\n";
		return 0;
	}
}

# Play the game.
sub game {
	my $nextPlayer;
	my $compStuck = 0;
	my $userStuck = 0;

	printboard_first_time;
	print "New game. You can go first (A1, B2, etc.),\n",
			"or press Enter to let the Computer go first: ";
	my $userString  = <>;
	chomp $userString;
	if ($userString eq "") { $nextPlayer = $C }
	else { $nextPlayer = $U }
	
	until (boardFull || ($compStuck && $userStuck)) {
		if ($nextPlayer == $C) {
			# Determine and perform Computer move.
			$compStuck = ! computerMove;
			$nextPlayer = $U;
		}
		elsif ($nextPlayer == $U) {
			# Input and perform User move.
			$userStuck = ! usermove($userString);
			$nextPlayer = $C;
		}
		$userString = ""; # only used once, if at all
	}

	printGameOver;
}

game;
