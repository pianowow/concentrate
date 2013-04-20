#!/usr/bin/env perl -w

# given a sorted file of words on STDIN (like /usr/share/dict/words)
# prints out matching lines from words-all.txt


use strict;
$| = 1;
my ($freqWord, $freqLetter, $freq, $freqFh, $word);
open $freqFh, '<', "words-all.txt" or die $!;

while (!eof(*STDIN) and !eof($freqFh)) {
  if ($freqWord gt $word) {
    ($word) = advance(*STDIN);
  } elsif ($freqWord eq $word) {
    print "$freqWord\t$freq\n";
    ($word) = advance(*STDIN);
    ($freqWord, $freq) = freqAdvance();
  } elsif ($freqWord lt $word) {
    ($freqWord, $freq) = freqAdvance();
  }
}

sub freqAdvance {
  my $line = advance($freqFh);
  my ($word, $freq) = split /\t/, $line;
  return ($word, $freq);
}

sub advance {
  my ($fh) = @_;
  my $line = <$fh>;
  chomp($line);
  return $line;
}

