perl -00e 'print map { $_->[0] } sort { $a->[1] <=> $b->[1] } map { chomp; [ "$_\n\n", /\n\D*(\d+)/ ] } <>' $1
