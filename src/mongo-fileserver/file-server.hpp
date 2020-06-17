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

#ifndef NDN_FILESERVER_HPP
#define NDN_FILESERVER_HPP

#include "core/common.hpp"

#include <bsoncxx/json.hpp>
#include <bsoncxx/builder/basic/kvp.hpp>
#include <bsoncxx/builder/basic/document.hpp>
#include <bsoncxx/builder/stream/document.hpp>

#include <mongocxx/uri.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>


namespace ndn {
namespace fileserver {

/**
 * @brief Server data chunks under a specific nameprefix
 *
 * Read Data chunks from MongoDB, packetize them and send them out.
 * If the version is not presented the latest available version of the
 * content will be used. Read (/src/util/README.md) for more information.
 */

class FileServer : noncopyable
{
public:
  struct Options
  {
    security::SigningInfo signingInfo;
    time::milliseconds freshnessPeriod{10000};
    size_t maxSegmentSize = MAX_NDN_PACKET_SIZE >> 1;
    bool isQuiet = false;
    bool isVerbose = false;
    bool wantShowVersion = false;
    uint64_t versionNo = 0;
  };

  struct Stats
  {
    uint32_t nData = 0; // counter for outgoing Data packets
    uint32_t nInterests = 0; // counter for incoming Interest packets
  };

public:
  /**
   * @brief Create the FileServer
   *
   * @param prefix prefix used to publish data
   */
  FileServer(const Name& prefix, Face& face, KeyChain& keyChain, std::istream& is,
             const Options& opts);

  /**
   * @brief Run the FileServer
   */
  void
  run();

public:
  /**
   * @brief Print statistical information content retrieval
   */
  static void
  printStats();

private:
  /**
   * @brief Respond with a metadata packet containing the versioned content name
   */
  void
  processDiscoveryInterest(const Interest& interest);

  /**
   * @brief Respond with the requested segment of content
   */
  void
  processSegmentInterest(const Interest& interest);

  void
  onRegisterFailed(const Name& prefix, const std::string& reason);

  /**
   * @brief Resolve the latest verioned nameprefix for @p name from mongodb
   *
   * @note The resolved versioned name contains nameprefix of the first found
   *       content according to @p name.
   *       E.g., assuming in there is one content
   *       in the DB, named `/ndn/test/readme.md`. Then the resolved versioned
   *       name for Interests with either of the following names:
   *          `/ndn`
   *          `/ndn/test`
   *          `/ndn/test/readme.md`
   *       will be translated into `/ndn/test/readme.md/<version>`.
   */
  Name
  resolveVersionedName(Name name);

public:
  // static variable member
  static Stats stats;

private:
  Name m_prefix;
  Name m_versionedPrefix;
  uint64_t m_version;
  Face& m_face;
  KeyChain& m_keyChain;
  const Options m_options;

  // mongodb
  mongocxx::instance m_inst{};
  mongocxx::client m_conn{mongocxx::uri{}};
  mongocxx::collection m_collection;
};

} // namespace fileserver
} // namespace ndn

#endif // NDN_FILESERVER_HPP
