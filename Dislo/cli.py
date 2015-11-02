#!/usr/bin/python

import optparse
import api

class ArgumentParser:
    """
    This class parses command line options and dispatches them to the DotRoll
    API lib.
    """

    def __init__(self):
        """
        This function sets up the option parser to use for command line
        processing.
        """
        self.parser = optparse.OptionParser(description='Access the Dislo data export API 2')
        api_group = optparse.OptionGroup(self.parser,
                                         'API options',
                                         'These options modify, how the API'
                                         ' endpoint is connected')
        api_group.add_option('--apiendpoint',
                             type='string',
                             help='The endpoint URL used to access the'
                                  ' service. You don\'t normally need'
                                  ' to change this. Defaults to'
                                  ' "%default"')
        api_group.add_option('--apikey',
                             type='string',
                             help='The API key used to access the service')
        api_group.add_option('--apisecret',
                             type='string',
                             help='The API secret used to sign requests')
        self.parser.add_option_group(api_group)

        action_group = optparse.OptionGroup(self.parser,
                                            'Actions',
                                            '')
        action_group.add_option('--runreport',
                                action='store_true',
                                help='Run a stored report')
        action_group.add_option('--runquery',
                                action='store_true',
                                help='Run an SQL query')
        self.parser.add_option_group(action_group)

        param_group = optparse.OptionGroup(self.parser,
                                           'Parameters',
                                           '')
        param_group.add_option('--report',
                               help='Report ID from the custom report interface')
        param_group.add_option('--query',
                               help='SQL query to run')
        self.parser.add_option_group(param_group)

    def usage(self):
        """
        This function provides an external option to print the usage text.
        """
        self.parser.print_help()

    def error(self, message):
        """
        This function provides an external option to raise a parser error and
        terminate the program.
        """
        self.parser.error(message)

    def parse(self, args):
        """
        This function parses and validates a set of arguments.
        Returns a tupple (function, arguments)
        """
        if len(args) < 2:
            raise ArgumentError('Incorrect number of arguments')
        (options, args) = self.parser.parse_args(args)

        api_args = ['apiendpoint', 'apikey', 'apisecret']
        for i in api_args:
            if getattr(options, i) is None:
                raise ArgumentError('The --' + i + ' parameter is required')

        action_args = ['runreport', 'runquery']
        for i in action_args:
            for j in action_args:
                if i != j and getattr(options, i) and getattr(options, j):
                    raise ArgumentError('Only one action can be called at a'
                                        ' time. --' + i + ' and --' + j +
                                        ' are incompatible.')

        if getattr(options, 'runreport') and getattr(options, 'query'):
            raise ArgumentError('The --query parameter is incompatible with the --runreport option.')
        if getattr(options, 'runquery') and getattr(options, 'report'):
            raise ArgumentError('The --report parameter is incompatible with the --runquery option.')

        func = None
        for i in action_args:
            if getattr(options, i):
                func = i
        return func, options

    def call(self, func, options):
        """
        Call corresponding API function with arguments
        """
        handler = api.HTTPQueryHandler(options.apiendpoint, options.apikey, options.apisecret)
        result = ''
        if func == 'runquery':
            result = handler.custom_query(getattr(options, 'query'))
        if func == 'runreport':
            result = handler.custom_report(getattr(options, 'report'))
        return result

    def parse_and_call(self, args):
        """
        Parse arguments and call function
        """
        (func, options) = self.parse(args)
        return self.call(func, options)

class ArgumentError(Exception):
    """
    This exception indicates, that an error has occured parsing command line
    arguments.
    """

    def __init__(self, message):
        """
        Initializes the class with an error message.
        """
        self.message = message

    def __str__(self):
        """
        Returns the error message passed to the Exception in __init__()
        """
        return self.message
