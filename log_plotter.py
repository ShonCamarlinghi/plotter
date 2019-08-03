import os
import fnmatch
import re
import functools
import itertools
import shutil
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# logDir = '/Users/iris7/Sand/PycharmProjects/plotter/logDir'
# logName = 'traceroute_perf.sh.8266.run'
# awkScript = 'avg.awk'
home = '/Users/iris7/Sand/PycharmProjects/plotter'
topLogDir = '/Users/iris7/Sand/logDir'  # root dir with logs
patterns = [r'*traceroute*run',  r'1G*iperf', r'100Mb*iperf*']

# patterns = {r'*traceroute*run': 'avg.awk',
#               r'1G*iperf': 'avg_iperf_Gbits.awk',
#               r'100Mb*iperf*': 'avg_iperf_mbits.awk',
#               }

def main():
    timestamp = "{:%Y_%m_%d}".format(datetime.now())
    print(timestamp)

    # prepare resultDir to store output files
    resultDir = os.path.join(topLogDir, 'resultDir')
    readmeTxt = os.path.join(topLogDir, 'README.txt')
    # if os.path.exists(resultDir):
    #     print("%s already exists", resultDir)
    # else:
    #     os.makedirs(resultDir)
    #
    if os.path.exists(resultDir):
        backup_delete = input("\n\nlet's backup or delete old results %s before we process raw data, \nenter 'b' to back up or 'd' to delete: " % resultDir)
        if 'b' in backup_delete:
            resultdir_backup = resultDir + '_backup' + timestamp
            print("saving your previous test results to %s" % resultdir_backup)
            os.rename(resultDir, resultdir_backup)

            with open(readmeTxt) as readme:
                readme.write("\n\nbacked up previous test results to %s. \n" % resultdir_backup)
            os.makedirs(resultDir)
          #  except:
              #  raise exception
        elif 'd' in backup_delete:
            print("you chose to delete content of previous in %s" % resultDir)
            shutil.rmtree(resultDir)
            os.makedirs(resultDir)
    else:
        os.makedirs(resultDir)

    BAD_DATA = os.path.join(topLogDir, 'BAD_DATA.txt')  # record of logs that are too short

    for logName in searchTree(topLogDir, patterns):
        print(logName)
        num_lines = sum(1 for line in open(logName))
        if num_lines < 1000:
            print(logName, "has only %d lines, please check your log and try again\n" % (num_lines),
                  "writing info to BAD_DATA.txt\n")
            with open(BAD_DATA, 'a+') as fo:
                fo.writelines(logName)
        else:
            logCleaned, logPlot, resultSubdir = awk_traceroute_log_cleaner(logName, resultDir)
            logData, min, max, avg, mode = loadData(logCleaned)
            plotData(resultDir, logName, logData, logPlot, min, max, avg, mode)



    print("Done processing data.. ")
    print("Following files were too short to process:")
    fo = open(BAD_DATA, 'a+')
    for items in fo.readlines():
        print(items.strip())
    fo.close()

    print("Copies of all plots saved in", resultDir)


############################# FUNCTIONS ################################

def awk_traceroute_log_cleaner( logName, resultDir ):
    # input var type check USE @beartype
    # print("input var type check for function \n"
    #       "def awk_traceroute_log_cleaner(logName, resultDir \n",
    #       (type(logName), type(resultDir)))

    awk_script = 'avg.awk'
    awkFullPath = os.path.join(home, awk_script)

    resultSubdir = os.path.join(resultDir, logName + '_out')  # directory for post-processed log and plot
    if os.path.exists(resultSubdir):
        print("%s\n already exists", resultSubdir)
    else:
        os.makedirs(resultSubdir)
    logCleaned = os.path.join(resultSubdir, os.path.basename(logName) + '_CLEANED.txt')
    logPlot = os.path.join(resultSubdir, os.path.basename(logName) + '_plot.png')

    cmd = 'awk -f ' + awkFullPath + ' ' + logName + ' > ' + logCleaned  # raw log processed to cleaned
    os.system(cmd)
    print("Extracted data from: %s\n to: %s\n Plot file: %s\n " % (logName, logCleaned, logPlot))

    return logCleaned, logPlot, resultSubdir


def loadData(logCleaned):
    logData = np.loadtxt(logCleaned, dtype=float)  # load data from cleaned text file
    print("Loaded log data, \nGetting stats... ")
    # get data stats
    min = logData.min()
    max = logData.max()
    avg = np.average(logData)
    mode = (stats.mode(logData)[0][0])
    # print logData.dtype, logData.size, logData.shape, logData.ndim
    print("Log stats:\n")
    print("min: %.3f\nmax: %.3f\navg: %.3f\nmode: %.3f << most of the data points is close to this number\n" % \
          (min, max, avg, mode))
    return logData, min, max, avg, mode


def plotData(resultDir, logName, logData, logPlot, min, max, avg, mode):
    # logData is np array; logPlot is a string filename to save plot to
    # fonts
    font = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 10, }
    # xlabel
    plt.title(logName, fontdict=font, size=16)
    plt.xlabel('Time (hr)\n\nStats (in ms):     min: %.3f    max: %.3f   avg: %.3f   mode: %.3f' %
               (min, max, avg, mode), fontdict=font)
    print("logData size is: ", logData.size)
    xIndexSeconds = [i for i in range(logData.size)]
    xIndexHours = [i * 3600 for i in range(round(logData.size / 3600))]
    plt.xticks(xIndexHours,
               [i for i in range(logData.size)])
    # ylabel
    plt.ylabel('TCP round-trip latency (ms)', fontdict=font)

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    plt.subplots_adjust(bottom=0.15)

    # Load data to the plot
    plt.scatter(xIndexSeconds, logData, color='blue', marker='.')

    # Set picture size, dpi, etc,
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10,
                        forward=True)  # (forward = True) for data that already fitted in default scatter or plot size, to take new window size
    fig.savefig(logPlot, dpi=500, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches=None, pad_inches=0.1,
                frameon=None)

    plt.close()  # done plotting.
    print("\nSaved plot in ", logPlot)
    os.system("cp " + logPlot + " " + resultDir) # save copy in resultDir


def findFile_and_rename(value, pattern, patternL):
    for root, dirs, files in os.walk(value, topdown=True):
        for name in dirs:
            for fn in fnmatch.filter(files, pattern):
                filename = os.path.join(value, fn)

                nn = re.sub(patternL, '', fn)
                print(nn)
                newFilename = os.path.join(value, nn)
                print("Renaming %s to %s" % (fn, nn))
                os.rename(filename, newFilename)
            print("Done renaming files in %s" % value)


def searchTree(dir_path: str=None, patterns: [str]=None) -> [str]:
    """
    Returns a generator yielding files matching the given patterns
    :type dir_path: str
    :type patterns: [str]
    :rtype : [str]
    :param dir_path: Directory to search for files/directories under. Defaults to current dir.
    :param patterns: Patterns of files to search for. Defaults to ["*"]. Example: ["*.json", "*.xml"]
    """
    path = dir_path or "."
    path_patterns = patterns or ["*"]

    for root_dir, dir_names, file_names in os.walk(path):
        filter_partial = functools.partial(fnmatch.filter, file_names)

        for file_name in itertools.chain(*map(filter_partial, path_patterns)):
            yield os.path.join(root_dir, file_name)


if __name__ == '__main__':
    main()
