import time
import winsound
import SvnParser

def main():
    svnParser = SvnParser.SvnParser()       # create our parsers object
    svnParser.dumpGameUrlToFile()           # create gameURLs.txt, unless specified by different name
    svnParser.dumpDependenciesOfGames()     # create libURLs.txt, unless specified by different name
    svnParser.dumpDependenciesUrlToFile()   # create gameDependencies.txt, unless specified by different name, it also create gameDependencies.json for internal use
    


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Execution time > --- %s sec ---" % int(time.time() - start_time))
    print("Execution time > --- %s min ---" % int((time.time() - start_time) / 60))
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)