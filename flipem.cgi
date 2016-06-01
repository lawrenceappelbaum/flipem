#! /usr/bin/perl -T

use strict;
use warnings;

use Flipem			0.10;
use Flipem::Move	0.20;

### USER INTERFACE DATA ###

use CGI;
my $q = new CGI;

my %unpackedDisc = (B => 0, C => 1, U => 2);
my @packedDisc = ("B", "C", "U");

my @collet = ("A", "B", "C", "D", "E", "F", "G", "H");
my @rownum = ("1", "2", "3", "4", "5", "6", "7", "8");
my @piece = ("/images/button_blank.png",	# 0 = empty square
					"/images/button_black.png",	# 1 = black piece
					"/images/button_white.png",	# 2 = white piece
					);  # piece to display on board

my @prevboard;  # board before previous move
my $inputMove;  # from Post

### USER INTERFACE FUNCTIONS ###

sub unpackBoard {
	for my $i (0..7) {
		for my $j (0..7) {
			$board[$i][$j] = $unpackedDisc{
				substr($q->param('Board'), ($i * 8 + $j), 1)};
		}
	}
}

sub unpackPreviousBoard {
	for my $i (0..7) {
		for my $j (0..7) {
			$prevboard[$i][$j] = $unpackedDisc{
				substr($q->param('PreviousBoard'), ($i * 8 + $j), 1)};
		}
	}
}

sub unpackPost {
	if ($q->param('Board') =~ /^[BCU]{64}$/) {
		unpackBoard;
	}
	else {
		print "Warning: Invalid Board was ",
			$q->param('Board'), ".<BR>";
	}
	
	if ($q->param('PreviousBoard') =~ /^[BCU]{64}$/) {
		unpackPreviousBoard;
	}
	else {
		print "Warning: Invalid PreviousBoard was ",
			$q->param('PreviousBoard'), ".<BR>";
	}
	
	unless ($q->param('NextPlayer') =~/^[CUE]$/) {
		print "Warning: Invalid NextPlayer was ",
			$q->param('NextPlayer'), ".<BR>";
		$q->param('NextPlayer', '');
	}

	unless ($q->param('ComputerPlaying') =~/^Black|White$/) {
		print "Warning: Invalid ComputerPlaying was ",
			$q->param('ComputerPlaying'), ".<BR>";
		$q->param('ComputerPlaying', '');
	}
	if ($q->param('ComputerPlaying') eq 'Black')
	{
		$C = 1;  # Computer playing Black
		$U = 2;  # User playing White
	}
	else {
		$U = 1;  # User playing Black
		$C = 2;  # Computer playing White
	}
	
	# Just use the A1.x part, ignore the A1.y and the values.
	$inputMove = "";
	foreach my $pn ($q->param) {
		if (($pn =~ /^([A-H][1-8])\.x$/) || ($pn =~ /^(CM)$/)) {
			$inputMove = $1;
			last;
		}
	}
	if ($inputMove eq '') {
		print "Warning: Invalid Input Move.<BR>";
	}
	
	unless ($q->param('ComputerStuck') =~/^[YN]$/) {
		print "Warning: Invalid ComputerStuck was ",
			$q->param('ComputerStuck'), ".<BR>";
		$q->param('ComputerStuck', '');
	}
	unless ($q->param('UserStuck') =~/^[YN]$/) {
		print "Warning: Invalid UserStuck was ",
			$q->param('UserStuck'), ".<BR>";
		$q->param('UserStuck', '');
	}
}

sub packBoard {
	my $packedBoard = '';
	for my $i (0..7) {
		for my $j (0..7) {
			$packedBoard .= $packedDisc[$board[$i][$j]];
		}
	}
	$q->param('Board', $packedBoard);
	print $q->hidden(-name=>'Board');
}

sub packPreviousBoard {
	my $packedBoard = '';
	for my $i (0..7) {
		for my $j (0..7) {
			$packedBoard .= $packedDisc[$prevboard[$i][$j]];
		}
	}
	$q->param('PreviousBoard', $packedBoard);
	print $q->hidden(-name=>'PreviousBoard');
}

sub packForm {
	packBoard;
	packPreviousBoard;
	print $q->hidden(-name=>'NextPlayer');
	print $q->hidden(-name=>'ComputerPlaying');
	print $q->hidden(-name=>'ComputerStuck');
	print $q->hidden(-name=>'UserStuck');
}

