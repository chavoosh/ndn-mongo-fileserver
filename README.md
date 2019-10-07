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

If no error occurred during any step you can safely quite the fileserver.

# Frontend
To learn how to watch the published videos in modern browsers visit [ndn-video-frontend](https://github.com/chavoosh/ndn-video-frontend).

# Reporting Bugs
To report any bugs or features use the project's [issue tracker](https://github.com/chavoosh/ndn-mongo-fileserver/issues).

# License
ndn-mongo-fileserver is an open source project licensed under the GPL version 3. See [COPYING.md](COPYING.md)
for more information.
