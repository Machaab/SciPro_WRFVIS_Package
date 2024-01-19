""" contains command line tools of WRFvis

Manuela Lehner
Andrea Wiech
November 2023
"""

import sys
import webbrowser

import wrfvis

HELP = """wrfvis_gridcell: Visualization of WRF output at a single selected grid cell.

Usage:
   -h, --help                       : print the help
   -v, --version                    : print the installed version
   -p, --parameter [PARAM]          : WRF variable to plot
   -l, --location [LON] [LAT] [HGT] : location and height above ground of the grid 
                                      cell for which to plot the data
   -r, --radius [RAD]               : radius (in meter) around the location for which the 
                                      gridcells are to be analyzed 
   -t, --timeindex [Time]           : Time for extracting the vertical profile  for SKEWT
   --no-browser                     : the default behavior is to open a browser with the
                                      newly generated visualisation. Set to ignore
                                      and print the path to the html file instead
"""


def gridcell(args):
    """The actual wrfvis_gridcell command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    # converts command line arguments paramter, location, raduis if entered as 
    # '--parameter', '--location', '--radius', '--timeindex' 
    # to associated shortcut '-p', '-l', '-r', '-t'
    if '--parameter' in args:
        args[args.index('--parameter')] = '-p'
    if '--location' in args:
        args[args.index('--location')] = '-l'
    if '--radius' in args:
        args[args.index('--radius')] = '-r'
    if '--timeindex' in args:
        args[args.index('--timeindex')] = '-t'

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('wrfvis_gridcell: ' + wrfvis.__version__)
        print('Licence: public domain')
        print('wrfvis_gridcell is provided "as is", without warranty of any kind')
        
    elif ('-p' in args) and ('-l' in args) and ('-t' in args):
        # if command line arguments '-p', '-l'  and '-t' are entered, assign 
        # the values to variablesand generate a html with all functionalities 
        # of the package
        param = args[args.index('-p') + 1]
        lon = float(args[args.index('-l') + 1])
        lat = float(args[args.index('-l') + 2])
        zagl = float(args[args.index('-l') + 3])
        timeindex = int(args[args.index('-t') + 1])
        if '-r' in args:
            rad = float(args[args.index('-r') + 1])
            html_path = wrfvis.write_html(param, lon, lat, zagl, rad, timeindex)
        else:
            html_path = wrfvis.write_html(param, lon, lat, zagl, timeindex)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
                
    elif ('-p' in args) and ('-l' in args):
        # if command line arguments '-p', '-l' are entered, assign
        # the values to variables
        param = args[args.index('-p') + 1]
        lon = float(args[args.index('-l') + 1])
        lat = float(args[args.index('-l') + 2])
        zagl = float(args[args.index('-l') + 3])
        if '-r' in args:
            # if radius is entered call write_html_multiple_gridcell function 
            # with radius
            rad = float(args[args.index('-r') + 1])
            html_path = wrfvis.write_html_multiple_gridcell(param, lon, lat, zagl, rad)
        else:
            # if no radius is entered call write_html_multiple_gridcell function
            # without radius
            html_path = wrfvis.write_html_multiple_gridcell(param, lon, lat, zagl)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
            
    
    elif  ('-l' in args) and  ('-t' in args):
        # if command line arguments -l and -t are entered, assign
        # the values to variables
        time_index = int(args[args.index('-t') + 1])
        lon = float(args[args.index('-l') + 1])
        lat = float(args[args.index('-l') + 2])
        #  write html for the skew T
        html_path = wrfvis.write_html_skewT(lon, lat, time_index)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
    
    elif ('-l' in args):
        # if command line arguments -l is entered, assign
        # the values to variables
        lon = float(args[args.index('-l') + 1])
        lat = float(args[args.index('-l') + 2])
        # write html for the snowcheck
        html_path = wrfvis.write_html_snowcheck(lon, lat)
        if '--no-browser' in args:
            print('File successfully generated at: ' + html_path)
        else:
            webbrowser.get().open_new_tab('file://' + html_path)
        

        
    else:
        print('wrfvis_gridcell: command not understood. '
              'Type "wrfvis_gridcell --help" for usage information.')

def wrfvis_gridcell():
    """Entry point for the wrfvis_gridcell application script"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is way above the purpose of this package
    gridcell(sys.argv[1:])
