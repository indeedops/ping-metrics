README
======

This makes possible to emit cross-datacenter ping metrics to datadog.

You can run this from hosts where you want to ping remote hosts and emit ping
results as a metric to DataDog or any statsd compatible daemon.

In order to run, first config file needs to be populated with the endpoint to
test ping against. You can pass '--silent' or '-s' to it to supress script
output to terminal. Then you can run this the way you like, e.g. supervisord,
init.d, nohup, etc.

Original code was taken from:
    https://gist.github.com/nambrosch/13679710eca4a268f775