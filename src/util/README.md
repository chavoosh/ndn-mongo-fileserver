# Chunker
Every file/content in NDN needs to be broken down to smaller pieces, called *chunks*. A given content
can have one or more chunks - depending on the size of the content and chunks. Chunker is a small program
that chunks the input file (or all the files under the input directory) and put the chunks in a database
with a specific arrangement.

The following command chunks `README.md` file under nameprefix `/ndn/test`, with version number 1, where
the max size of each chunk is 1KB:

       $ chunker /ndn/test -i ~/ndn-mongo-fileserver/README.md -s 1000 -e 1

And here is how Chunker populate the database for this file:

- Create a new document for `/ndn/test/README.md` that contains all available versions of this file (this document is called ***versionDoc***).
- Create a new document for the following name prefixes and point them to the versionDoc (these documents are called ***referenceDoc***):
```
/
/ndn
/ndn/test
/ndn/test/README.md
```
- Create a new document for each chunk with name `/ndn/test/README.md/<version>/<segment>` that contain the payload
of the corresponding chunk (these documents are called ***dataDoc***).
- Create a new referenceDoc for `/ndn/test/README.md/<version>` and point it to the first (chunk zero) dataDoc.

Here is a diagram of created documents for content `/ndn/test/README.md` with a given version number.
<img src="https://serving.photos.photobox.com/8604621875f706f4086cb7f6c0809f8ea9db9e5ae015b11086215116c237fd554a1ca0c8.jpg" alt="alt text" width="500px">

# Stats-Collector
stats-collector is developed to collect statistical information about video streaming service performance
on the client side. Upon receiving a file by by the consumer the consumer's browser sends an Interest out
to report the performance of file retrieval for the corresponding file. To avoid affecting the performance
of file retrieval process, this Interest is sent out when the file is completely retrieved. The statistics
are embedded in the Interest name and the namespace we use for statistics collection is
`/ndn/web/64=stats/<TYPE>=<VALUE>/../<TYPE>= <VALUE>`, where `/ndn/web` is a certified name prefix, `stats`
is a special name component (with type `64`), and `<TYPE>` and `<VALUE>` are the type and value of reporting
information, respectively.

Here is the list of current TYPE-VALUE paris:
```
[TYPE]              [VALUE]
=======             ========
status            : DONE | FAIL
hub               : The NDN testbed hub that the consumer is connected to
ip                : Public IP address of the consumer
estBW             : Consumer's estimated goodput
nRetransmissions  : Number of Interest retransmissions
nTimeouts         : Number of Interest timeouts
nNacks            : Number of received nacks
nSegments         : Number of received segments
delay             : Amount of time to download the current file
avgRTT            : Average RTT over all chunks
avgJitter         : Average jitter over all chunks
session           : A unique number to identify each session
startupDelay      : Amount of time from loading the page to starting video playback
rebufferings      : Number of rebufferings during video playback
bufferingDuration : Duration of a single rebuffering


NOTE:
1. Everytime the consumer starts watching a video (even by reloading the current browser tab) a new session will be created.
2. Rebuffering includes the following behaviors:
    - When the video playback stops to receive more video segments without consumer interaction (i.e., video hiccups).
    - When the consumer fast forwards or rewinds, so the player must receive initial video segments at that position.
    - When the consumer pauses the video (the duration of this rebuffering is determined by amount of time between pausing and resuming the video by the consumer).
```
To see the options of stats-collector program run `$ stats-collector` or `$ <path-to-ndn-cxx>/build/examples/stats-collector`.
Collected stats can be found under `~/.chunks` directory on the server.

**IMPORTANT NOTE**: Timestamp in the log files is derived from server's localtime zone, so make sure the
server's time zone is set to a desirable one you can check timezone on an Ubuntu server by using this
command `$ timedatectl` (for more info see [this](https://vitux.com/how-to-change-the-timezone-on-your-ubuntu-system/)).
