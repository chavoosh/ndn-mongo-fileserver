/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019-2020, Regents of the University of Arizona.
 * Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
 *
 * ndn-mongo-fileserver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * ndn-mongo-fileserver is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * ndn-mongo-fileserver, e.g., in COPYING.md file.
 * If not, see <http://www.gnu.org/licenses/>.
 */

#include "core/common.hpp"

#include <ndn-cxx/util/string-helper.hpp>

#include <boost/filesystem.hpp>
#include <boost/range/iterator_range.hpp>

#include <bsoncxx/json.hpp>
#include <bsoncxx/builder/basic/kvp.hpp>
#include <bsoncxx/builder/basic/document.hpp>
#include <bsoncxx/builder/stream/document.hpp>

#include <mongocxx/uri.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>

namespace po = boost::program_options;

namespace ndn {
namespace chunker {

const std::string	DATABASE_NAME = "chunksDB";
const std::string	COLLECTION_NAME = "chunksCollection";
uint32_t FRESHNESS_PERIOD = 10;
uint64_t nFiles = 0;
uint64_t nChunks = 0;
uint16_t code = 0; // 0: success o.w. failure

using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;
using bsoncxx::builder::basic::kvp;
using bsoncxx::builder::basic::make_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::basic::make_array;

class Chunker : noncopyable
{
public:
  Chunker(const std::string& path,
          const std::string& prefix,
          size_t segmentSize,
          uint64_t version,
          bool isVerbose)
  : m_verbose(isVerbose)
  {
    // chech the input path
    m_inputPath = path;
    int found = m_inputPath.find("//");
    while (found != -1) {
      m_inputPath.replace(found, 2, "/");
      found = m_inputPath.find("//");
    }
    if (m_inputPath[m_inputPath.length() - 1] == '/')
      m_inputPath = m_inputPath.substr(0, m_inputPath.length() - 1);

    // determine the root path
    boost::filesystem::path p(m_inputPath);
    try {
      if (checkExistance(m_inputPath)) {
        if (is_regular_file(boost::filesystem::status(p))) {
          int pos = m_inputPath.find_last_of("/");
          if (pos == -1)
            m_root = "";
          else
            m_root = m_inputPath.substr(0, pos + 1);
        }
        else if (is_directory(p))
          m_root = m_inputPath;
        else {
          code = 2;
          std::cerr << p << " is neither a regular file nor a directory\n";
          return;
        }
      }
      else {
        code = 4;
        std::cerr << path << " does not exist..." << std::endl;
      }
    }
    catch (const boost::filesystem::filesystem_error& ex)
    {
      code = 1;
      std::cerr << ex.what() << std::endl;
      return;
    }

    // check the segment size
    if (segmentSize > 8000) {
      code = 1;
      std::cerr << "Max segment size is 8000" << std::endl;
      return;
    }
    m_segmentSize = segmentSize;

    // check input NDN prefix (no tailing slash)
    std::string tempPrefix = prefix;
    while (tempPrefix.length() > 1 && tempPrefix[tempPrefix.length() - 1] == '/') {
      tempPrefix = tempPrefix.substr(0, tempPrefix.length() - 1);
    }

    m_prefix = Name(tempPrefix);
    if (version != 0) {
      m_versionedPrefix = Name(tempPrefix).appendVersion(version);
      m_version = version;
    }
    else {
      m_versionedPrefix = Name(m_prefix).appendVersion();
      m_version = m_versionedPrefix[-1].toVersion();
    }

    m_collection = m_conn[DATABASE_NAME][COLLECTION_NAME];
    mongocxx::options::index index_options{};
    index_options.unique(true);
    m_collection.create_index(make_document(kvp("prefix", 1)), index_options);
  }

  void
  run()
  {
    scan(m_inputPath);
  }

