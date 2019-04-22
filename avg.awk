awk 

BEGIN{
sum = 0.0
avg_total = 0.0
longLatencyLines = 0.0
dropsToZero = 0.0
}
{
if ( /ms/ )  {   
    
	avg = ($4 + $6 + $8)/3.0
    print avg

    sum = sum + $4 +$6 +$8
	
 }
}
END{
#print "-1.0"
#print sum/(NR*1.5)
#print NR/2
}
