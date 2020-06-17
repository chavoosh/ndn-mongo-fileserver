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

#include "file-server.hpp"

#include <ndn-cxx/metadata-object.hpp>
#include <ndn-cxx/util/string-helper.hpp>

#include <boost/filesystem.hpp>
#include <boost/range/iterator_range.hpp>

namespace ndn {
namespace fileserver {

struct FileServer::Stats FileServer::stats;

const char* HOME_DIR = (getenv("HOME") == NULL)
                       ? getpwuid(getuid())->pw_dir
                       : getenv("HOME");
const std::string ROOT_DIR = std::string(HOME_DIR).append("/.chunks-log");
const std::string SERVER_STATS_PATH = std::string(ROOT_DIR)
                                      .append("/ndn-file-server.log");

// mongodb
const std::string	DATABASE_NAME = "chunksDB";
const std::string	COLLECTION_NAME = "chunksCollection";

using bsoncxx::stdx::string_view;
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

std::ofstream FOUT;

void
FileServer::printStats()
{
  std::cout << "\tnData: " << stats.nData << "\n";
  std::cout << "\tnInterests: " << stats.nInterests << "\n\n";

  std::time_t end_time = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
  std::string t(ctime(&end_time));

  FOUT.open(SERVER_STATS_PATH, std::ios_base::app);
  FOUT << t.substr(0, t.length()-1) << " nData: " << stats.nData << "\n\n";
  FOUT.close();
}

FileServer::FileServer(const Name& prefix, Face& face, KeyChain& keyChain, std::istream& is,
                   const Options& opts)
  : m_face(face)
  , m_keyChain(keyChain)
  , m_options(opts)
{
  boost::filesystem::path p(ROOT_DIR);
  try {
    if (!exists(p)) {
      if (boost::filesystem::create_directories(ROOT_DIR)) {
        std::cout << "Created directory " << ROOT_DIR << std::endl;
      }
      else {
        std::cout << "Error: Failed to creat directory " << ROOT_DIR << ". Exit ...\n";
        return;
      }
    }
  }
  catch (const boost::filesystem::filesystem_error& ex)
  {
    std::cerr << ex.what() << '\n';
    return;
  }

  if (prefix.size() > 0 && prefix[-1].isVersion()) {
    m_prefix = prefix.getPrefix(-1);
    m_version = prefix[-1].toVersion();
  }
  else if (opts.versionNo != 0) {
    m_prefix = prefix;
    m_version = opts.versionNo;
  }
  else {
    m_prefix = prefix;
    m_version = 0;
  }

  if (m_options.wantShowVersion)
    std::cout << m_version << std::endl;

  // match Interests whose name starts with m_prefix
  face.setInterestFilter(m_prefix,
                         bind(&FileServer::processSegmentInterest, this, _2),
                         RegisterPrefixSuccessCallback(),
                         bind(&FileServer::onRegisterFailed, this, _1, _2));

  m_collection = m_conn[DATABASE_NAME][COLLECTION_NAME];
}

void
FileServer::run()
{
  m_face.processEvents();
}

void
FileServer::processDiscoveryInterest(const Interest& interest)
{
  if (m_options.isVerbose)
    std::cerr << "Discovery Interest: " << interest << std::endl;

  if (!interest.getCanBePrefix()) {
    if (m_options.isVerbose)
      std::cerr << "Discovery Interest lacks CanBePrefix, sending Nack" << std::endl;
    m_face.put(lp::Nack(interest));
    return;
  }

  // first we need to know the version of the solicited content
  Name versionedName;
  if (m_version > 0)
    versionedName = Name(interest.getName().getPrefix(-1)).appendVersion(m_version);
  else {
    versionedName = resolveVersionedName(interest.getName());
    if (versionedName.size() == 0)
      return;
  }

  MetadataObject mobject;
  mobject.setVersionedName(versionedName);

  // make a metadata packet based on the received discovery Interest name
  Data mdata(mobject.makeData(interest.getName(), m_keyChain, m_options.signingInfo));

  if (m_options.isVerbose)
    std::cerr << "Sending metadata: " << mdata << std::endl;

  m_face.put(mdata);
}

void
FileServer::processSegmentInterest(const Interest& interest)
{
  auto start = std::chrono::system_clock::now();

  if (interest.getName()[-1].toUri() == "32=metadata") {
    processDiscoveryInterest(interest);
    return;
  }

  Name name = interest.getName();
  Data data;

  if (m_options.isVerbose) {
    std::cerr << "Interest: " << interest << std::endl;
  }

  // first we need to know the versioned name of the solicited content
  if (!name[-1].isSegment()) {
    if (name[-1].isVersion())
      name.appendSegment(0);
    else {
      if (m_version > 0)
        name = Name(name).appendVersion(m_version);
      else {
        name = resolveVersionedName(interest.getName());
        if (name.size() == 0)
          return;
      }
      name.appendSegment(0);
    }
  }

  // record the stats
  stats.nInterests++;

  // try to retrieve data chunk from mongodb
  auto result = m_collection.find_one(document{} << "prefix" << name.toUri() << finalize);
  if(!result) {
    std::cerr << name.toUri() << " does not exist in the DB\n";
    if (m_options.isVerbose)
      std::cerr << "Sending Nack..." << std::endl;

    m_face.put(lp::Nack(interest));
    return;
  }

  auto da = result->view()["data"].get_binary();
  data = Data(Block((uint8_t*)da.bytes, da.size));

  if (m_options.isVerbose)
    std::cerr << "Data: " << data << std::endl;

  // record the stats
  stats.nData++;

  if (m_options.isVerbose) {
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end - start;

    std::time_t end_time = std::chrono::system_clock::to_time_t(end);
    std::string t(ctime(&end_time));

    FOUT.open(SERVER_STATS_PATH, std::ios_base::app);
    FOUT << t.substr(0, t.length()-1)
         << " Elapsed time of "
         << interest.getName().toUri()
         << ": " << elapsed_seconds.count() << "\n";
    FOUT.close();

    std::cerr << t.substr(0, t.length()-1)
              << " Elapsed time of "
              << interest.getName().toUri()
              << ": " << elapsed_seconds.count() << "\n";
  }

  m_face.put(data);
}

Name
FileServer::resolveVersionedName(Name name)
{
  uint64_t version = 0; // ZERO is considered as invalid version
  Name versionedNameprefix("");

  auto result = m_collection.find_one(document{} << "prefix" << name.toUri() << finalize);
  if (result) { // is this version doc or reference doc?
    if ((std::string)result->view()["type"].get_utf8().value == "ref") {
      result = m_collection.find_one(document{}
                   << "_id"
                   << bsoncxx::oid{(std::string)result->view()["ref_id"].get_utf8().value}
                   << finalize);
    }
    // version document exists
    bsoncxx::array::view subarray{result->view()["versions"].get_array().value};
    for (const bsoncxx::array::element& sub_ele : subarray) {
      version = (uint64_t)sub_ele.get_int64().value;
    }
  }

  if (version == 0) {
    std::cerr << "No version is available for " << name.toUri() << " (No VERSION DOC exists)\n";
  }
  else {
    versionedNameprefix = Name((std::string)result->view()["prefix"].get_utf8().value);
    versionedNameprefix.appendVersion(version);
  }
  return versionedNameprefix;
}

void
FileServer::onRegisterFailed(const Name& prefix, const std::string& reason)
{
  std::cerr << "ERROR: Failed to register prefix '"
            << prefix << "' (" << reason << ")" << std::endl;
  m_face.shutdown();
}

} // namespace fileserver
} // namespace ndn
