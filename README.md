README
======

This makes possible to emit cross-datacenter ping metrics to datadog.
Original issue: https://bugs.indeed.com/browse/SYSAPP-1122

In order to run, first config file needs to be populated with the endpoint to
test ping against. You can pass '--silent' or '-s' to it to supress script
output to terminal.

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
