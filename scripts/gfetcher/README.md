# gFetcher

This script bundle provides an automated way to publish/remove videos in/from [NDN video streaming service (iViSA)](https://ivisa.named-data.net).

This tool runs on the server side. It frequently checks a specific Google drive folder of a Gmail account and reflects any changes in that folder in the streaming service.
More specificly, if a new video will be added to the Google drive folder, this tool automatically will encode and publish it in the streaming service.
Also, if the name of any previously published video changes in the Google drive folder, this tool will accordingly update the name of the video in the service.
The last operation that this tool supports is deleting a video. Upon deleting a previously published video, this tool will accordingly remove it from the streaming service.

## Prerequisites
* Install NDN MongoDB Fileserver [prereleases](https://github.com/chavoosh/ndn-mongo-fileserver#prerequisites)
* Install [pip](https://pip.pypa.io/en/stable/installing/#) package management tool
* Install the Google Client Library. Run the following command:

    `$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
* Turn on Drive API of the Gmail account that you want to sync with the streaming service.
Follow __Step 1__ in this [link](https://developers.google.com/drive/api/v3/quickstart/python#step_1_turn_on_the).

## How to use
1. Create a folder in the Google drive; let's say its name is `video-collection`.
2. Upload a video in that folder; let's say sample-video.mp4.
3. Run the tool by running the following command:

    `$ python gFetcher.py video-collection`
4. If this is the first time running this tool, you will be asked to grant the tool sufficient access to your Google account. The tool walks you through the steps.
5. The tool will add the video to MongoDB and it will be ready to be served by NDN MongoDB Fileserver.
6. After inserting, if you want to rename the name of the published video, simply rename the video in the Google drive folder; the tool will update the name of the published video accordingly.
7. If you need to delete the published video from MongoDB, put keyword __`_delete_`___ at the beginning of the video file name.
For example, if __sample-video.mp4__ is published and you want to delete it, just rename it from `sample-video.mp4` to `_delete_sample-video.mp4`.

## Note
This tools keeps all its log files and necessary resources under __`/var/log/gFetcher`__ directory.