  /**
   * @brief Scan a directory and publish all files under it.
   *
   * The relative address of each file determines the published content name.
   * @p address can point to either a file or directory
   */
  void
  scan(const std::string address)
  {
    if (m_verbose)
      std::cout << "start scanning " << address << std::endl;

    boost::filesystem::path p(address);
    try {
      if (checkExistance(address)) {
        if (is_regular_file(p)) {
          std::cout << "FILE ===> " << address << std::endl;
          if (populateStore(address) != 0)
            return;
        }
        else {
          for(auto& entry :
              boost::make_iterator_range(boost::filesystem::directory_iterator(p), {})) {
            scan(entry.path().string());
          }
        }
      }
      else {
        code = 4;
        std::cerr << address << " does not exist..." << std::endl;
        return;
      }
    }
    catch (const boost::filesystem::filesystem_error& ex)
    {
      code = 1;
      std::cerr << ex.what() << std::endl;
      return;
    }
  }

  bool
  checkExistance(std::string path)
  {
    boost::filesystem::path p(path);
    try {
      if (exists(p))
        return true;
      else
        return false;
    }
    catch (const boost::filesystem::filesystem_error& ex)
    {
      code = 1;
      std::cerr << ex.what() << std::endl;
    }
    return false;
  }

  /**
   * @brief chunk each content and store them in mongodb
   *
   * DATA DOC SCHEME:
   *     {
   *       type: "data"
   *       prefix: <data nameprefix - with version and segment>
   *       version: <current version>
   *       data: <binary of payload>
   *     }
   *
   * VERSION DOC SCHEME:
   *     {
   *       type: "version"
   *       prefix: <namespace - without version and segment>
   *       versions: [ ... ]
   *     }
   *
   * REFERENCE DOC SCHEME:
   *     {
   *       type: "ref"
   *       prefix: <decreamented nameprefix>
   *       ref: <oid of either init_doc or ver_doc>
   *     }
   *
   * @note If the current version already exists in version document no chunks
   *       will be created and the file is skipped.
   */
  int
  populateStore(std::string fpath)
  {
    bool hasInitDocOid = false;
    bsoncxx::oid verDocOid;
    bsoncxx::oid initDocOid;

    //std::cerr << "Loading input ..." << std::endl;

    if(fpath.find(m_root) == std::string::npos) {
      code = 4;
      std::cerr << "An error occured while loading " << fpath << ". Exit ..." << std::endl;
      return 1;
    }

    std::string prefix = fpath;
    prefix.erase(0, m_root.size()).insert(0, "/").insert(0, m_prefix.toUri());
    int found = prefix.find("//");
    // make sure prefix is well-formatted
    while (found != -1) {
      prefix.replace(found, 2, "/");
      found = prefix.find("//");
    }
    Name versionedPrefix = Name(prefix).appendVersion(m_versionedPrefix[-1].toVersion());
    std::vector<uint8_t> buffer(m_segmentSize);
    std::filebuf fb;
    if (fb.open (fpath, std::ios::in)) {
      std::istream is(&fb);
      while (is.good()) {
        is.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        const auto nCharsRead = is.gcount();

        if (nCharsRead > 0) {
          auto data = make_shared<Data>(Name(versionedPrefix).appendSegment(m_store.size()));
          data->setFreshnessPeriod(time::seconds(ndn::chunker::FRESHNESS_PERIOD)); // default: 10s
          data->setContent(buffer.data(), static_cast<size_t>(nCharsRead));
          m_store.push_back(data);
        }
      }
    }
    else {
      code = 2;
      std::cerr << "Failed to open file " << fpath << "\n";
      return 1;
    }

    if (m_store.empty()) {
      code = 1;
      if (m_verbose)
        std::cerr << "No chunk has been created ... Exit ... \n";
      return 1;
    }

    // add this version to the version document
    auto result = m_collection.find_one(document{} << "prefix" << prefix << finalize);
    if(result) { // version document exists
      try {
        bsoncxx::array::view subarray{result->view()["versions"].get_array().value};
        for (const bsoncxx::array::element& sub_ele : subarray) {
          if ((uint64_t)sub_ele.get_int64().value == m_version && m_verbose) {
            // this version exists, exit
            std::cout << "  version [" << m_version << "] exists, skip the file ...\n";
            return 1;
          }
        }

        // add the version
        m_collection.update_one(
          make_document(
            kvp("prefix", prefix)
          ),
          make_document(
            kvp("$addToSet", make_document(
              kvp("versions", (int64_t)m_version))
            )
          )
        );
      }
      catch (const std::exception& e) {
        code = 2;
        std::cerr << e.what() << std::endl;
      }
    }
    else { // version document does not exist, so create it
      try {
        auto retVal = m_collection.insert_one(
          make_document(
            kvp("type", "version"),
            kvp("prefix", prefix),
            kvp("versions", make_array((int64_t)m_version))
          )
        );
        verDocOid = retVal->inserted_id().get_oid().value;
      }
      catch (const std::exception& e) {
        code = 1;
        std::cerr << "version document should not exist. " << e.what() << std::endl;
        return 1;
      }
    }

    // refer decreamented prefixes to version document
    for (int i = Name(prefix).size() - 1; i >=0; --i) {
      std::string cprefix = Name(prefix).getPrefix(i).toUri();
      try{
        m_collection.insert_one(
          make_document(
            kvp("type", "ref"),
            kvp("prefix", cprefix),
            kvp("version", (int64_t)m_version),
            kvp("ref_id", verDocOid.to_string())
          )
        );
      }
      catch (const std::exception& e) {
        break; // do not continue, the rest decreamented prefixes exist
      }
    }

    auto finalBlockId = name::Component::fromSegment(m_store.size() - 1);
    for (const auto& data : m_store) {
      data->setFinalBlock(finalBlockId);
      m_keyChain.sign(*data, security::SigningInfo(""));

      if (!data->hasWire())
        return 1;

      uint32_t nBlob = data->wireEncode().size();
      const auto *zBlob = data->wireEncode().wire();

      // insert the full prefix
      bsoncxx::types::b_binary blob {bsoncxx::binary_sub_type::k_binary,
                                     nBlob, zBlob};

      try {
        auto retVal = m_collection.insert_one(
          make_document(
            kvp("type", "data"),
            kvp("prefix", data->getName().toUri()),
            kvp("version", (int64_t)m_version),
            kvp("data", blob)
          )
        );

        if (!hasInitDocOid) {
          initDocOid = retVal->inserted_id().get_oid().value;
          hasInitDocOid = true;
        }
      }
      catch (const std::exception& e) {
        code = 1;
        if (m_verbose)
          std::cerr << versionedPrefix.toUri() << " exits, no chunk is created..." << std::endl;
        return 1;
      }

      // refer decreamented prefix(es) to initial document
      for (int i = data->getName().size() - 1; i >=0; --i) {
        std::string cprefix = data->getName().getPrefix(i).toUri();
        try{
          m_collection.insert_one(
            make_document(
              kvp("type", "ref"),
              kvp("prefix", cprefix),
              kvp("version", (int64_t)m_version),
              kvp("ref_id", initDocOid.to_string())
            )
          );
        }
        catch (const std::exception& e) {
          break; // do not continue, the rest decreamented prefixes exist
        }
      }
    }

    nFiles++;
    nChunks += m_store.size();

    if (m_verbose) {
      std::cout << "  " << m_store.size() << " chunks is created under prefix {"
                << versionedPrefix.toUri() << "}" << std::endl;
    }
    m_store.clear();
    return 0;
  }

private:
  std::string m_inputPath;  // the path provided by end-user (either a directory or a file)
  std::string m_root;  // root address of input file(s)
  Name m_prefix;       // prefix under which each file publishes (e.g., /ndn/video)
  size_t m_segmentSize;
  uint64_t m_version;
  bool m_verbose;

