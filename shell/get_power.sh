#!/bin/bash

node=$(hostname)
count=0
finish=0
while [ $finish -eq 0 ]; do
  start_freshness=$(cat /sys/cray/pm_counters/freshness)
  buf=$(grep ^ /sys/cray/pm_counters/*power | sed 's/:/ /;s|/sys/cray/pm_counters/||' | awk -v host=$node '
  {
    buffer = buffer host " " $1 " " $2 " " $3 " " $4 " " $5 "@@";
    if ($1  != "power")
    {
      total_power = total_power + $2; 
    }
    else
    {
      node_power = $2
    }
  }
  END {
    if (node_power > total_power){
      buffer = buffer host  " power = " node_power  " sum = "  total_power  " ### PASS";
    }
    else
    {
      buffer = buffer host  " power = " node_power  " sum = "  total_power " ###  FAIL";
    }
    print buffer
  }
  ')
  end_freshness=$(cat /sys/cray/pm_counters/freshness)
  if [[ $start_freshness -eq $end_freshness ]]; then
    echo $buf | sed 's/@@/\n/g';
    echo "$node start_freshness = $start_freshness  end_freshness = $end_freshness  count =  $count" 
  else 
    count=$(( count + 1 ))
  fi
  sleep 0.1
done

