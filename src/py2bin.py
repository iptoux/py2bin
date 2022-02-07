#!/bin/env python3.10

from asyncio.subprocess import PIPE
import sys, os, subprocess, shutil, logging
from pickle import FALSE, TRUE
from time import sleep
import time
from unittest.mock import patch

#from sqlalchemy import true

COL = {"NC": "\033[0m", 
          "RD": "\033[0;31m", 
          "DG": "\033[1;30m",
          "BO": "\033[0;33m", 
          "YL": "\033[1;33m", 
          "BL": "\033[0;34m", 
          "PU": "\033[0;35m", 
          "CY": "\033[0;36m", 
          "LG": "\033[0;37m", 
          "LB": "\033[1;34m",
          "WH": "\033[1;37m"
          }

def main():
    t = time.localtime()
    global current_time
    
    current_time = time.strftime("%d-%m-%y_%H:%M:%S", t)
    ## TODO
    # check for sudo
    # create log dir (check if exists; No = login)
    lfile = "compile_"+current_time+".log"
    ldir = 'log/'
    os.system('mkdir %s' % ldir)
    lpath = ldir+lfile
    #if(checkSudo() == TRUE):
    #    os.system('mkdir log')
    #else:
    #    sys.exit(COL['RD'] + "Error:" + COL['NC'] + " Compile"+COL['CY']+" main()"+COL['NC']+" has been failed.\nYou need sudo/root to create an log folder, instead it is possible to craete it manualy.\n")
    logging.basicConfig(filename=lpath, format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    os.system('clear')



    if(preCheck() == FALSE):
        sys.exit(COL['RD'] + "Error:" + COL['NC'] + " Compile"+COL['CY']+" preCheck"+COL['NC']+" has been failed. please see log\n")    
    if(buildScript() == FALSE):
        sys.exit(COL['RD'] + "Error:" + COL['NC'] + " Compile"+COL['CY']+" buildSRC"+COL['NC']+" has been failed. please see log\n")    
    if(doCompile() == FALSE):
        sys.exit(COL['RD'] + "Error:" + COL['NC'] + " Compile"+COL['CY']+" doCompile"+COL['NC']+" has been failed. please see log\n")    
    postOps()
    cleanUp()

# Submod to check if user is sudo, user will be asked if je wanna
# # start the sudo prompt
def checkSudo():
    msg = "[sudo] password for %u:"
    ret = subprocess.call("sudo -v -p '%s'" % msg, shell=True, stderr=subprocess.PIPE)
    if(ret == 1):
        return(FALSE)
    else:
        return(TRUE)


def postOps():
    logging.info("---------- Post operations.......")
    print(COL['CY']+" ##"+COL['NC']+" Post operations........"+COL['CY']+" ##"+COL['NC'])
    print("    + Rename output file: ", end = "", flush = True)
    logging.info("postOps: rename output to program name.")
    #mv dist/output dist/CMBFan
    sleep(0.5)
    print(COL['YL']+"Done."+COL['NC'])
    print("    + Make file executable: ", end = "", flush = True)
    logging.info("postOps: making file executable.")
    #chmod +x dist/CMBFan
    sleep(0.5)
    print(COL['YL']+"Done."+COL['NC'])
    logging.info("postOPs: done.")
    return(TRUE)

def cleanUp():
    logging.info("---------- cleanUp...")
    print(COL['CY']+" ##"+COL['NC']+" Cleaning temporary build files...."+COL['CY']+" ##"+COL['NC'])
    x = input("    + delete files? (Y/n): ")
    x = x.upper()
    if(x=='Y'):
        print("        ++ Deleting... ",end="",flush=True)
        logging.info("cleanUp: delete output directory.")
        t = os.getcwd() + "/output"
        shutil.rmtree(t)
        logging.info("cleanUp: delete spec and src files.")
        os.system("rm output.spec")
        os.system("rm build.src")
        sleep(0.5)
        print(COL['YL']+"Done."+COL['NC'])
    logging.info("cleanUp: done.")
    print("\n"+COL['CY']+"*********************************************")
    print("** "+COL['NC']+"Compiling complete. You can find the binary in dist/ folder.\n\n")
    return(TRUE)
    
def doCompile():
    logging.info("---------- doCompile...")
    print(COL['CY']+" ##"+COL['NC']+" Calling pythoninstall to generate binary "+COL['CY']+" ##"+COL['NC'])
    sleep(1)
    #### Call options (arguments) #### c
    # --specpath DIR    # -F, --onefile
    # --clean           # --distpath DIR
    # -n NAME, --name NAME
    compOps=" --clean --distpath ../dist --workpath ../build -F -n output build.src"
    logging.info("doCompile: compiler arguments -> " + compOps)
    print("    + Generate binary (can take a wile): ", end = "", flush = True)
    logging.info("doCompile: build....")
    buildCMD = "pyinstaller"+compOps+" > log/pyinstaller_"+current_time+".log"
    ret = 0
    ret = subprocess.Popen(buildCMD, shell=True, stderr=subprocess.PIPE, stdout=PIPE)
    retw = ret.wait()
    if(retw == 0):
        print(COL['YL']+"Done."+COL['NC'])
        eoutput = ret.communicate()[1]
        f = open(os.getcwd()+'/log/pyinstaller_'+current_time+'.log','wb+')
        f.write(eoutput)
        f.close
        logging.info("doCompile: done.")
        return(TRUE)
    else:
        print(COL['RD']+"Error"+COL['NC'])
        eoutput = ret.stderr.read()
        f = open(os.getcwd()+'/log/pyinstaller_'+current_time+'.log','wb+')
        f.write(eoutput)
        f.close
        logging.error("doCompile: ERROR -> see pyinstaller.log")
        return(FALSE)


def readPatchFile(pF):
    # Read all Lines into an list
    pFc = []
    f = open(pF, "r")
    fc = f.readlines()
    f.close()
    for i in fc:
        i = i.rstrip("\n")
        pFc.append(i)
    return(pFc)

def checkFile(file):
    logging.debug("buildSRC:fileCheck: src file -> %s" % file)
    xe = file.partition('.')[2]
    if(xe == 'py'):
        return(TRUE)
    else:
        logging.error("buildSRC:check: Error. Not an python script file.")
        return(FALSE)

def buildScript(buildPath='',srcPath = '../src/',patchPath = 'patches/'):
    logging.info("---------- buildSRC...")
    returncode = FALSE
    
    buildSet = {
        'buildPath':    buildPath,
        'srcPath':      srcPath,
        'patchPath':    patchPath,
        'buildFile':    ''
    }
    
    buildSet['buildFile'] = buildSet['buildPath']+'build.src'

    #STEP 1 count files in src directory.
    try:
        logging.info("buildSRC:prepare: count files in src directory.")
        print("    + Looking for src files...:\t\t", end = "", flush = TRUE)
        # Read all python src file names in directory src to an list.
        srcFilesNames = os.listdir(buildSet['srcPath'])
        srcFilesCount = len(srcFilesNames)
        print("%s Files" % srcFilesCount)
        logging.debug("buildSRC:prepare: Found %s Files." % srcFilesCount)
        returncode = TRUE
    except:
        logging.error("buildSRC:prepare:s1 FAILED ^^")
        returncode = FALSE

    #STEP 2 count files in patches directory.
    try:
        logging.info("buildSRC:prepare: count files in patch directory.")
        print("    + Looking for patch files...:\t", end = "", flush = TRUE)
        # Read all python src file names in directory src to an list.
        srcFilesPatches = os.listdir(buildSet["patchPath"])
        srcFilesPatchesCount = len(srcFilesPatches)
        print("%s Files" % srcFilesPatchesCount)
        logging.debug("buildSRC:prepare: Found %s Files." % srcFilesPatchesCount)
        returncode = TRUE
    except:
        logging.error("buildSRC:prepare:s2 FAILED ^^")
        returncode = FALSE
    
    #STEP 3 Generating (prepare) Build File, pop none .py files from srcFileNames obj
    # (Over)Write buildFile 
    try:
        logging.info("buildSRC:prepare: generating build file: %s." % buildSet['buildFile'])
        print("    + Prepare buildFile...:\t\t", end = "", flush = TRUE)
        
        #ceate write obj
        #loop src folder -> call function to read file (apply patch if available)
        writeObj = open(buildSet['buildFile'],"w")
        writeObj.flush()
        writeObj.close()
        print('done.')

        print("    + remove none .py files...:\t\t", end = "", flush = TRUE)
        # For each file in src check if is an .py, if not remove from list.
        rm = int(0)
        for x in srcFilesNames:
            if(checkFile(x) == FALSE):
                srcFilesNames.pop(srcFilesNames.index(x))
                rm = rm + 1
        print('%s Files.' % rm)
        returncode = TRUE
    except:
        logging.debug("###################EXEPTCION######################")
        logging.debug("buildSRC:prepare: STEP 3 FAILED... ")
        logging.exception("buildSRC:prepare: execptionMSG below.\n___________________________________")

        returncode = FALSE
        sys.exit()

    #STEP 4
    try:
        buildFile = open(buildSet["buildFile"],"a")
        
        for x in srcFilesNames:
            logging.info("buildSRC:building: read src file -> %s" % x)

            scFile = buildSet["srcPath"]+x
            if(os.path.isfile(scFile)):
                srcFile = open(scFile,"r")
                print("    + Loading file...:\t\t\t"+COL['LB']+"%s" % x,end = "",flush = True)
                print(""+COL['NC'])
                srcFileData = srcFile.readlines()
                srcFile.close()       
            else:
                logging.error('buildSRC:building: File %s not found' % scFile)
                return(FALSE)
        
            #check for patch
            xp = x.partition('.')[0]+'.patch'
            xpPath = buildSet["patchPath"] + xp

            if(checkPatch(xpPath) != FALSE):
                print("        ++ Found patch, Lines...:\t", end = "", flush = True)
                toWrite = doPatch(srcFileData,xpPath)

                print("        ++ Write to build file...:\t", end = "", flush = True)
                logging.info("buildSRC:building: write to build file... ")
                for i in toWrite:
                    for l in i:
                        buildFile.write(l)
                logging.info("buildSRC:building: done ")
                sleep(0.5)
                print("done.")
            else:
                print("        ++ Write to build file...:\t", end = "", flush = True)
                logging.info("buildSRC:building: write to build file... ")
                for i in srcFileData:
                   buildFile.write(i)
                logging.info("buildSRC:building: done ")
                sleep(0.5)
                print("done.")
        
        buildFile.close()
    except:
        logging.debug("###################EXEPTCION######################")
        logging.debug("buildSRC:processing: STEP 4 FAILED... ")
        logging.exception("buildSRC:processing: execptionMSG below.\n___________________________________")
        returncode = FALSE

    if(returncode == FALSE):
        sys.exit('\n\nThere occured some Error, please see log for more infromations.\nYou can alternativly activate DEBUG logging to get more log output.')


def checkPatch(file):
    logging.info("buildSRC:processing: checking for patch...")
    if(os.path.isfile(file) == 1):
        logging.info("buildSRC:processing: found -> %s" % file)
        return(TRUE)
    else:
        logging.info("buildSRC:processing: no patchfile (%s) found." % file)
        return(FALSE)

def doPatch(srcFile,patchFilePath):
    comp = FALSE
    logging.info("buildSRC:patching: reading patchfile...")
    patchfile = open(patchFilePath,"r")
    patchline = patchfile.readlines()
    
    # Holderlist for Patchlines
    patchLinesRM = []       # List for removing patch lines
    patchLinesRE = []       # List for replace patch lines
    patchLinesADD = []      # List for adding patch lines
    logging.debug("buildSRC:patching: creating lists with elements")

    # Fill patch lists
    for act in patchline:
        if(act.find('RM%') == 0):
            patchLinesRM.append(act)
        elif(act.find('RE%') == 0):
            patchLinesRE.append(act)
        elif(act.find('ADD%') == 0):
            patchLinesADD.append(act)

    patchfile.close()
    logging.info("buildSRC:patching: %s RM | %s RE | %s ADD" % (len(patchLinesRM),len(patchLinesRE),len(patchLinesADD)))
    print("%s RM | %s RE | %s ADD" % (len(patchLinesRM),len(patchLinesRE),len(patchLinesADD)))

    # Sorting lists, to do patches in right order.
    patchLinesRM.sort(reverse=True)
    patchLinesRE.sort()
    patchLinesADD.sort()

    # Object for contect of patchedsrc
    patched = srcFile
    LineCount = {
        'RM': int(0)
    }

    if(len(patchLinesRE) > 0):
        print("        ++ Patching RE..........:\t", end="", flush=TRUE)
        logging.info('buildSRC:patching:........ REPLACE OPS')
        for steps in patchLinesRE:
            pline = steps.split('%')
            if(len(pline) == 4):    
                liner = int(pline[1])
                pos = int(pline[2])
                code = pline[3]
                code = code.rstrip('\n')
                code = code + '\n'

                #TODO
                # adding option to set an position where to apply patch.                

                logging.debug('buildSRC:patching:RE: Line: %s' % liner)
                patched[liner] = code
            else:
                v = int(4) - int(len(pline))
                logging.warning('buildSRC:patching:skip: %s - values (%s) (pos/code) missing.' % (pline,v))
        sleep(0.5)    
        print("done.")

    if(len(patchLinesADD) > 0):
        print("        ++ Patching ADD..........:\t", end="", flush=TRUE)
        logging.info('buildSRC:patching:......... ADD OPS')
        for steps in patchLinesADD:
            pline.clear()
            pline = steps.split('%')
            if(len(pline) == 3):   
                line = int(pline[1])
                code = pline[2]
                logging.debug('buildSRC:patching:ADD: Line: %s' % line)
                patched.insert(int(line),code)
            else:
                v = int(3) - int(len(pline))
                logging.warning('buildSRC:patching:skip: %s - values (%s) (pos/code) missing.' % (pline,v))
        sleep(0.5)
        print("done.")
    

    if(len(patchLinesRM) > 0):
        print("        ++ Patching RM..........:\t", end="", flush=TRUE)
        logging.info('buildSRC:patching:........ REMOVE OPS')
        for steps in patchLinesRM:
            pline = steps.split('%')
            if(len(pline) == 2):
                # RM Single line
                line1 = pline[1]
                line1 = line1.rstrip("\n")
                if "-" in line1:
                    logging.warning('buildSRC:patching:skip: %s - should be one number only.' % pline)
                else:
                    logging.debug('buildSRC:patching:RM: Line: %s' % line1)
                    ltr = int(line1) - 1
                    patched.pop(ltr)
                    LineCount["RM"] += 1
            elif(len(pline) == 3):
                # RM Multiple lines (from - to)
                line1 = pline[1].rstrip("\n")
                line2 = pline[2].rstrip("\n")
                if(line1 >= line2):
                    logging.debug('buildSRC:patching:skip: %s - value1 should be smaller than value2.' % pline)
                else:
                    logging.debug('buildSRC:patching:RM: Line: %s - %s' % (line1,line2))
                    c = int(line2) - int(line1)
                    cl = 0
    
                    while cl <= c:
                        LineCount["RM"] += 1
                        print(cl+1)
                        cl += 1
                        #TODO
                        # REMOVE MULTILINE
            else:
                #Wrong line values, skipping
                logging.warning('buildSRC:patching:skip: %s - values wrong for RM operations.' % pline)
        sleep(0.5)
        print("done.")

    patched.append('\n\n')
    logging.info('buildSRC:patching: all operations for %s done, next file...' % patchFilePath)
    return(patched)

def dirs():
    print(COL['CY']+" ##"+COL['NC']+" Generating build space "+COL['CY']+" ##"+COL['NC'])
    logging.info("preCheck:dirs: checking for output & dist directorys")
    if(os.path.isdir('output')):
        logging.info("preCheck:dirs: output dir exists, delete?")
        x = input("    + Delete old build directory? (Y/n): ")
        x = x.upper()
        #if(x != "Y" or x != "N"):
        #    logging.error("preCheck:dirs: You have to enter Y or N.")
        #    return(FALSE)
        #    #sys.exit("Error:You have to enter Y or N.")
        if(x == "Y"):
            print("        ++ Deleting... ",end="",flush=True)
            logging.info("preCheck:dirs: delete old output directory")
            t = os.getcwd() + "/output"
            shutil.rmtree(t)
            sleep(0.5)
            print(COL['YL']+"done"+COL['NC'])
    if(os.path.isdir('../dist')):
        logging.info("preCheck:dirs: dist directory exists, delete?")
        x = input("    + Delete old dist directory? (Y/n): ")
        x = x.upper()
        #if(x != "Y" or x != "N"):
        #    logging.error("preCheck:dirs: You have to enter Y or N.")
        #    return(FALSE)
        #    #sys.exit("Error:You have to enter Y or N.")
        if(x == "Y"):
            print("        ++ Deleting... ",end="",flush=True)
            logging.info("preCheck:dirs: delete old dist directory.")
            shutil.rmtree("../dist")
            sleep(0.5)
            print(COL['YL']+"done"+COL['NC'])
    return(TRUE)

def preCheck():
    logging.info("---------- preCheck...")
    if(dirs() == FALSE):
        return FALSE
    elif(checkPyInstall() == FALSE):
        return FALSE
    
    #logging.info("---------- preCheck: done.")
    return TRUE
    
def checkPyInstall():
    logging.info("preCheck:modules: checking for PyInstaller")
    print(COL['CY']+" ##"+COL['NC']+" checking for requirements "+COL['CY']+" ##"+COL['NC'])
    print("    + PyInstaller: ", end="", flush=True)
    try:
        import PyInstaller
        sleep(1)
        print(COL['YL']+"installed."+COL['NC'])
        logging.info("preCheck:modules: module is installed")
        return(TRUE)
    except ImportError:
        sleep(1)
        print(COL['RD']+"not installed."+COL['NC'])
        logging.critical("preCheck:modules: module is not installed")
        return(FALSE)

if (__name__ == "__main__"):
    main()