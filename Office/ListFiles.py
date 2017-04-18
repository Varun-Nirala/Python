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
    content = content.replace(firstAppearedAt, dataToAppend)
    return content


# ModifyNamespaces
# @Param1	:	fileName which is read into content
# @Param2	:	content to modify
# @Param3	:	List for files in which we are unable to include our required files
# @Return	:	Modified content
def ModifyNamespaces(currentfile, content, remainingFileList):

    namespaceDic = {}  # our namespace dictionary with key = NamespaceAlias and value is actual Namespace
    for line in content.split("\n"):
        temp = re.sub(r"\s", "", line)  # using regex to strip whitespaces
        start = temp.find("namespace")
        if start != -1:
            start = start + len("namespace")
            end = temp.find("=", start)
            key = temp[start:end]

            start = end
            end = len(temp)
            value = temp[start:end]

            #TODO: rework on it
            if namespaceDic.get(key, "NotFound") == "NotFound":
                print("key:value pair already exists :: ", key, ":", value)
            else:
                print("Adding key:value pair to dic :: ", key, ":", value)
                namespaceDic[key] = value
    return content


# Includes common files to other files and modify namespaces
# @Param1	:	AllFiles
# @Param2	:	List of files to be included in other file
# @Param3	: 	List of extensions, in which Param2 files are to be included
# @Param4	:	List for files in which we are unable to include our required files
# @Return	:	True if yes, else False		
def IncludeCommonFilesAndModifyNameSpace(directoryPath, fileNameList, extensioList, remainingFileList):
    fileNameToAppend = ""
    for eachInclude in fileNameList:
        fileNameToAppend = fileNameToAppend + eachInclude + "\n"

    AllFiles = ListAllFilesInADirectory('.', extensioList)

    for currentfile in AllFiles:
        file = open(currentfile, "r")
        content = file.read()  # read out whole file in memory
        file.close()

        content = AppendIncludeFiles(currentfile, content, "include", fileNameToAppend, remainingFileList)

        content = ModifyNamespaces(currentfile, content, remainingFileList)

        file = open(currentfile, "w")
        file.write(content)
        file.close()


# IncludeCommonFilesAndModifyNameSpace('.', ["#include <Mercury.h>", "#include <hahahah.h>"], [".h", ".hpp"], [])
localStr = """
using namespace Mercury;
namespace GDK = Aristocrat::GDK;
	namespace GDKServer = GDK::Server;
"""

ModifyNamespaces("Abc.h", localStr, [])
input("Press any key to exit......")