sub printBoard {
	my $r	= shift; # moved-to row
	my $c	= shift; # moved-to column
	my $nextMoves = shift; # possible moves for next player
	my $disc;
	my $square;
	my @tableData; 
	my @tableRow;

	# For each square on the 8 x 8 board,
	# create the contents of its HTML Table Data Cell.
	for my $i (0..7) {
		for my $j (0..7) {
		
			# Determine the style and color of disc to be placed on each square.
			# A heavier disc for the moved-to square.
			if (($i == $r) && ($j == $c)) {
				if ($board[$i][$j] == 1)
					{ $disc =
						"/images/button_black_move.png" }
				else  # board[i][j] == 2
					{ $disc =
						"/images/button_white_move.png" }
			}
			# A disc-covering-disc for a flipped square.
			elsif ($board[$i][$j] != $prevboard[$i][$j]) {
				if ($board[$i][$j] == 1)
					{ $disc =
						"/images/button_black_flip.png" }
				else  # board[i][j] == 2
					{ $disc =
						"/images/button_white_flip.png" }
			}
			# A regular disc for an unaffected square,
			# or no disc at all for an empty square.
			else {
				$disc = $piece[$board[$i][$j]];
			}
			
			# Determine the kind of square for the next players move.
			# A clickable button if this square is a valid move for the
			# next player, or an unclickable image if not.
			if ($nextMoves->[$i][$j]) {
				$tableData[$i][$j]
					= $q->image_button(
						-name=>$collet[$j] . $rownum[$i],
						-src   =>$disc);
			}
			else {
				$tableData[$i][$j] = $q->img({src=>$disc});
			}
		}
	}

	# For each row on the board, pack the contents
	# we just created into each HTML Table Data Cell.
	# The CGI method does a whole row-array at a time.
	for my $i (0..7) {
		$tableRow[$i] = $q->td($tableData[$i]);
	}

	# Create the overall HTML Table representing the 8 x 8 board.
	# The CGI method does the entire array of rows at one time.
	print $q->table({-border=>4},
		$q->Tr({-align=>"CENTER",-valign=>"CENTER"},
			\@tableRow));

	# Save the printed board state to show changes next time printed.
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			$prevboard[$i][$j] = $board[$i][$j];
		}
	}
}

# Print Board with no changes indicated.
sub printBoardFirstTime {
	my $nextMoves = shift; # possible first moves for User
	
	for (my $i = 0; $i <= 7; $i++) {
		for (my $j = 0; $j <= 7; $j++) {
			$prevboard[$i][$j] = $board[$i][$j];
		}
	}
	printBoard(-1, -1, $nextMoves);
}

sub printLowerMessage {
	print $q->table({-border=>0, -width=>250, -height=>68},
		$q->td({-align=>"CENTER", -valign=>"CENTER"}, @_) );
}

sub printComputersTurn {
	printLowerMessage(
		$q->submit(-name=>"CM", -value=>"Computer's Turn") );
}

sub printYourTurn {
	printLowerMessage( $q->p("Your Turn") );
}

sub printGameOver {
	my $uniqueMessage = shift;
	
	(my $cs, my $us) = calcscores;
	
	if ($cs > $us) {
		printLowerMessage($uniqueMessage, $q->br,
								"Game Over: Computer Won!<BR>",
								"Score: Computer $cs, You $us.");
	}
	elsif ($cs < $us) {
		printLowerMessage($uniqueMessage, $q->br,
								"Game Over: You Won!<BR>",
								"Score: You $us, Computer $cs.");
	}
	else {
		printLowerMessage($uniqueMessage, $q->br,
								"Game Over: You Tied!<BR>",
								"Score: Computer $cs, You $us.");
	}
}

# Determine and perform Computer's move.
sub computersTurn {
	my $computersMove = new Flipem::Move(\@board, $C);
	my $row;
	my $col;
	my $score;

	# Determine Computer's move.
	($row, $col, $score) = $computersMove->bestMove; 	# Also needed for flips.

	# Perform Computer's move
	updateBoard($computersMove->flipMove($row, $col));

	# Look ahead to User's next move.
	my $usersNextMove = new Flipem::Move(\@board, $U);
	$q->param('UserStuck', $usersNextMove->canMove ? 'N' : 'Y');
	
	# If the board is full, end the game,
	if (boardFull) {
		printBoard($row, $col);
		printGameOver("The board is full.");
	}
	
	# If both players are stuck, end the game,
	elsif (($q->param('ComputerStuck') eq 'Y') &&
			($q->param('UserStuck') eq 'Y')) {
		printBoard($row, $col);
		printGameOver("Neither the Computer nor you can move!");
	}

	# If just the User is stuck, he forfeits his turn.
	elsif ($q->param('UserStuck') eq 'Y') {
	
		# Look ahead to the Computer's next move.
		my $computersNextMove = new Flipem::Move(\@board, $C);
		$q->param('ComputerStuck', $computersNextMove->canMove ? 'N' : 'Y');

		# If the Computer is also stuck now, end the game.
		if ($q->param('ComputerStuck') eq 'Y') {
			printBoard($row, $col);
			printGameOver("Neither you nor the Computer can move!");
		}

		# Otherwise the Computer can move again.
		else {
			printBoard($row, $col);
			printLowerMessage("You cannot move!");
			printComputersTurn;
			$q->param('NextPlayer', 'C');
		}
	}
	
	# Otherwise the User can move next.
	else {
		printBoard($row, $col, $usersNextMove->getMoves);
		printYourTurn;
		$q->param('NextPlayer', 'U');
	}
}

