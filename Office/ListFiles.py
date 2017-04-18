import os
import sys
import re

# Read up all files with a specific extension and get them into a list
# @Param1	:	Path
# @Param2	:	List of extensions
# @Return	:	List of all files in specific path with specific extensions
def ListAllFilesInADirectory(directoryPath, withExtension):
    fileList = []
    for currentfile in os.listdir(directoryPath):
        for i in range(len(withExtension)):
            if currentfile.endswith(withExtension[i]):
                fileList.append(currentfile)
    return fileList


# Checks if a particular file exists in the provided directoryPath
# @Param1	:	Path
# @Param2	:	FileName
# @Return	:	True if yes, else False
def CheckIfFileExists(directoryPath, fileName):
    fullPath = directoryPath + '//' + fileName
    if os.path.isfile(fullPath):
        return True
    else:
        return False


# Adds a file with the provided name in the provided path, if same file doesnt exists,
# otherwise keeps on suffixing "_" upto the name upto 10 times 
# @Param1	:	Path
# @Param2	:	FileName
# @Return	:	True if yes, else False		
def AddAFileToTheFolderWithDataInIt(directoryPath, fileName, dataToWriteInFile):
    for i in range(10):
        if CheckIfFileExists(directoryPath, fileName):
            fileName = "_" + fileName
        else:
            break
    if i < 10:
        newFile = open(fileName, "w+")
        newFile.write(dataToWriteInFile)  # All namespace related data
        newFile.close()
    else:
        # TODO:: Maybe we shouldn't abort here
        sys.exit("Cannot create file NamespaceAlias.h as its already there.")
    return fileName


# find the first line with a word/substring in it CaseSensitive match
# @Param1	:	content/multiline
# @Param2	:	word/substring
# @Return	:	that whole line
def FindFirstLineWithWord(content, word):
    for line in content.split("\n"):
        if line.find(word):
            return line


# Includes common files to other files
# @Param1	:	fileName which is read into content
# @Param2	:	content to modify
# @Param3	:	substring which is searched in content and @Param3 is appended after that line 
# @Param4	: 	data to be appneded after @param3 found
# @Param5	:	List for files in which we are unable to include our required files
# @Return	:	Modifed content
def AppendIncludeFiles(fileName, content, appendAt, dataToAppend, remainingFileList):
    firstAppearedAt = FindFirstLineWithWord(content, appendAt)
    if len(firstAppearedAt) == 0:
        remainingFileList.append(fileName)
        return content
    dataToAppend = dataToAppend + firstAppearedAt
    content = content.replace(firstAppearedAt, dataToAppend, 1)
    return content


# ModifyNamespaces
# @Param1	:	fileName which is read into content
# @Param2	:	content to modify
# @Param3	:	List for files in which we are unable to include our required files
# @Return	:	Modified content
def ModifyNamespaces(currentfile, content, remainingFileList):
    namespaceDic = {}       # our namespace dictionary with key = NamespaceAlias and value is actual Namespace
    newLine = ""
    for line in content.split("\n"):
        temp = re.sub(r"\s", "", line)  # using regex to strip whitespaces
        start = temp.find("namespace")
        if start != -1:
            start = start + len("namespace")
            end = temp.find("=", start)
            if end != -1:           # it mean its a new alias for namespace
                value = re.sub(r"\s", "", temp[start:end])

                start = end
                end = len(temp)
                key =  re.sub(r"\s", "", temp[start:end])

                #TODO: rework on it
                temp = namespaceDic.get(key, "NotFound")
                if temp == "NotFound":
                    print("key:value pair already exists :: ", key, ":", value)
                else:
                    print("Adding key:value pair to dic :: ", key, ":", value)
                    namespaceDic[key] = value
            else:                   # it mean its a "using namespace" statemanet
                end = len(temp) - 1         # -1 for ';'
                key = temp[start:end]
                temp = namespaceDic.get(key, "NotFound")
                newLine = line.replace(key, temp)
        content = content.replace(line, newLine, 1)
    return content


# Includes common files to other files and modify namespaces
# @Param1	:	FilesList which is included in content, from which have to read and fill our dictionary  with
#               Alias and Actual namespace expansion
# @Param2	:	Convention from which Alias start with (ours start's with "G_")
# @Param3	: 	Base namespace which contain all namespaces, (ours is "Aristocrat::")
# @Param4	:	Dictionary filled with key as Expansion of namespace and value as its alias
#               Example :   ((key) : (value))
#                           ((Aristocrat::GDK::Slot) : (G_Slot))
# @Return	:	True if yes, else False
def FillNamespaceDic(fileNameList, AliasStartWith, ActualStartsWith, namespaceDic):
    regex = AliasStartWith + r"[a-zA-Z]+[ \t=]"

    for eachInclude in fileNameList:
        file = open(eachInclude, "r")
        content = file.read()
        file.close()

        for line in content.split("\n"):
            key = ""
            firstMatch = re.search(regex, line)
            if firstMatch:
                value = firstMatch.group(0)
                if len(value) > 0:
                    start = line.find(ActualStartsWith)
                    end = line.find(";")
                    key = line[start:end]

                    # Aristocrat Specific content
                    if ActualStartsWith == "Aristocrat::" or ActualStartsWith == "Aristocrat":
                        key = key.replace("GDK_NAMESPACE", "GDK")
                        key = key.replace("GDX_NAMESPACE", "GDX")

                    found = namespaceDic.get(key, "Not Found")
                    if found == "Not Found":
                        namespaceDic[key] = value
                        #print("Key Not Found : Key = ", key, ", Value = ", value)
                    #else:
                        #print("Key Found : Key = ", key, ", Value = ", value)
            #else:
                #print("No match found")


# Includes common files to other files and modify namespaces
# @Param1	:	AllFiles
# @Param2	:	List of files to be included in other file
# @Param3	: 	List of extensions, in which Param2 files are to be included
# @Param4	:	List for files in which we are unable to include our required files
# @Return	:	True if yes, else False		
def IncludeCommonFilesAndModifyNameSpace(directoryPath, fileNameList, extensioList, remainingFileList):
    fileNameToAppend = ""
    for eachInclude in fileNameList:
        eachInclude = r'#include "' + eachInclude + r'"'
        fileNameToAppend = fileNameToAppend + eachInclude + "\n"

    namespaceDic = {}
    FillNamespaceDic(["NamespaceAlias.h"], "G_", "Aristocrat::", namespaceDic)  #Thats how it should be called

    for key in namespaceDic:
        print(key, ":", namespaceDic[key])

    AllFiles = ListAllFilesInADirectory(directoryPath, extensioList)

    for currentfile in AllFiles:
        currentfile = directoryPath + r'/' + currentfile
        file = open(currentfile, "r")
        content = file.read()  # read out whole file in memory
        file.close()

        print(currentfile)
        content = AppendIncludeFiles(currentfile, content, "include", fileNameToAppend, remainingFileList)

        content = ModifyNamespaces(currentfile, content, remainingFileList)

        file = open(currentfile, "w")
        file.write(content)
        file.close()

def CallFun():
    remainingFileList = []
    IncludeCommonFilesAndModifyNameSpace('./src', ["NamespaceAlias.h"], [".h", ".hpp"], remainingFileList)
    input("Press any key to exit......")

print("Calling First Function : FillNamespaceDic")
CallFun()

# IncludeCommonFilesAndModifyNameSpace('.', ["#include <Mercury.h>", "#include <hahahah.h>"], [".h", ".hpp"], [])
# TODO: Add NamespaceAlias.h in the src folder at the end of the process.
# TODO: currently deleteing all data
