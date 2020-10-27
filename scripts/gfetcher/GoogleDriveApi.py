#!/usr/bin/python
#.....................................................................
# Copyright (c) 2019-2020, Regents of the University of Arizona.
# Author: Chavoosh Ghasemi<chghasemi@cs.arizona.edu>
#
# You should have received a copy of the GNU General Public License along with
# this script e.g., in COPYING.md file. If not, see <http://www.gnu.org/licenses/>.
#.....................................................................

import os.path
import pickle
import io

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest 
from googleapiclient.http import MediaIoBaseDownload

from constants import *
from core import *

class GoogleDriveApi:
    __service = None
    __cred = None
    __mainDirectory = ""

    def connect(self):
        self.__checkOrSetCredential()
        self.__service = build('drive', 'v3', credentials=self.__cred)

    def __checkOrSetCredential(self):
        if os.path.exists(TOKEN_PICKLE_PATH):
            with open(TOKEN_PICKLE_PATH, 'rb') as token:
                self.__cred = pickle.load(token)
        if self.__isCredentialInvalidOrNotPresent():
            if self.__isCredentialExpired():
                self.__cred.refresh(Request())
            else:
                self.__askUserToSetupCredential()
            self.__saveCredentialOnDisk()

    def __refreshConnection(self):
        self.connect()

    def __isCredentialInvalidOrNotPresent(self):
        return not self.__cred or not self.__cred.valid

    def __isCredentialExpired(self):
        return self.__cred and self.__cred.expired and self.__cred.refresh_token

    def __askUserToSetupCredential(self):
        assertWithMessage(os.path.exists(CREDENTIAL_PATH), getGoogleCredentialErrorMessage())
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIAL_PATH, SCOPES)
        self.__cred = flow.run_local_server(port=0)

    def __saveCredentialOnDisk(self):
        with open(TOKEN_PICKLE_PATH, 'wb') as token:
            pickle.dump(self.__cred, token)

    def __getDirIdByDirName(self, directory):
        query = "mimeType='application/vnd.google-apps.folder' and name=" + "'" + directory + "'" + " and trashed=false"
        space = "drive"
        request = self.__service.files().list(q=query, spaces=space)
        response = request.execute()
        folders = response.get('files', [])
        if isEmpty(folders):
            warningMessage(directory + ": Queried Google directory does not exist, please provide a valid directory. Exiting...")
            sys.exit(7)
        return folders[0].get("id")

    @trycatch
    def getListOfVideosIn(self, directory):
        listOfVideos = []
        pageToken = None
        parentId = self.__getDirIdByDirName(directory)
        query = "mimeType contains 'video' and parents=" + "'" + parentId + "'" + " and trashed=false"
        space = "drive"
        queryFields = "nextPageToken, files(id, name, modifiedTime, mimeType)"
        while True:
            request = self.__service.files().list(q=query, spaces=space,
                                                  fields=queryFields,
                                                  pageToken=pageToken)
            response = request.execute()
            listOfVideos.extend(response.get('files', []))
            pageToken = response.get('nextPageToken', None)
            if isEmpty(pageToken):
                break

        return listOfVideos

    def __getFileInfoByFileId(self, fileId):
        request = self.__service.files().get(fileId=fileId, fields="*")
        response = request.execute()
        return response 

    def downloadFileByFileId(self, fileId):
        fileInfo = self.__getFileInfoByFileId(fileId)
        fileName = fileInfo.get("name")
        saveAs = VIDEO_DIR + "/" + fileName

        request = self.__service.files().get_media(fileId=fileId)
        fh = io.FileIO(saveAs, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        downloadIsFinished = False
        while not downloadIsFinished:
            downloadStatus, downloadIsFinished = downloader.next_chunk()
            infoMessage("Download %d%%." % int(downloadStatus.progress() * 100))

    def isFileModifiedFromLastCheck(self, fileInfo):
        lastModifiedTime = self.__getFileInfoByFileId(fileInfo.get("id")).get("modifiedTime")
        if fileInfo.get("modifiedTime") != lastModifiedTime:
            return True
        return False
