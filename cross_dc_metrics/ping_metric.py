#!/usr/bin/env python
#
# Original code was taken from
# https://gist.github.com/nambrosch/13679710eca4a268f775
#

try:
    from statsd import statsd
except ImportError:
    from datadog import statsd

import ConfigParser
import argparse
import multiprocessing
import socket
import subprocess


class PingMetric(object):
    """
    Class to ping given pool of hosts and emit metrics to statsd (DataDog)
    """
    def __init__(self, pool, silent=True):
        self.origin = socket.gethostname()
        self.pool = pool
        self.silent = silent
    
    def run(self):
        """
        This function starts the main loop.
        """
        jobs = []
        for i in self.pool:
            p = multiprocessing.Process(target=self._worker, args=(i[0],i[1]))
            jobs.append(p)
            p.start()
            if self.silent:
                print 'thread started for: ' + i[0] + ' (' + i[1] + ')'
    
    def _worker(self, name, ip):
        """
        One worker will spawn per-ip.
        
        :param name: Friendly name of the host
        :type name: str
        :param ip: IP address or the hostname of the ping endpoint
        :type ip: str
        """
        p = multiprocessing.current_process()
    
        while 1:
            try:
                var = subprocess.check_output('ping -q -c 5 -t 20 ' + ip,
                                              shell=True).splitlines(True)
            except KeyboardInterrupt:
                if self.silent:
                    print 'died'
                return 0
            except:
                (var, min, avg, max, jitter, loss) = ('', '', '', '', '', '')
    
            for line in var:
                if "round-trip" in line or "rtt" in line:
                    split = line.replace('/',' ').split()
                    (min, avg, max, jitter) = (split[6], split[7], split[8],
                                               split[9])
    
                elif " packets received, " in line:
                    split = line.replace('%','').split()
                    loss = split[6]
    
                elif " received, " in line:
                    split = line.replace('%','').split()
                    loss = split[5]
    
            if len(var) > 0 and len(min) > 0 and len(avg) > 0 \
                    and len(max) > 0 and len(jitter) > 0 and len(loss) > 0:
                if self.silent:
                    print ip, min, avg, max, jitter, loss
                statsd.gauge('testping.min', min, tags=self._tags(ip, name))
                statsd.gauge('testping.max', max, tags=self._tags(ip, name))
                statsd.gauge('testping.avg', avg, tags=self._tags(ip, name))
                statsd.gauge('testping.jitter', jitter, tags=self._tags(ip,
                                                                       name))
                statsd.gauge('testping.loss', loss, tags=self._tags(ip, name))
            else:
                if self.silent:
                    print 'no data for', ip
                statsd.gauge('testping.loss', '100', tags=self._tags(ip, name))


    def _tags(self, ip, name):
        """
        This generates tags to be added to the metric
        
        :param ip: IP or hostname of the endpoint
        :type ip: str
        :param name: Friendly name of the endpoint
        :type name: str
        """
        return ['testping_ip:' + ip, 'testping_name:' + name,
                'origin:' + self.origin]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ping metrics emitter')
    parser.add_argument('-s', '--silent', help="supress output to stdout",
        action='store_false')
    args = parser.parse_args()
    # Read the config file and get the pool of servers
    config = ConfigParser.ConfigParser()
    try:
        config.read('/etc/cross_dc_metrics/config.ini')
    except ImportError:
        config.read('config.ini')
    pool = []
    for name, hostname in config.items('Pool'):
        pool.append([name, hostname])
    # Start the app
    ping_metric = PingMetric(pool, **vars(args))
    ping_metric.run()