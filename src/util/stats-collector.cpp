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

#include <boost/filesystem.hpp>
#include <boost/program_options.hpp>

#include <csignal>
#include <pwd.h>
#include <tuple>

namespace po = boost::program_options;

namespace ndn {
namespace collector {

const char* HOME_DIR = (getenv("HOME") == NULL)
                       ? getpwuid(getuid())->pw_dir
                       : getenv("HOME");
const std::string ROOT_DIR = std::string(HOME_DIR).append("/.chunks-log");
const std::string LOG_PATH = std::string(ROOT_DIR).append("/segment-stats.log");

time_t rawtime;
struct tm* timeinfo;

std::ofstream FOUT;

class StatsCollector : noncopyable
{
public:
  StatsCollector(const std::string& name, bool isVerbose)
    : m_prefix(Name(name))
    , m_verbose(isVerbose)
  {
    boost::filesystem::path p(ROOT_DIR);
    try {
      if (!exists(p)) {
        if (boost::filesystem::create_directories(ROOT_DIR))
          std::cout << "Created directory " << ROOT_DIR << std::endl;
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
  }

  void
  run()
  {
    m_face.setInterestFilter(m_prefix,
                             bind(&StatsCollector::onInterest, this, _1, _2),
                             RegisterPrefixSuccessCallback(),
                             bind(&StatsCollector::onRegisterFailed, this, _1, _2));

    std::cout << "Program is running ...\n";
    m_face.processEvents();
  }

  static void
  printStats(Name stats_name)
  {
    FOUT.open(LOG_PATH, std::ios_base::app);

    std::time(&rawtime);
    timeinfo = std::localtime(&rawtime);
    std::string t = asctime(timeinfo);

    FOUT << t.substr(0, t.length()-1) << "  "
         << stats_name.toUri() << "\n";
    FOUT.close();
  }

private:
  void
  onInterest(const InterestFilter& filter, const Interest& interest)
  {
    // check for stats Interest
    if (m_verbose)
      std::cerr << "Stats Interest: " << interest.getName() << std::endl;

    // collect stats
    printStats(interest.getName());

    // Create Data name based on Interest's name
    Name dataName(interest.getName());
    dataName.appendVersion(0);
    dataName.appendSegment(0);
    static const std::string content = "REPLY TO STAT REPORT";

    // Create a dumb Data packet
    shared_ptr<Data> data = make_shared<Data>();
    data->setName(dataName);
    data->setFreshnessPeriod(10_s); // 10 seconds
    data->setContent(reinterpret_cast<const uint8_t*>(content.data()), content.size());
    data->setFinalBlock(name::Component::fromSegment(0));

    // Sign Data packet with default identity
    m_keyChain.sign(*data);

    // Return Data packet to the requester
    if (m_verbose)
      std::cerr << "Dummy Stats D: " << *data << std::endl;

    m_face.put(*data);
  }

  void
  onRegisterFailed(const Name& prefix, const std::string& reason)
  {
    std::cerr << "ERROR: Failed to register prefix \""
              << prefix << "\" in local hub's daemon (" << reason << ")"
              << std::endl;
    m_face.shutdown();
  }

private:
  Name m_prefix;
  Face m_face;
  bool m_verbose;
  KeyChain m_keyChain;
};

} // namespace collector
} // namespace ndn

void
signal_callback_handler(int signum)
{
  std::cout << "\nStats-Collector is killed ...\n";
  exit(signum);
}

static void
usage(std::ostream& os, const std::string& programName, const po::options_description& desc)
{
  os << "Usage: " << programName << " prefix-name [options] \n"
     << "Collect video streaming statistical info of client side."
     << "\n" << desc;
}

int
main(int argc, char** argv)
{
  std::string programName = argv[0];
  std::string prefix;
  bool verbose = false;

  po::options_description visibleDesc("Options");
  visibleDesc.add_options()
    ("help,h",      "print this help message and exit")
    ("verbose,v",   po::bool_switch(&verbose),
                   "turn on verbose output (per Interest information)");

  po::options_description hiddenDesc;
  hiddenDesc.add_options()
    ("ndn-name,n", po::value<std::string>(&prefix), "Name prefix to collect stats");

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

  // Register signal and signal handler
  std::signal(SIGINT, signal_callback_handler);

  ndn::collector::StatsCollector collector(prefix, verbose);
  try {
    collector.run();
  }
  catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 1;
  }
  return 0;
}
