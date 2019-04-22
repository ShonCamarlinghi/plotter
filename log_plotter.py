import os, os.path, fnmatch, re, shutil, glob, time
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# avg_total 0.389053  (without rounding, done in awk)

# logDir = '/Users/iris7/Sand/PycharmProjects/plotter/logDir'
# logName = 'traceroute_perf.sh.8266.run'
# awkScript = 'avg.awk'
home = '/Users/iris7/Sand/PycharmProjects/plotter'
topLogDir = '/Users/iris7/Sand/PycharmProjects/plotter/logDir'  # root dir with logs
pattern = '*traceroute*'


# r'*traceroute*' : 'avg.awk',
# r'1G*iperf' : 'avg_iperf_Gbits.awk',
# r'100Mb*iperf*' : 'avg_iperf_mbits.awk'

def main():
    BAD_DATA = os.path.join(home, 'BAD_DATA.txt')  # record of logs that are too short
    os.chdir(home)
    # prepare resultDir to store output files
    resultDir = os.path.join(home, 'resultDir')
    if os.path.exists(resultDir):
        print("%s already exists", resultDir)
    else:
        os.makedirs(resultDir)

    #     backup_delete = input("\n\nlet's backup or delete old results %s before we process raw data, \nenter b to back up or d to delete: " % resultdir)
    #     if 'b' in backup_delete:
    #         try:
    #             resultdir_backup = resultdir + '_backup' + str(time.time())
    #             print("saving your previous test results to %s" % resultdir_backup)
    #             os.rename(resultdir, resultdir_backup)
    #             with open(resultdir + "/readme.txt", "a+") as readme:
    #                 readme.write("\n\nbacked up previous test results to %s. \n" % resultdir_backup)
    #             os.makedirs(resultdir)
    #         except oserror as oserror:
    #             raise e
    #     elif 'd' in backup_delete:
    #         print("you chose to delete content of previous checksum test in %s" % resultdir)
    #         shutil.rmtree(resultdir)
    #         os.makedirs(resultdir)
    # else:
    #     os.makedirs(resultdir)
    #

    # Go to raw log directory and open file for processing
    os.chdir(topLogDir)
    os.listdir(topLogDir)


    for root, dirs, files in os.walk(topLogDir, topdown=True):
        print(root, dirs, files)
        # for dirName in dirs:
        # print dirName
        for filename in fnmatch.filter(files, pattern):
            # print filename
            # filename = os.path.join(name, fn)
            logDir = os.getcwd()
            logName = filename
            print(logDir, logName)
            logCleaned, logPlot, resultSubdir = awk_traceroute_log_cleaner(pattern, logDir, logName, resultDir, BAD_DATA)
            logData, min, max, avg, mode = loadData(logCleaned)
            plotData(logName, logData, logPlot, min, max, avg, mode)

        print("Done processing data.. ")
        print("Following files were too short to process:\n")
        fo = open(BAD_DATA, 'a+')
        for items in fo.readlines():
            print(items.strip())
        fo.close()


######## functions ########

def awk_traceroute_log_cleaner(pattern, logDir, logName, resultDir, BAD_DATA):
    """

    :type logDir: object
    """
    # type: (object, object, object) -> object;
    #input var type check
    print("input var type check for function \n"
          "def awk_traceroute_log_cleaner(pattern, logDir, logName, resultDir, BAD_DATA)\n",
          type(pattern), type(logDir), type(logName), type(resultDir), type(BAD_DATA))



    # exit if line count < 1000 in the raw log
    os.chdir(logDir)
    num_lines = sum(1 for line in open(logName))
    if num_lines < 1000:
        print(logName, "has only %d lines, please check your log and try again\n" % (num_lines),
              "writing info to BAD_DATA.txt\n")
        print(type(BAD_DATA))
        fo = open(BAD_DATA, 'a+')
        fo.write(logName)
        fo.close()

        with open(BAD_DATA, 'a+') as fo:
            fo.writelines(logName)
    else:
    # awk_tools = {r'*traceroute*': 'avg.awk',
    #              r'1G*iperf': 'avg_iperf_Gbits.awk',
    #              r'100Mb*iperf*': 'avg_iperf_mbits.awk'
    #              }
    # for key in awk_tools:
    #     if pattern == key:
    #         s = awk_tools[key]
    #         print(s)
        awk_script = 'avg.awk'
        awkFullPath = os.path.join(home, awk_script)
        logFullPath = os.path.join(logDir, logName)
        resultSubdir = os.path.join(resultDir, logName + '_out')  # directory for post-processed log and plot
        if os.path.exists(resultSubdir):
            print("%s\n already exists", resultSubdir)
        else:
            os.makedirs(resultSubdir)
        logCleaned = os.path.join(resultSubdir, logName + '_CLEANED.txt')
        logPlot = os.path.join(resultSubdir, logName + '_plot.png')

        cmd = 'awk -f ' + awkFullPath + ' ' + logFullPath + ' > ' + logCleaned  # raw log processed to cleaned
        os.system(cmd)
        print("Extracted data from: %s\n to: %s\n Plot file: %s\n " % (logFullPath, logCleaned, logPlot))

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


def plotData(logName, logData, logPlot, min, max, avg, mode):
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
    print("saved plot in ", logPlot)


def crawler(value, pattern, patternL):
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


# Exception e:
# (
#    print "could not find logs with 'traceroute' or 'iperf' pattern"
#    print "please rename logs to reflect actual content, i.e.\n" \
#                "'24hr_iperf_1Gb' or 'traceroute_10MBs', etc.");


if __name__ == '__main__':
    main()
