# downtimereport
Measures downtime duration during maintenance windows etc. Example:

::

   sudo ./downtimereport.py 10.100.2.101
   Performing pre-flight checks...
   Initial ICMP test to host 10.100.2.101 (10.100.2.101): avg_rtt: 3.696
   Recording of downtime intervals for host 10.100.2.101 (10.100.2.101) started at 2020-02-19 12:43:00 CET.
   Press Ctrl-C to stop and report.
   Downtime: 0.6s
   Start: 12:43:03
   Stop:  12:43:03
   Downtime: 0.8s
   Start: 12:43:08
   Stop:  12:43:09
   Downtime: 0.3s
   Start: 12:43:13
   Stop:  12:43:13
   Downtime: 0.4s
   Start: 12:43:18
   Stop:  12:43:18
   ^C
   Aborted by user at 2020-02-19 12:43:23 CET
   Number of downtimes: 4
   Downtime 0: 0.6s
   Start: 12:43:03
   Stop:  12:43:03
   Downtime 1: 0.8s
   Start: 12:43:08
   Stop:  12:43:09
   Downtime 2: 0.3s
   Start: 12:43:13
   Stop:  12:43:13
   Downtime 3: 0.4s
   Start: 12:43:18
   Stop:  12:43:18
 
