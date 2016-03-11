import sys

def main():
    """The main routine which adds additional module to the sys.path"""
    sys.path.append('/usr/lib/python2.6/site-packages/')
    from cross_dc_metrics import ping_metric
    ping_metric.main()

if __name__ == "__main__":
    main()