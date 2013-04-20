#!/usr/bin/env perl -w

use strict;

my $c = shift;
my $word = "";
my $count = 0;
open my $gzcat_fh, '-|', "/usr/bin/gzcat googlebooks-eng-all-1gram-20120701-$c.gz" or die $!;
while (<$gzcat_fh>) {
  chomp;
  my @F = split ' ';
  $F[0] =~ s/[_.].*//; 
  next if $F[0] =~ /[A-Z]/; 
  if ($F[0] ne $word) { 
    print "$word\t$count\n"; 
    $count = 0;
    $word = $F[0];
  } 
  $count += $F[2];
}
close $gzcat_fh or die $!;
