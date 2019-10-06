## ndn-mongo-fileserver
Upon receiving an Interest, the fileserver sends a query to MongoDB driver to find a document for the
solicited content. If the resolved document was a referenceDoc, the referenced document will be fetched.
If the referenced document was a dataDoc, file server sends back a Data packet including the payload of
the dataDoc. However, if the referenced document was versionDoc, the file server uses the latest available
version, fetches the dataDoc of the first segment of the corresponded version, makes a Data packet based on
it, and sends it back to the consuemr.

For instance, assume there is nothing in the database except `/ndn/test/README.md` file. If the consumer
sends an Interest out with nameprefix `/`, `/ndn`, `/ndn/test`, or `/ndn/test/README.md` then the fileserver
will fetch the versionDoc and find content's latest version. Then it will ask for data document
`/ndn/test/README.md/<latest-version>/%FD%00`. Upon fetching the dataDoc, it will send a Data packet back
that includes the first segment of the content and the full name of it (i.e., `/ndn/test/README.md/<latest-version>/%FD%00`).
Then the consumer will simply fetch the rest of the segments, since he knows the full name of the content.

If the consumer asks for `/ndn/test/README.md/<specific-version>` or `/ndn/test/README.md/<specific-version>/<specific-segment>`
then file server will return the first segment or the solicited segment, respectively.

If file server could not resolve any dataDoc to answer an Interest, it will send back a Nack.
