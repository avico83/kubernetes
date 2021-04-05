#!/usr/bin/env python
__author__ = 'avic'

import argparse
import textwrap
import time
import sys
import texttable as tt
import os
import logging
from kubernetes import client, config

# import the Kubernetes library used to connect to client

FILE_NAME = 'resolver'


def option_parser():
    """
    The function show's the option parser menu
    :return: the options
    """
    # ================= Action ====================

    parser = argparse.ArgumentParser(usage='', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''\
        Available usages are:

        show:
           resolver --pod-ip <ip> --dc <dc_name> --namespace <namespace>
           resolver --show --ns
     '''))

    # ================= Mandatory Parameters ====================
    actions = parser.add_mutually_exclusive_group(required=True)
    if len(sys.argv) < 2:
        parser.print_help()
    actions.add_argument("--show",
                         help="Show information of serial and dc",
                         action="store_true",
                         dest="show")
    mandatory = parser.add_argument_group('Actions', 'You must choose one of the following actions:')
    mandatory.add_argument("--dc",
                           action="store",
                           type=str,
                           dest="datacenter",
                           help="Use --show --dcs to get the list of dcs")
    mandatory.add_argument("--pod-ip",
                           action="store",
                           type=str,
                           dest="pod_ip")
    mandatory.add_argument("--namespace",
                           action="store",
                           type=str,
                           dest="namespace")
    optional_parameters = parser.add_argument_group('Optional Parameters')
    optional_parameters.add_argument("--ns",
                                     action="store_true",
                                     dest="ns",
                                     help="get the list of available namespaces")
    opt = parser.parse_args()
    return opt


def options_validation(k8s_config):
    """
    This function will parse the CLI options, and run the actual function on Resolver tools.
    """
    if options.show:
        if options.ns:
            logging.info('user runs show ns command')
            print(get_ns(k8s_config))  # print the available namespaces from the cluster
            end_time = time.time()  # print the end time of the process
            print('Resolver runtime was {} seconds'.format(int(end_time - start_time)))
            exit(0)
        if not options.datacenter:
            logging.info('Datacenter was not typed')
            print("You must choose dc, the options are:\n{}".format(lst_dcs()))
            end_time = time.time()
            print('Resolver runtime was {} seconds'.format(int(end_time - start_time)))
            exit(1)


def lst_dcs():
    """
    ** For future use, This function prints prints the list of available DCS
    :return: dc name
    """
    lst_dc = ['IL', 'FR', 'SY', 'CH']
    return lst_dc


def get_ns(ns):
    """
    This function gets a call and return the list of available Namespaces in a cluster
    :return: ns name
    """
    lst_ns = []
    for i in ns.items:
        lst_ns.append(i.metadata.name)
    return lst_ns


def load_k8s_config():
    """
    This function loads the configs of the k8s cluster
    :return: all pods for all namespaces
    """
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        ns = v1.list_namespace()
        return pods, ns
    except IOError as e:
        print(e)
    except client.ApiException as e:
        print(e)


def get_pods(options, ret):
    """
    :param options: Get the options from the user cli and looks for the relevant ip
    :param ret: get the kubernetes configs and use them to access the cluster
    :return: none, prints the name and namespace if found
    """
    found_pod = False
    try:
        tab = tt.Texttable()
        tab.header(["Pod's Name", "Namespace"])
        for i in ret.items:
            if options.pod_ip in i.status.pod_ip:
                found_pod = True
                tab.add_row([i.metadata.name, i.metadata.namespace])
                print(tab.draw())
                end_time = time.time()
                print('Resolver runtime was {} seconds'.format(int(end_time - start_time)))
        if not found_pod:
            print("Cannot find specific pod ip to name")
            end_time = time.time()
            print('Resolver runtime was {} seconds'.format(int(end_time - start_time)))
    except IOError as e:
        print(e)
    except client.ApiException as e:
        print(e)


if __name__ == "__main__":
    try:
        logging.basicConfig(filename='logs', level=logging.DEBUG)
        logging.info("Starting %s" % FILE_NAME)
        options = option_parser()
        logging.info(options)
        start_time = time.time()
        pods, ns = load_k8s_config()
        options_validation(ns)
        get_pods(options, pods)
    except KeyboardInterrupt as e:
        print ('Goodbye!')
        exit(1)
    except Exception as e:
        print (e)
        logging.exception(e)
        exit(1)
