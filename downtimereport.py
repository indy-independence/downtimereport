# downtimereport.py
# Interactive measurement of downtime duration during maintenance windows etc
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import sys

import threading
import subprocess

import pyping

class Traceroute(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def set(self, host):
        self.host = host
        self.stdout = None
        self.stderr = None

    def run(self):
        p = subprocess.Popen(['mtr','-nrwc5',self.host],
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        self.stdout, self.stderr = p.communicate()

def print_downtime(downtime):
    td = downtime['stop'] - downtime['start']
    print "Downtime: {:.1f}s".format(td)
    print "Start: " + time.strftime("%H:%M:%S", time.localtime(downtime['start']))
    print "Stop:  " + time.strftime("%H:%M:%S", time.localtime(downtime['stop']))

def main():
    downtimes = []
    curdown = None

    if not len(sys.argv) == 2:
        print "Usage: downtimereport.py <ip>"
        print "Make sure your clock is synchronized with NTP before starting"
        print "Will send one ICMP every 100ms, with a timeout of 75ms. " +\
            "Reports outages longer than around 200ms."
        sys.exit(1)

    host = sys.argv[1]

    print "Performing pre-flight checks..."
    try:
        r = pyping.ping(host, count=3, timeout=1000)
        host_ip = r.destination_ip
        print "Initial ICMP test to host {} ({}): avg_rtt: {}".format(
            host,
            host_ip,
            r.avg_rtt)
    except Exception as e:
        print "Could not ping host {}".format(host)
        print str(e)
        sys.exit(2)

    if r.ret_code != 0:
        print "Could not ping host {}".format(host)
        sys.exit(3)

    if float(r.max_rtt) > 50.0:
        print "WARNING: max_rtt is over 50 ms ({}). This script will ".format(r.max_rtt) +\
            "report downtime if no response is seen in 75ms. You might get false-positives."
    
    print "Recording of downtime intervals for host {} ({}) started at {}.".format(
        host,
        host_ip,
        time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print "Press Ctrl-C to stop and report."

    try:
        trace = Traceroute()
        trace_started = False
        seq = 0
        while True:
            t1 = time.time()
            try:
                seq += 1
                r = pyping.ping_once(host_ip, seq=seq, timeout=90)
            except ZeroDivisionError:
                sleep_t = max(0, (0.1 - (time.time()) - t1))
                time.sleep(sleep_t)
                continue

            if trace_started and not trace.is_alive():
                print trace.stdout
                trace_started = False
                trace.join()
                del(trace)
                trace = Traceroute()

            if curdown and r.packet_lost != 0 and \
                    time.time() - curdown['start'] > 1.0 and \
                    not trace_started and not curdown.has_key('trace'):
                print "Downtime of more than 1s detected, trigger traceroute run"
                trace_started = True
                curdown['trace'] = True
                trace.set(host_ip)
                trace.start()
        
            if not curdown and r.packet_lost != 0:
                curdown = {}
                curdown['start'] = time.time()
            elif curdown and r.packet_lost == 0:
                if time.time() - curdown['start'] > 0.19:
                    curdown['stop'] = time.time()
                    downtimes.append(curdown)
                    print_downtime(curdown)
                curdown = None
        
            sleep_t = max(0, (0.1 - (time.time() - t1)))
            time.sleep(sleep_t)
    except KeyboardInterrupt:
        if curdown:
            curdown['stop'] = time.time()
            downtimes.append(curdown)
            print_downtime(curdown)

    print ""
    print "Aborted by user at {}".format(time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print "Number of downtimes: {}".format(len(downtimes))
    for i, downtime in enumerate(downtimes):
        td = downtime['stop'] - downtime['start']
        print "Downtime {}: {:.1f}s".format(i, td)
        print "Start: " + time.strftime("%H:%M:%S", time.localtime(downtime['start']))
        print "Stop:  " + time.strftime("%H:%M:%S", time.localtime(downtime['stop']))
    
if __name__ == "__main__":
    main()
