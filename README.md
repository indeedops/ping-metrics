README
======

This makes possible to emit cross-datacenter ping metrics to datadog.

You can run this from hosts where you want to ping remote hosts and emit ping
results as a metric to DataDog or any statsd compatible daemon.

In order to run, first config file needs to be populated with the endpoints to
test ping against. It is done in /etc/cross_dc_metrics/config.ini file where
you can find examples.

You can increase verbosity by passing '-v', '-vv' or '-vvv' to the script.
Then you can run this the way you like, e.g. supervisord, init.d, nohup, etc.

Be default this is installed into datadog /opt/datadog-agent/embedded/bin/
directory so it could be run using the same python interpreter as datadog.

Build
=====
Build on aus-fpm6 like:
```
fpm -s python -t rpm --python-bin /opt/datadog-agent/embedded/bin/python --no-python-fix-dependencies setup.py
```
Run as:
```
/opt/datadog-agent/embedded/bin/python /opt/datadog-agent/embedded/bin/cross_dc_metrics
```