# Perform User's move.
sub usersTurn {
	my $row	= shift;
	my $col		= shift;
	my $usersMove = new Flipem::Move(\@board, $U);
	my $userscore;

	# Perform the User's move.
	$usersMove->tryOneMove($row, $col); 	# Needed for flips.
	updateBoard($usersMove->flipMove($row, $col));
	
	# Look ahead to Computer's next move.
	my $computersNextMove = new Flipem::Move(\@board, $C);
	$q->param('ComputerStuck', $computersNextMove->canMove ? 'N' : 'Y');

	# If the board is full, end the game,
	if (boardFull) {
		printBoard($row, $col);
		printGameOver("The board is full.");
	}

	# If both players are stuck, end the game,
	elsif (($q->param('ComputerStuck') eq 'Y') &&
			($q->param('UserStuck') eq 'Y')) {
		printBoard($row, $col);
		printGameOver("Neither you nor the Computer can move!");
	}

	# If just the Computer is stuck, he forfeits his turn.
	elsif ($q->param('ComputerStuck') eq 'Y') {
	
		# Look ahead to User's next move.
		my $usersNextMove = new Flipem::Move(\@board, $U);
		$q->param('UserStuck', $usersNextMove->canMove ? 'N' : 'Y');
	
		# If the User is also stuck now, end the game,
		if ($q->param('UserStuck') eq 'Y') {
			printBoard($row, $col);
			printGameOver("Neither the Computer nor you can move!");
		}
			
		# Otherwise the User can move again.
		else {
			printBoard($row, $col, $usersNextMove->getMoves);
			printLowerMessage("Computer cannot move!<BR>",
										"Your turn again.");
			$q->param('NextPlayer', 'U');
		}
	}
	
	# Otherwise the Computer can move next.
	else {
		printBoard($row, $col);
		printComputersTurn;
		$q->param('NextPlayer', 'C');
	}
}

### CREATE HTML OUTPUT ###

print $q->header(-type=>"text/html", -expires=>"now");
print $q->start_html("Flip \'Em!");

# DEBUG
#foreach my $pn ($q->param) {
#	print "Param Name: $pn" , $q->br;
#	foreach my $pv ($q->param($pn)) {
#		print "Param Value: $pv", $q->br;
#	}
#}

# Start the Form.
print $q->startform("POST","flipem.cgi","application/x-www-form-urlencoded");

# First time script is run, before first move of game.
if (! $q->param) {

	# PATCH: Fix center squares. Should fix in Flipem.pm.
	$board[3][3] = 2;  # white
	$board[3][4] = 1;  # black
	$board[4][3] = 1;  # black
	$board[4][4] = 2;  #white

	# Defaults
	$q->param('NextPlayer', 'E');  # Either
	$q->param('ComputerPlaying', 'Black');  # default unless User moves first
	$q->param('ComputerStuck', 'N');  # Computer can move.
	$q->param('UserStuck', 'N');  # User can move.

	# Enable board buttons for possible first move by the User.
	# If the User makes the first move, he will become Black.
	my $nextUserMove = new Flipem::Move(\@board, 1);
	printBoardFirstTime($nextUserMove->getMoves);
	printComputersTurn;
	printLowerMessage("New game. You can go first,<BR>",
								"or let the Computer go first.");
	# Either player can make the first move.
}

# Game has started.
else {
	# Get the input.
	unpackPost;
#	print "Debug: Board is ", $q->param('Board'), ".<BR>";
#	print "Debug: PreviousBoard is ", $q->param('PreviousBoard'), ".<BR>";
#	print "Debug: NextPlayer is ", $q->param('NextPlayer'), ".<BR>";
#	print "Debug: ComputerPlaying is ", $q->param('ComputerPlaying'), ".<BR>";
#	print "Debug: Move is $inputMove.<BR>";
#	print "Debug: ComputerStuck is ", $q->param('ComputerStuck'), ".<BR>";
#	print "Debug: UserStuck is ", $q->param('UserStuck'), ".<BR>";

	# Computer Move
	if ($inputMove eq "CM") {
		computersTurn;
	} 

	# User Move
	elsif ($inputMove =~ /[A-H][1-8]/) {
	
		# If the User makes the first move of the game, he plays Black.
		# Otherwise the Computer plays Black by default.
		if ($q->param('NextPlayer') eq "E") {
			$U = 1;  # User plays Black
			$C = 2;  # Computer plays White
			$q->param('ComputerPlaying', 'White');
		}
		
		# Perform User's move.
		(my $col, my $row) = $inputMove =~ /([A-H])([1-8])/;
		$col =~ tr/A-H/0-7/;
		$row =~ tr/1-8/0-7/;
		usersTurn($row, $col);
	}
}

# Save the game state data.
packForm;

# End the Form.
print $q->endform;

print $q->end_html;
