my $file1=$ARGV[0];
my $file2=$ARGV[1];
open (file_1,$file1) or die "Couldn't open the file" ;

while(my $String = <file_1>)   {
   if(($String =~ /internal_channel/  or $String =~ /internal2_channel/ )and $String =~ /MASTER/ )
        {
              my @spl = split(' ', $String);
              @chain_name1= split('_', $spl[1]);
              @chain_value = split('/', $spl[9]);
              @chain_value1 = split('_sig', $chain_value[-2]);
              @chain_value2 = split('_reg', $chain_value1[1]);
               
               
if ($spl[4]=~ /FFFF/)
              {
              push (@signature_value,$chain_value2[0]);
              #printf (" %s %d %s \n " ,$chain_name1[-1] ($chain_nu)-1 $chain_val[-1] );
              } else {
                #print ("entering into else");
                $neg= int($spl[0]); 
              if ($neg > 5) {
               $signature_value_neg_1 = not($chain_value2[0]);
               #print ($chain_value_neg_1);
               } else {
             $signature_value_neg_1 = $chain_value2[0];
               }
              push (@signature_value,$signature_value_neg_1);
              #print ("$chain_name1[-1] $chain_nu $chain_value_neg_1\n" );
              #print ("$spl[1] $spl[0] $spl[-3] \n" );
             }
            ##print ("$spl[4]\n");
                              
              $subs="chain";
                 
                $a=index($chain_name1[-1], $subs);
              # print ($a);
               if($a==0) { 
              @chain_name= split('chain', $chain_name1[-1]);
              push(@chain_nu,$chain_name[-1]); #chain name
               }
               else 
               {
              push(@chain_nu,$chain_name1[-1]); #chain name
               }
             ## print ("$chain_name[-1] $spl[0]\n");
              push(@chain_pos,$spl[0]);  ##chain shift value 
             #debug  print(pop(@chain_nu));
             #debug  print ("\n");

	 } 
 } 

$size =@signature_value ;
 $size1 =@chain_pos ;
 $size2 =@chain_nu ;

   if ( ($size==$size1) and ($size==$size2)) 
   {
for ($i=1;$i<=$size;$i++)
{
  $a1=shift(@chain_nu);
  $a2=int($a1);
  $a=$a2-1;
  $c=pop(@chain_pos);
  $b=pop(@signature_value);
  printf("%s %s %0b\n", $a, $c, $b);
}

   }
   else 

     { 
       print( " ijtag_txt file size is $size and scan cell report size is $size1 ,  please check the scancell report and signature txt file not matching" );
     }

close file_1;