  Name m_versionedPrefix;
  KeyChain m_keyChain;
  std::vector<shared_ptr<Data>> m_store;

  // mongodb
  mongocxx::instance m_inst{};
  mongocxx::client m_conn{mongocxx::uri{}};
  mongocxx::collection m_collection;
};

} // namespace chunker
} // namespace ndn

static void
usage(std::ostream& os, const std::string& programName, const po::options_description& desc)
{
  os << "Usage: " << programName << " prefix-name [options] \n"
     << "\nChunk the input file or all files under the input directory."
     << "\nNOTE: Files under the input directory are named based on their relative path."
     << "\n\n" << desc;
}

int
main (int argc, char** argv)
{
  std::string programName = argv[0];
  std::string prefix;
  std::string path;
  size_t segmentSize = 4000;
  uint64_t version = 1;
  bool verbose = false;

  po::options_description visibleDesc("Options");
  visibleDesc.add_options()
    ("help,h",         "print this help message and exit")
    ("path,i",         po::value<std::string>(&path),
                       "file or directory path to chunk")
    ("segment-size,s", po::value<size_t>(&segmentSize),
                       "maximum segment size, in bytes")
    ("freshness-period,f", po::value<uint32_t>(&ndn::chunker::FRESHNESS_PERIOD),
                       "freshness period of Data packets in seconds")
    ("version-no,e",   po::value<uint64_t>(&version),
                       "version under which all files will be published")
    ("verbose,v",      po::bool_switch(&verbose),
                       "turn on verbose output (per Interest information)");

  po::options_description hiddenDesc;
  hiddenDesc.add_options()
    ("ndn-name,n", po::value<std::string>(&prefix), "Prefix of published chunks");

  po::positional_options_description p;
  p.add("ndn-name", -1);

  po::options_description optDesc;
  optDesc.add(visibleDesc).add(hiddenDesc);

  po::variables_map vm;
  try {
    po::store(po::command_line_parser(argc, argv).options(optDesc).positional(p).run(), vm);
    po::notify(vm);
  }
  catch (const po::error& e) {
    ndn::chunker::code = 3;
    std::cerr << e.what() << std::endl;
    return 2;
  }
  catch (const boost::bad_any_cast& e) {
    ndn::chunker::code = 3;
    std::cerr << e.what() << std::endl;
    return 2;
  }

  if (vm.count("help") > 0) {
    usage(std::cout, programName, visibleDesc);
    return 0;
  }

  if (prefix.empty() || path.empty()) {
    ndn::chunker::code = 3;
    usage(std::cerr, programName, visibleDesc);
    return 2;
  }

  if (segmentSize > 8000) {
    ndn::chunker::code = 3;
    std::cerr << "Max segment size is 8000\n";
    usage(std::cerr, programName, visibleDesc);
    return 1;
  }

  std::cout << "Exec settings: \n"
            << "\tpath: " << path << "\n"
            << "\tprefix: " << prefix << "\n"
            << "\tfreshness-period: " << ndn::chunker::FRESHNESS_PERIOD << "\n"
            << "\tsegment-size: " << segmentSize << "\n"
            << "\tversion: " << version << std::endl;

  ndn::chunker::Chunker c(path, prefix, segmentSize, version, verbose);
  if (ndn::chunker::code == 0) {
    try {
      c.run();
    }
    catch (const std::exception& e) {
      ndn::chunker::code = 3;
      std::cerr << e.what() << std::endl;
    }
  }
  std::cerr << "(ECode:" << ndn::chunker::code << ")" << std::endl;
  if (ndn::chunker::code == 0) {
    std::cout << "=======================\n"
              << "No. of inserted files: " << ndn::chunker::nFiles << "\n"
              << "No. of inserted chunks: " << ndn::chunker::nChunks << std::endl;
  }
  return 0;
}
