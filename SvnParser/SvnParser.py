import pysvn
import re
import json

defaultGameUrl = 'https://svn.ali.global/Games'
defaultDependenciesUrl = 'https://svn.ali.global/GamesDependencies'

class SvnParser:
    def __init__(self, gameUrl = defaultGameUrl, dependenciesUrl = defaultDependenciesUrl):
        self.__gameUrl = gameUrl
        self.__dependenciesUrl = dependenciesUrl
        self.__svnClient = pysvn.Client()
        self.__svnClient.exception_style = 1

        self.__gameUrlList = []
        self.__dependenciesUrlList = []
        self.__gameDependenciesMap = {}


    ''' Public Interface '''
    ''' 
        To Dump all the lib url to a txt file
        @TODO : it still doesnot parse the Recipies structure
    '''
    def dumpDependenciesUrlToFile(self, fileName='libURLs.txt'):
        self.__dependenciesUrlList = self.__dumpSvnUrlToFile(self.__dependenciesUrl, fileName)


    ''' 
        To Dump all the games url to a txt file
    '''
    def dumpGameUrlToFile(self, fileName='gameURLs.txt'):
        self.__gameUrlList = self.__getGameTrunkUrlList(self.__gameUrl)
        self.__dumpListToFile(self.__gameUrlList, fileName)

    
    ''' 
        To Dump all the games and library used by a game into two different files txt and json
    '''
    def  dumpDependenciesOfGames(self, fileName = 'gameDependencies.txt'):
        if len(self.__gameDependenciesMap) == 0:
            if len(self.__gameUrlList) == 0:
                self.__gameUrlList = self.__getGameTrunkUrlList(self.__gameUrl)

            self.__gameDependenciesMap = self.__filterMap(self.__getMapOfGameDependenciesFile(self.__gameUrlList))
        
        with open(fileName, 'w') as f:
            for key, value in self.__gameDependenciesMap.items():
                f.write("\n%s => " % key)
                for line in value:
                    f.write("    %s" % line)

        self.__mapToJson(self.__gameDependenciesMap, 'gameDependencies.json')


    def getMap(self, fileName='gameDependencies.json'):
        return self.__JsonToMap(fileName)


    def __mapToJson(self, nMap, fileName):
        j = json.dumps(nMap, sort_keys=True)
        with open(fileName, 'w') as outfile:
            outfile.write(j)


    def __JsonToMap(self, fileName):
        nMap = json.load(open(fileName))
        return nMap


    def __filterMap(self, myMap):
        nMap = {}
        for key, value in myMap.items():
            allLines = value.splitlines()
            gList = []
            for line in allLines:
                startWithStr = r'set(GAME_DEPENDENCIES ${GAME_DEPENDENCIES} "../GameDependencies/'
                if line.startswith('#') == False:
                    if line.startswith(startWithStr) == True:
                        line.strip()
                        startIndex = line.rfind('/')
                        endIndex = line.rfind('")')
                        if startIndex != -1:
                            data = line[startIndex:endIndex]
                            gList.append(data)
            nMap[key] = gList.copy()
            gList.clear()
        return nMap


    ''' Private Methods '''
    def __filterUrl(self, url):
        return url[url.index('http'):url.index("'>")]


    def __testURL(self, url):
        try:
            self.__svnClient.info2(url)
            return True
        except:
            return False

    
    def __getSvnUrlList(self, svnPath):
        urlList = []
        svnlist = self.__svnClient.list(svnPath)
        svnlist.sort()
        for item in svnlist:
            url = str(item)
            urlList.append(self.__filterUrl(url))
        return urlList


    def __getSvnUrlListWithDepth(self, svnPath):
        urlList = []
        svnlist = self.__svnClient.list(svnPath, depth=pysvn.depth.immediates)
        svnlist.sort()
        for item in svnlist:
            url = str(item)
            urlList.append(self.__filterUrl(url))
        return urlList


    def __dumpListToFile(self, urlList, fileName):
        with open(fileName, 'w') as f:
            for item in urlList:
                url = str(item)
                f.write("%s\n" % url)


    def __dumpSvnUrlToFile(self, svnPath, fileName):
        urlList = self.__getSvnUrlList(svnPath)
        self.__dumpListToFile(urlList, fileName)
        return urlList


    def __printList(self, listData, startQuote='START', endQuote='END'):
        print(startQuote)
        for item in listData:
            print(str(item))
        print(endQuote)


    def __getGameTrunkUrlList(self, svnPath):
        svnUrlList = self.__getSvnUrlList(svnPath)
        urlList = []
        for item in svnUrlList:
            svnlist = self.__getSvnUrlListWithDepth(item)
            for url in svnlist:
                if re.search('trunk', url, re.IGNORECASE) != None:
                    if url.endswith('trunk'):
                        urlList.append(url)

                elif re.search('DevLines', url, re.IGNORECASE) != None:
                    nList = self.__getSvnUrlListWithDepth(url)
                    for inVal in nList:
                        inList = self.__getSvnUrlListWithDepth(inVal)
                        for val in inList:
                            if re.search('trunk', val, re.IGNORECASE):
                                if val.endswith('trunk'):
                                    urlList.append(val)
        return urlList


    def __getMapOfGameDependenciesFile(self, gameTrunkUrlList):
        dicMap = {}
                                    
        for item in gameTrunkUrlList:
            key = item
            item = item + '/source/dependencies.cmake'
            textData = 'NONE'

            if self.__testURL(item) == True:
                data = self.__svnClient.cat(item)
                textData = data.decode()

            dicMap[key] = textData
        return dicMap
