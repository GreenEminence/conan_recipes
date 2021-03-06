/*
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying
 *  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
 */
#ifndef TWOBLUECUBES_CATCH_REPORTER_TEAMCITY_HPP_INCLUDED
#define TWOBLUECUBES_CATCH_REPORTER_TEAMCITY_HPP_INCLUDED

#include <catch2/catch_timer.hpp>
#include <catch2/reporters/catch_reporter_bases.hpp>

#include <cstring>

#ifdef __clang__
#   pragma clang diagnostic push
#   pragma clang diagnostic ignored "-Wpadded"
#endif

namespace Catch {

    struct TeamCityReporter : StreamingReporterBase {
        TeamCityReporter( ReporterConfig const& _config )
        :   StreamingReporterBase( _config )
        {
            m_reporterPrefs.shouldRedirectStdOut = true;
        }

        ~TeamCityReporter() override;

        static std::string getDescription() {
            using namespace std::string_literals;
            return "Reports test results as TeamCity service messages"s;
        }

        void skipTest( TestCaseInfo const& /* testInfo */ ) override {}

        void noMatchingTestCases( std::string const& /* spec */ ) override {}

        void testGroupStarting(GroupInfo const& groupInfo) override;
        void testGroupEnded(TestGroupStats const& testGroupStats) override;


        void assertionStarting(AssertionInfo const&) override {}

        bool assertionEnded(AssertionStats const& assertionStats) override;

        void sectionStarting(SectionInfo const& sectionInfo) override {
            m_headerPrintedForThisSection = false;
            StreamingReporterBase::sectionStarting( sectionInfo );
        }

        void testCaseStarting(TestCaseInfo const& testInfo) override;

        void testCaseEnded(TestCaseStats const& testCaseStats) override;

    private:
        void printSectionHeader(std::ostream& os);

    private:
        bool m_headerPrintedForThisSection = false;
        Timer m_testTimer;
    };

} // end namespace Catch

#ifdef __clang__
#   pragma clang diagnostic pop
#endif

#endif // TWOBLUECUBES_CATCH_REPORTER_TEAMCITY_HPP_INCLUDED
