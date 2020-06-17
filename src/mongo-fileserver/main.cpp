/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019-2020, Regents of the University of Arizona.
 * Author: Chavoosh Ghasemi <chghasemi@cs.arizona.edu>
 *         [ndn-tools](https://github.com/named-data/ndn-tools/tree/master/tools/chunks/putchunks)
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
#include <signal.h>
#include <csignal>

namespace po = boost::program_options;

namespace ndn {
namespace fileserver {

static void
usage(std::ostream& os, const std::string& programName, const po::options_description& desc)
{
  os << "Usage: " << programName << " [options] ndn:/name\n"
     << "\n"
     << "Serve data under the specified prefix.\n"
     << "\n"
     << desc;
}

void
signal_callback_handler(int signum)
{
  ndn::fileserver::FileServer::printStats();
  exit(signum);
}

static int
main(int argc, char* argv[])
{
  std::string programName = argv[0];
  std::string prefix;
  std::string signingStr;
  FileServer::Options opts;

  po::options_description visibleDesc("Options");
  visibleDesc.add_options()
    ("help,h",          "print this help message and exit")
    ("freshness,f",     po::value<time::milliseconds::rep>()->default_value(opts.freshnessPeriod.count()),
                        "FreshnessPeriod of the published Data packets, in milliseconds")
    ("print-data-version,p", po::bool_switch(&opts.wantShowVersion),
                             "print Data version to the standard output")
    ("size,s",          po::value<size_t>(&opts.maxSegmentSize)->default_value(opts.maxSegmentSize),
                        "maximum chunk size, in bytes")
    ("version-no,e", po::value<uint64_t>(&opts.versionNo)->default_value(opts.versionNo),
                     "version under which all files will be published (0 means random version number)")
    ("signing-info,S",  po::value<std::string>(&signingStr), "signing information")
    ("quiet,q",         po::bool_switch(&opts.isQuiet), "turn off all non-error output")
    ("verbose,v",       po::bool_switch(&opts.isVerbose), "turn on verbose output (per Interest information)")
    ;

  po::options_description hiddenDesc;
  hiddenDesc.add_options()
    ("ndn-name,n", po::value<std::string>(&prefix), "NDN name for the served content");

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
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 2;
  }
  catch (const boost::bad_any_cast& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 2;
  }

  if (vm.count("help") > 0) {
    usage(std::cout, programName, visibleDesc);
    return 0;
  }

  if (prefix.empty()) {
    usage(std::cerr, programName, visibleDesc);
    return 2;
  }

  opts.freshnessPeriod = time::milliseconds(vm["freshness"].as<time::milliseconds::rep>());
  if (opts.freshnessPeriod < time::milliseconds::zero()) {
    std::cerr << "ERROR: FreshnessPeriod cannot be negative" << std::endl;
    return 2;
  }

  if (opts.maxSegmentSize < 1 || opts.maxSegmentSize > MAX_NDN_PACKET_SIZE) {
    std::cerr << "ERROR: Maximum chunk size must be between 1 and " << MAX_NDN_PACKET_SIZE << std::endl;
    return 2;
  }

  if (opts.versionNo > std::numeric_limits<uint64_t>::max() - 1) {
    std::cerr << "ERROR: version number must be less than " << std::numeric_limits<uint64_t>::max() << std::endl;
    return 2;
  }

  try {
    opts.signingInfo = security::SigningInfo(signingStr);
  }
  catch (const std::invalid_argument& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 2;
  }

  if (opts.isQuiet && opts.isVerbose) {
    std::cerr << "ERROR: Cannot be quiet and verbose at the same time" << std::endl;
    return 2;
  }

  try {
    Face face;
    KeyChain keyChain;
    FileServer fserver(prefix, face, keyChain, std::cin, opts);
    fserver.run();
  }
  catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 1;
  }

  return 0;
}

} // namespace fileserver
} // namespace ndn

int
main(int argc, char* argv[])
{
  // Register signal and signal handler
  std::signal(SIGINT, ndn::fileserver::signal_callback_handler);

  return ndn::fileserver::main(argc, argv);
}
