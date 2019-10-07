# NDN Seves Files From MongoDB

NDN-MONGO-FILESERVER tool-bundle is part of [iViSA project](https://ivisa.named-data.net) which includes the following tools:
1. [ndn-mongo-fileserver](src/mongo-fileserver)
2. [chunker](src/util)
3. [stats-collector](src/util)

## INSTALL
Take the following steps to install this tool-bundle.

### Prerequisites
Install the mentioned version of the following packages:
- [ndn-cxx](https://github.com/named-data/ndn-cxx) (release 0.6.6)
- [NFD](https://github.com/named-data/NFD) (release 0.6.6)
- [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-on-ubuntu)

### Build Steps
To configure, compile, and install this tool-bundle, type the following commands
in the source directory:

      CXXFLAGS="-I/usr/local/include/mongocxx/v_noabi \
                -I/usr/local/include/bsoncxx/v_noabi" \
                LINKFLAGS="-L/usr/local/lib -lmongocxx \
                -lbsoncxx" ./waf configure
      ./waf
      sudo ./waf install

# Reporting Bugs
To report any bugs or features use the project's issue tracker.

# License
ndn-mongo-fileserver is an open source project licensed under the GPL version 3. See [COPYING.md](COPYING.md)
for more information.
