# NDN Sevres Files From MongoDB

NDN-MONGO-FILESERVER tool-bundle is part of [iViSA project](https://ivisa.named-data.net) which includes the following tools:
1. [ndn-mongo-fileserver](src/mongo-fileserver)
2. [chunker](src/util)
3. [stats-collector](src/util)

## INSTALL
Take the following steps to install this tool-bundle.

### Prerequisites
Install the mentioned version of the following packages:
- [ndn-cxx](https://github.com/named-data/ndn-cxx) (release `0.6.6`)
- [NFD](https://github.com/named-data/NFD) (release `0.6.6`)
- [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-on-ubuntu)

### Build Steps
To configure, compile, and install this tool-bundle, type the following commands
in the source directory:

      ./waf configure
      ./waf
      sudo ./waf install

### Quick test
To make sure the tool-bundle is installed properly here is a quick test:

1. Run MongoDB service:

       sudo systemctl start mongod.service

2. Chunk a content and populate the DB (the following command breaks down the input file into
1kB chunks with version 1 where each chunk's name looks like: `/ndn/test/README.md/%FD%01/<segment-number>`)

       chunker /ndn/test -i ~/ndn-mongo-fileserver/README.md -s 1000 -e 1

3. Run NFD and then run fileserver to serve the available contents in the DB (the following command lets the fileserver to answer
all Interests whose name start with `/ndn/test`):

        ndn-mongo-fileserver /ndn/test
4. Open [segment-fetcher.html](util/segment-fetcher.html) in browser and ask for `/ndn/test/README.md`.

If no error occurred during any step you can safely quite the fileserver and be sure that the tool-bundle works properly. 

# Frontend
To learn how to watch the published videos in modern browsers visit [ndn-video-frontend](https://github.com/chavoosh/ndn-video-frontend).

# Serve videos via NDN testbed
After setting up the NDN fileserver you might want to serve your videos via NDN testbed. To do this, take the following steps:
1. [Get a valid certificate](https://ndncert.named-data.net/help) from NDN testbed and set it up on your server. Assume your certificate name is `/ndn/my/cert`.

2. Connect the NFD on your server to [one of the testbed hubs](http://ndndemo.arl.wustl.edu) (you might want to choose the closest hub to your server). To do this you can run the following command:

        bash ~/ndn-mongo-fileserver/scripts/main/run.sh /ndn/my/cert udp hobo.cs.arizona.edu with-stats
 
This command connects the the NFD instance on your server to `hobo.cs.arizona.edu` hub via UDP tunnel and collects the statistical information of the video streaming service whenever anyone watches your videos. You can find the stats under `~/.chunks-log` directory.
 
3. Set up a webserver and use [ndn-video-frontend](https://github.com/chavoosh/ndn-video-frontend) as your website resources with the following modifications:

    - Update `BASEPREFIX` in [`app.js`](https://github.com/chavoosh/ndn-video-frontend/blob/master/app.js) to your cert name (e.g., `/ndn/my/cert`).
    - Encode, package, and chunk your video(s). To do this, first update `base` in [`driver.sh`](scripts/video/driver.sh) file to your cert (e.g., `/ndn/my/cert/video`), and then run the following command:
    
           (cd ~/ndn-mongo-fileserver/scripts/video && bash driver.sh <absolute-address-of-your-video>)
           
    - Then simply copy the generated HTML file under your webserver directory (e.g., `/var/www/html/my-website`) and add a link to this HTML file in index.html (look at [ndn-video-frontend](https://github.com/chavoosh/ndn-video-frontend) to see a template).

# Reporting Bugs
To report any bugs or features use the project's [issue tracker](https://github.com/chavoosh/ndn-mongo-fileserver/issues).

# License
ndn-mongo-fileserver is an open source project licensed under the GPL version 3. See [COPYING.md](COPYING.md)
for more information.
