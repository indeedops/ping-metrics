#!/usr/bin/env python

try:
    from statsd import statsd
except ImportError:
    from datadog import statsd

import ConfigParser
import argparse
import logging
import socket
import subprocess

logging.basicConfig()
logger = logging.getLogger('Cross DC Metrics')


class PingMetric(object):
    """
    Class to ping given pool of hosts and emit metrics to statsd (DataDog)
    """
    def __init__(self, pool):
        """
        :param pool: Pool of servers to ping
        :type pool: dict
        """
        self.origin = socket.gethostname()
        self.dc = self.origin.split('-')[0]
        self.pool = pool

    def run(self):
        """
        This function starts the main loop.
        """
        # Construct an oping argument
        destinations = [ip for ip in self.pool]
        while 1:
            try:
                var = subprocess.check_output(['fping', '-qC5'] + destinations,
                    stderr=subprocess.STDOUT)
            except KeyboardInterrupt:
                logger.warning('Process was interrupted from keyboard')
                return 0
            except subprocess.CalledProcessError as e:
                # We don't care if fping exited with non zero exit code, but
                # we need its output
                var = e.output
            except OSError:
                logger.exception('Do you have fping installed?')
                raise
            data = (line.split() for line in var.splitlines())
            for record in data:
                try:
                    ip, name = record[0], self.pool[record[0]]
                except KeyError:
                    # Sometimes fping returns additional errors
                    logger.debug('fping message: %s', ' '.join(record))
                    continue
                logger.debug('Preparing data for %s, %s', name, ip)
                try:
                    values = [float(value) if value != '-' else 0
                        for value in record[2:]]
                    if not values:
                        continue
                except Exception as e:
                    logger.warning('Exception occurred during value unpack: %s',
                        e)
                    continue
                try:
                    positive_values = filter(lambda x: x > 0, values)
                    minimum = min(positive_values) if positive_values else 0
                    maximum = max(values)
                    average = sum(values) / len(positive_values) \
                        if positive_values else 0
                    jitter = sum(abs(values[i] - values[i-1])
                        for i in xrange(1, len(values))) / (len(values) - 1)
                    loss = sum(100/len(values) for x in values if x == 0)
                    logger.debug('Raw values for %s: %s', ip, values)
                    logger.debug('Parsed values for %s: (min, max, avg, jtr, los)'
                        '%s, %s, %s, %s, %s', ip, minimum, maximum, average,
                        jitter, loss)
                except Exception as e:
                    logger.warning('Exception occurred during calculation: %s',
                        e)
                    continue
                try:
                    statsd.gauge('pingtest.min', minimum,
                        tags=self._tags(ip, name))
                    statsd.gauge('pingtest.max', maximum,
                        tags=self._tags(ip, name))
                    statsd.gauge('pingtest.avg', average,
                        tags=self._tags(ip, name))
                    statsd.gauge('pingtest.jitter', jitter,
                        tags=self._tags(ip, name))
                    statsd.gauge('pingtest.loss', loss, tags=self._tags(ip, name))
                except AttributeError as e:
                    # Dogstatsd sometimes fails to call get_socket()
                    logger.warning('Statsd error: %s', e)


    def _tags(self, ip, name):
        """
        This generates tags to be added to the metric

        :param ip: IP or hostname of an endpoint
        :type ip: str
        :param name: Friendly name of an endpoint
        :type name: str
        """
        dc = name.split('-')[0]
        try:
            address = socket.gethostbyname(ip)
            target_type = 'private' if address.startswith('10.') else 'public'
        except:
            target_type = 'unknown'
        return ['pingtest_ip:' + ip, 'pingtest_name:' + name,
                'origin:' + self.origin, 'target_dc:' + dc,
                'target_type:' + target_type]


def main():
    parser = argparse.ArgumentParser(description='Ping metrics emitter')
    parser.add_argument('-v', '--verbosity', help="Increase the verbosity",
        action='count', default=0)
    args = parser.parse_args()
    # Configure the logging
    if args.verbosity >= 3:
        logger.setLevel(logging.DEBUG)
    elif args.verbosity >= 1:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)
    # Read the config file and get the pool of servers
    config = ConfigParser.ConfigParser()
    config.read('/etc/cross_dc_metrics/config.ini')
    pool = {}
    for name, hostname in config.items('Pool'):
        if hostname in pool:
            logger.warning('Duplicate host entry in config file')
        pool[hostname] = name
    logger.debug('Pool generated: %s', pool)
    # Start the app
    ping_metric = PingMetric(pool)
    ping_metric.run()

if __name__ == '__main__':
    main()
