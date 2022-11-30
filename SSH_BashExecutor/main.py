import paramiko
import pysftp
import ntpath

defaultSrcScriptPath = '/dev/scripts/bash1.sh'

defaultDstHost = '192.168.168.2'
defaultDstPort = '22'
defaultDstCopyPath= '/dev/scripts'

defaultUser = 'codename'
defaultPassword = 'nothing'

class ScriptExecutor:
    def __init__(self):
        self.__scriptPath = None
        self.__dstHost = None
        self.__dstPort = None
        self.__dstCopyPath = None
        self.__dstUser = None
        self.__dstPass = None
        self.__scriptName = None
        self.__cmdOutput = None

    ''' Public Interface '''
    def setSrcScriptPath(self, srcScriptPath):
        self.__scriptPath = srcScriptPath
        # extract filename from the path
        (head, tail) = ntpath.split(srcScriptPath)
        self.__scriptName = tail or ntpath.basename(head)

    def setDstHostAndPort(self, dstHost, dstPort):
        self.__dstHost = dstHost
        self.__dstPort = dstPort

    def setDstUserAndPass(self, dstUser, dstPass):
        self.__dstUser = dstUser
        self.__dstPass = dstPass

    def setDstCopyPath(self, dstCopyPath):
        self.__dstCopyPath = dstCopyPath

    def print(self):
        print('Script Path : %s\n' % self.__scriptPath)
        print('Script Name : %s\n' % self.__scriptName)
        print('Destination\n')
        print('    Host : %s\n' % self.__dstHost)
        print('    Port : %s\n' % self.__dstPort)
        print('    User : %s\n' % self.__dstUser)
        print('    Pass : %s\n' % self.__dstPass)
        print('    Path : %s\n' % self.__dstCopyPath)

    def copyAndExecute(self):
        self.__copyToDst()
        self.__executeScript()
        print('Script Output :\n', self.__scriptName, self.__cmdOutput)

    ''' Private Interface '''
    def __copyToDst(self):
        print('Copying source script [%s] to machine [%s] @ location [%s]' % (self.__scriptPath, self.__dstHost, self.__dstCopyPath))
        with pysftp.Connection(host=self.__dstHost, username=self.__dstUser, password=self.__dstPass) as sftp:
            with sftp.cd(self.__dstCopyPath):
                sftp.put(self.__scriptPath)

    def __executeScript(self, scriptOutPut):
        print('Executing script [%s] on machine [%s] ' % (self.__dstCopyPath, self.__dstHost))

        sshClient = paramiko.SSHClient()

        sshClient.load_system_host_keys()

        sshClient.connect(self.__dstHost, username=self.__dstUser, password=self.__dstPass, port=self.__dstPort)

        (stdin, stdout, stderr) = sshClient.exec_command('cd ' + self.__dstCopyPath)
        (stdin, stdout, stderr) = sshClient.exec_command('./' + self.__scriptName)

        self.__cmdOutput = stdout.read()

if __name__ == "__main__":
    scriptExecutor = ScriptExecutor.ScriptExecutor()

    scriptExecutor.setSrcScriptPath(defaultSrcScriptPath)
    scriptExecutor.setDstHostAndPort(defaultDstHost, defaultDstPort)
    scriptExecutor.setDstUserAndPass(defaultUser, defaultPassword)
    scriptExecutor.setDstCopyPath(defaultDstCopyPath)

    scriptExecutor.copyAndExecute()