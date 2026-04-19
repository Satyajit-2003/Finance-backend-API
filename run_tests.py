#!/usr/bin/env python3
"""
Comprehensive test suite for Finance SMS Logger Flask Application.
Tests SMS parser, Google Sheets integration, API endpoints, and caching functionality.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --api-only         # Run only API endpoint tests
    python run_tests.py --local            # Run tests against local server
    python run_tests.py --extended         # Run extended tests with edge cases
    python run_tests.py --quick            # Run quick tests (no network)
"""

import dotenv
from config import ValidationRules
from sms_parser import get_transaction_info
from config import get_env_variable
from sheet_manager import SheetManager
import os
import sys
import json
import time
import random
import requests
import csv
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
from pprint import pprint

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))


dotenv.load_dotenv()


class ComprehensiveTestSuite:
    """Comprehensive test suite for the Finance SMS Logger application."""

    def __init__(self, base_url="https://finance-backend-api.onrender.com"):
        self.base_url = base_url.rstrip("/")
        self.sheet_manager = None
        self.api_key = get_env_variable("API_KEY", "test-api-key")
        self.auth_headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        self.test_results = {
            "parser": {"passed": 0, "failed": 0},
            "sheets": {"passed": 0, "failed": 0},
            "api": {"passed": 0, "failed": 0},
            "cache": {"passed": 0, "failed": 0},
            "auth": {"passed": 0, "failed": 0},
            "extended": {"passed": 0, "failed": 0},
        }

    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 STARTING COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print()

        # Test 1: SMS Parser
        self.test_sms_parser_direct()
        print()

        # Test 2: Google Sheets Integration
        self.test_google_sheets_integration()
        print()

        # Test 3: Monthly Spending Statistics
        self.test_monthly_spending_stats()
        print()

        # Test 4: Authentication Middleware
        self.test_authentication_middleware()
        print()

        # Test 5: API Endpoints
        self.test_api_endpoints()
        print()

        # Test 6: Performance and Caching
        self.test_performance_and_caching()
        print()

        # Summary
        self.print_test_summary()

    def run_api_only_tests(self):
        """Run only API endpoint tests."""
        print("🚀 RUNNING API-ONLY TESTS")
        print("=" * 60)
        print()

        # Test authentication
        self.test_authentication_middleware()
        print()

        # Test API endpoints
        self.test_api_endpoints()
        print()

        # Summary
        self.print_test_summary()

    def run_extended_tests(self):
        """Run extended tests with edge cases and error scenarios."""
        print("🚀 RUNNING EXTENDED API TESTS")
        print("=" * 60)
        print()

        # Basic API tests
        self.test_authentication_middleware()
        print()
        self.test_api_endpoints()
        print()

        # Extended tests
        self.test_error_scenarios()
        print()
        self.test_edge_cases()
        print()
        self.test_response_formats()
        print()

        # Summary
        self.print_test_summary()

    def run_quick_tests(self):
        """Run quick tests without network dependencies."""
        print("🚀 RUNNING QUICK LOCAL TESTS")
        print("=" * 60)
        print()

        # Test 1: SMS Parser (always local)
        self.test_sms_parser_direct()
        print()

        # Test 2: If local server is configured, run API tests
        if self.base_url.startswith("http://127.0.0.1") or self.base_url.startswith(
            "http://localhost"
        ):
            print("🌐 Local server detected - running API tests...")
            print()
            self.test_authentication_middleware()
            print()
            self.test_api_endpoints()
            print()
        else:
            print("ℹ️  Remote server configured - skipping API tests in quick mode")
            print("   (Use --local flag to test against local server)")
            print()

        # Summary
        self.print_test_summary()
        print()

        # Test 2: Google Sheets Integration
        self.test_google_sheets_integration()
        print()

        # Test 3: Monthly Spending Statistics
        self.test_monthly_spending_stats()
        print()

        # Test 4: Authentication Middleware
        self.test_authentication_middleware()
        print()

        # Test 5: API Endpoints
        self.test_api_endpoints()
        print()

        # Test 6: Performance and Caching
        self.test_performance_and_caching()
        print()

        # Summary
        self.print_test_summary()

    def test_sms_parser_direct(self):
        """Test the SMS parser directly with various message formats."""
        print("📱 TESTING SMS PARSER DIRECTLY")
        print("=" * 60)

        test_messages = [
            "Your slice credit card transaction of Rs. 35.00 on bgl 16 global count is successful. If not you, call - slice"
            "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
            "Your a/c no. XX1234 has been credited with INR 5,000.00 on 10-03-23 through NEFT. Avl Bal: INR 12,435.50",
            "INR 1,500.00 spent on HDFC Card XX7890 at AMAZON RETAIL on 15-04-23. Avl limit: INR 35,000.00",
            "Your Paytm wallet was debited for Rs. 299.00 for payment to NETFLIX. Avl Bal: Rs. 1,211.50",
            "Rs.435.00 debited from your Slice Card for Swiggy order on 28-06-23. Outstanding: Rs.1,235.00",
        ]

        for i, sms in enumerate(test_messages, 1):
            print(f"\n🔍 Test {i}:")
            print(f"SMS: {sms}")

            try:
                transaction_info = get_transaction_info(sms)
                if transaction_info:
                    transaction_data = transaction_info.to_dict()
                    is_valid = ValidationRules.is_valid_transaction(
                        transaction_data, sms
                    )

                    print("✅ Parsed successfully:")
                    print(json.dumps(transaction_data, indent=2))
                    print(f"🔍 Valid transaction: {is_valid}")

                    self.test_results["parser"]["passed"] += 1
                else:
                    print("❌ Failed to parse SMS")
                    self.test_results["parser"]["failed"] += 1

            except Exception as e:
                print(f"❌ Error parsing SMS: {e}")
                self.test_results["parser"]["failed"] += 1

            print("-" * 50)

    def test_google_sheets_integration(self):
        """Test Google Sheets integration."""
        print("📊 TESTING GOOGLE SHEETS INTEGRATION")
        print("=" * 60)

        try:
            # Initialize sheet manager
            self.sheet_manager = SheetManager()

            # Check if services are initialized
            if not self.sheet_manager.service:
                print("❌ Google services not initialized")
                print("Please check your Google API credentials at:")
                print("   credentials/google-credentials.json")
                self.test_results["sheets"]["failed"] += 1
                return False

            print("✅ Google Sheets service initialized successfully")
            print(
                f"📄 Using shared workbook: {self.sheet_manager.shared_workbook_id}")
            self.test_results["sheets"]["passed"] += 1

            # Test creating a monthly sheet
            test_date = datetime(2025, 7, 14)
            print(
                f"\n🔍 Testing sheet creation for {test_date.strftime('%B %Y')}...")

            sheet_id = self.sheet_manager.get_or_create_monthly_sheet(
                test_date)
            print(f"✅ Sheet created/retrieved in workbook: {sheet_id}")
            self.test_results["sheets"]["passed"] += 1

            # Test transaction insertion
            test_sms = "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23."
            print(f"\n🔍 Testing transaction insertion...")
            print(f"SMS: {test_sms}")

            # Parse transaction
            transaction_info = get_transaction_info(test_sms)
            if transaction_info:
                transaction_data = transaction_info.to_dict()
                success, _row = self.sheet_manager.insert_transaction_data(
                    transaction_data, test_date
                )

                if success:
                    print("✅ Transaction inserted successfully")
                    sheet_url = self.sheet_manager.get_sheet_url(test_date)
                    print(f"📊 Sheet URL: {sheet_url}")
                    self.test_results["sheets"]["passed"] += 1
                else:
                    print("❌ Transaction insertion failed")
                    self.test_results["sheets"]["failed"] += 1
            else:
                print("❌ Failed to parse test SMS")
                self.test_results["sheets"]["failed"] += 1

            # Check sheet statistics
            stats = self.sheet_manager.get_sheet_statistics()
            print(f"\n📈 Sheet statistics: {stats}")

            return True

        except Exception as e:
            print(f"❌ Google Sheets integration test failed: {e}")
            self.test_results["sheets"]["failed"] += 1
            return False

    def test_monthly_spending_stats(self):
        """Test monthly spending statistics functionality."""
        print("💰 TESTING MONTHLY SPENDING STATISTICS")
        print("=" * 60)

        if not self.sheet_manager:
            print("❌ Sheet manager not initialized, skipping spending stats test")
            return

        # Test September 2025 (which should have data from our tests)
        month = "September"
        year = 2025

        print(f"🔍 Testing spending stats for {month} {year}...")

        try:
            # First call (no cache)
            start_time = time.time()
            result = self.sheet_manager.get_month_spends(month, year)
            first_call_time = time.time() - start_time

            print(f"⏱️  First call took: {first_call_time:.3f} seconds")

            if "error" in result or "empty" in result:
                print(f"⚠️  Sheet not found or empty: {result}")
                self.test_results["cache"]["failed"] += 1
            else:
                print("✅ Success!")
                print(f"📊 Total Spend: ₹{result['total_spend']:.2f}")
                print(f"📋 Categories: {len(result['categories'])}")

                if result["categories"]:
                    print("📈 Top 3 categories:")
                    sorted_cats = sorted(
                        result["categories"].items(),
                        key=lambda x: x[1]["amount"],
                        reverse=True,
                    )
                    for i, (cat, cat_data) in enumerate(sorted_cats[:3]):
                        print(f"   {i+1}. {cat}: ₹{cat_data['amount']:.2f}")

                self.test_results["cache"]["passed"] += 1

                # Test cache (second call)
                print("\n🔄 Testing cache (second call)...")
                start_time = time.time()
                result2 = self.sheet_manager.get_month_spends(month, year)
                second_call_time = time.time() - start_time

                print(f"⏱️  Second call took: {second_call_time:.3f} seconds")

                if result == result2:
                    print("✅ Cache working correctly - same results returned")
                    if second_call_time < first_call_time:
                        if second_call_time > 0:
                            print(
                                f"⚡ Cache speedup: {first_call_time/second_call_time:.1f}x faster"
                            )
                        else:
                            print("⚡ Cache speedup: Instant response!")
                    self.test_results["cache"]["passed"] += 1
                else:
                    print("❌ Cache not working - different results returned")
                    self.test_results["cache"]["failed"] += 1

                # Test cache statistics
                print(
                    f"\n📦 Cache entries: {len(self.sheet_manager.monthly_spends_cache)}"
                )
                for sheet_name, (
                    data,
                    timestamp,
                ) in self.sheet_manager.monthly_spends_cache.items():
                    cache_age = time.time() - timestamp
                    print(
                        f"   🔸 {sheet_name}: cached {cache_age:.1f} seconds ago")

        except Exception as e:
            print(f"❌ Error testing spending stats: {e}")
            self.test_results["cache"]["failed"] += 1

    def test_authentication_middleware(self):
        """Test authentication middleware for API endpoints."""
        print("🔐 TESTING AUTHENTICATION MIDDLEWARE")
        print("=" * 60)

        # Check if API key is configured
        api_key = get_env_variable("API_KEY")
        if not api_key:
            print(
                "⚠️  API_KEY environment variable not set. Using test key for testing."
            )
            api_key = "test-api-key"

        # Test 1: Health endpoint should not require auth
        print("\n🏥 Testing health endpoint (no auth required)...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint accessible without authentication")
                self.test_results["auth"]["passed"] += 1
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["auth"]["failed"] += 1
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            self.test_results["auth"]["failed"] += 1

        # Test 2: API endpoints should require auth
        print("\n🚫 Testing API endpoints without authentication...")
        test_endpoints = [
            ("GET", "/api/v1/stats?month_year=July-2025"),
            ("GET", "/api/v1/check-auth"),
            ("POST", "/api/v1/parse-sms", {"text": "Test SMS"}),
            (
                "POST",
                "/api/v1/transactions",
                {
                    "date": "2025-09-05T14:30:00",
                    "transaction_data": {"Amount": "150.00"},
                },
            ),
        ]

        for method, endpoint, *data in test_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data[0] if data else None,
                        timeout=5,
                    )
                else:
                    response = requests.get(
                        f"{self.base_url}{endpoint}", timeout=5)

                if response.status_code == 403:
                    print(
                        f"✅ {method} {endpoint} correctly requires authentication")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print(
                        f"❌ {method} {endpoint} should require auth (got {response.status_code})"
                    )
                    self.test_results["auth"]["failed"] += 1
            except Exception as e:
                print(f"❌ {method} {endpoint} test error: {e}")
                self.test_results["auth"]["failed"] += 1

        # Test 3: API endpoints with valid auth should work
        print("\n✅ Testing API endpoints with valid authentication...")
        headers = {"X-API-KEY": api_key}

        for method, endpoint, *data in test_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data[0] if data else None,
                        headers=headers,
                        timeout=5,
                    )
                else:
                    response = requests.get(
                        f"{self.base_url}{endpoint}", headers=headers, timeout=5
                    )

                # Should not get 403 with valid auth
                if response.status_code != 403:
                    print(f"✅ {method} {endpoint} accepts valid authentication")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print(f"❌ {method} {endpoint} rejected valid auth")
                    self.test_results["auth"]["failed"] += 1
            except Exception as e:
                print(f"❌ {method} {endpoint} valid auth test error: {e}")
                self.test_results["auth"]["failed"] += 1

        # Test 4: API endpoints with invalid auth should fail
        print("\n🔑 Testing API endpoints with invalid authentication...")
        invalid_headers = {"X-API-KEY": "invalid-key-123"}

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats?month_year=July-2025",
                headers=invalid_headers,
                timeout=5,
            )
            if response.status_code == 403:
                response_data = response.json()
                if "Authentication failed" in response_data.get("error", ""):
                    print("✅ Invalid API key correctly rejected")
                    self.test_results["auth"]["passed"] += 1
                else:
                    print("❌ Wrong error message for invalid key")
                    self.test_results["auth"]["failed"] += 1
            else:
                print(
                    f"❌ Invalid key should return 403 (got {response.status_code})")
                self.test_results["auth"]["failed"] += 1
        except Exception as e:
            print(f"❌ Invalid auth test error: {e}")
            self.test_results["auth"]["failed"] += 1

    def test_api_endpoints(self):
        """Test API endpoints."""
        print("🌐 TESTING API ENDPOINTS")
        print("=" * 60)

        # Get API key for authenticated requests
        self.api_key = get_env_variable("API_KEY", "test-api-key")
        self.auth_headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        # Test health check
        self._test_health_endpoint()

        # Test check-auth endpoint
        self._test_check_auth_endpoint()

        # Test SMS logging endpoint
        self._test_sms_logging_endpoint()

        # Test parser test endpoint
        self._test_parser_endpoint()

        # Test sheet info endpoint
        self._test_sheet_info_endpoint()

        # Test stats endpoints
        self._test_stats_endpoints()

        # Test add transaction endpoint (direct API add)
        self._test_add_transaction_endpoint()

        # Test transaction management endpoints
        self._test_transaction_management()

        # Test uncategorized dates endpoint (month-wise)
        self._test_uncategorized_dates_endpoint()

        # Test endpoint validation
        self._test_endpoint_validation()

    def _test_uncategorized_dates_endpoint(self):
        """Test uncategorized dates endpoint with backdated data and cleanup."""
        print("\n🔍 Testing uncategorized dates endpoint...")

        inserted_rows = []
        expected_dates_by_month = {"July-2025": set(), "August-2025": set()}

        try:
            random.seed(int(time.time()))

            # Step 1: Insert uncategorized test transactions for backdated months.
            print("  ↳ 1. Inserting backdated uncategorized transactions...")
            for month_year, month_num in (("July-2025", 7), ("August-2025", 8)):
                random_days = random.sample(range(5, 26), 2)
                for idx, day in enumerate(random_days, start=1):
                    date_str = f"2025-{month_num:02d}-{day:02d}"
                    unique_amount = f"{200 + (month_num * 10) + idx + random.random():.2f}"

                    payload = {
                        "date": f"{date_str}T11:30:00",
                        "transaction_item": {
                            "Amount": unique_amount,
                            "Type": "Select",
                            "Notes": f"Uncategorized endpoint test {month_year} {date_str}",
                            "Account": "ACCOUNT - 9999",
                        },
                    }

                    response = requests.post(
                        f"{self.base_url}/api/v1/transactions",
                        headers=self.auth_headers,
                        json=payload,
                        timeout=15,
                    )

                    if response.status_code == 201:
                        data = response.json().get("data", {})
                        row_index = data.get("row_index")
                        if row_index:
                            inserted_rows.append(
                                {
                                    "sheet_name": month_year,
                                    "row_index": row_index,
                                }
                            )
                            expected_dates_by_month[month_year].add(date_str)
                            print(
                                f"    ✅ Inserted {month_year} transaction on {date_str} (row {row_index})"
                            )
                        else:
                            print(
                                f"    ❌ Missing row_index in insert response for {date_str}"
                            )
                            self.test_results["api"]["failed"] += 1
                    else:
                        print(
                            f"    ❌ Insert failed for {date_str}: {response.status_code}"
                        )
                        print(f"       Response: {response.text}")
                        self.test_results["api"]["failed"] += 1

            if not inserted_rows:
                print("    ❌ No rows inserted; skipping endpoint assertions")
                self.test_results["api"]["failed"] += 1
                return

            # Step 2: Verify endpoint month-wise.
            print("  ↳ 2. Verifying uncategorized dates by month...")
            for month_year in ("July-2025", "August-2025"):
                response = requests.get(
                    f"{self.base_url}/api/v1/transactions/uncategorized?month_year={month_year}",
                    headers={"X-API-KEY": self.api_key},
                    timeout=15,
                )

                if response.status_code != 200:
                    print(
                        f"    ❌ Endpoint failed for {month_year}: {response.status_code}"
                    )
                    print(f"       Response: {response.text}")
                    self.test_results["api"]["failed"] += 1
                    continue

                body = response.json()
                data = body.get("data", {})
                returned_dates = set(data.get("uncategorized_dates", []))
                expected_dates = expected_dates_by_month[month_year]

                if expected_dates.issubset(returned_dates):
                    print(
                        f"    ✅ {month_year}: endpoint returned expected dates {sorted(expected_dates)}"
                    )
                    self.test_results["api"]["passed"] += 1
                else:
                    print(
                        f"    ❌ {month_year}: missing expected dates. Expected subset={sorted(expected_dates)}, got={sorted(returned_dates)}"
                    )
                    self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Uncategorized endpoint test connection error: {e}")
            self.test_results["api"]["failed"] += 1
        except Exception as e:
            print(f"    ❌ Uncategorized endpoint test error: {e}")
            self.test_results["api"]["failed"] += 1
        finally:
            # Step 3: Cleanup inserted rows (delete in descending row order per sheet).
            print("  ↳ 3. Cleaning up inserted uncategorized test rows...")
            cleanup_failed = False
            for row in sorted(
                inserted_rows,
                key=lambda r: (r["sheet_name"], r["row_index"]),
                reverse=True,
            ):
                try:
                    delete_resp = requests.delete(
                        f"{self.base_url}/api/v1/transactions",
                        headers=self.auth_headers,
                        json={
                            "sheet_name": row["sheet_name"],
                            "row_index": row["row_index"],
                        },
                        timeout=15,
                    )
                    if delete_resp.status_code == 200:
                        print(
                            f"    ✅ Deleted test row {row['row_index']} from {row['sheet_name']}"
                        )
                    else:
                        cleanup_failed = True
                        print(
                            f"    ❌ Failed to delete row {row['row_index']} from {row['sheet_name']}: {delete_resp.status_code}"
                        )
                except Exception as e:
                    cleanup_failed = True
                    print(
                        f"    ❌ Cleanup error for row {row['row_index']} in {row['sheet_name']}: {e}"
                    )

            if cleanup_failed:
                self.test_results["api"]["failed"] += 1
            else:
                self.test_results["api"]["passed"] += 1

    def _test_health_endpoint(self):
        """Test health check endpoint."""
        print("\n🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint connection error: {e}")
            print("💡 Make sure Flask server is running: python app.py")
            self.test_results["api"]["failed"] += 1

    def _test_check_auth_endpoint(self):
        """Test check-auth endpoint with authentication."""
        print("\n🔍 Testing check-auth endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/check-auth",
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "API authentication successful" in data.get(
                    "message", ""
                ):
                    print("✅ Check-auth endpoint working")
                    self.test_results["api"]["passed"] += 1
                else:
                    print("❌ Unexpected response structure for check-auth endpoint")
                    print(f"   Response: {data}")
                    self.test_results["api"]["failed"] += 1
            else:
                print(f"❌ Check-auth endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Check-auth endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_sms_logging_endpoint(self):
        """Test SMS logging endpoint."""
        print("\n🔍 Testing SMS logging endpoint...")
        test_payload = {
            "text": "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
            "date": "2025-08-14T10:30:00",
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/log-sms",
                json=test_payload,
                headers=self.auth_headers,
                timeout=10,
            )
            if response.status_code == 201:
                print("✅ SMS logging endpoint working")
                result = response.json()
                print(f"📊 Response: {result['success']}")
                self.test_results["api"]["passed"] += 1
            elif response.status_code == 200:
                print("✅ SMS logging endpoint working (invalid transaction)")
                result = response.json()
                print(f"📊 Response: {result['success']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ SMS logging endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results["api"]["failed"] += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ SMS logging endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_add_transaction_endpoint(self):
        """Test add transaction endpoint (direct API add)."""
        print("\n🔍 Testing add transaction endpoint...")
        unique_amount = f"{time.time():.2f}"  # Use timestamp as unique amount
        payload = {
            "date": "2025-09-05T14:30:00",
            "transaction_item": {
                "Amount": unique_amount,
                "Type": "Test",
                "Notes": "Direct add test",
            },
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json=payload,
                timeout=10,
            )
            if response.status_code == 201:
                data = response.json()
                if data.get("success"):
                    print("✅ Add transaction endpoint working")
                    print(
                        f"   Added amount: {payload['transaction_item']['Amount']}")
                    self.test_results["api"]["passed"] += 1
                else:
                    print("❌ Add transaction endpoint returned unsuccessful response")
                    self.test_results["api"]["failed"] += 1
            else:
                print(
                    f"❌ Add transaction endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["api"]["failed"] += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Add transaction endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

        test_payload = {
            "text": "INR 2000 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 2343.23.",
            "date": "2025-08-14T10:30:00",
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/log-sms",
                json=test_payload,
                headers=self.auth_headers,
                timeout=10,
            )

            if (
                response.status_code == 201
            ):  # Updated to expect 201 for successful creation
                print("✅ SMS logging endpoint working")
                result = response.json()
                print(f"📊 Response: {result['success']}")
                self.test_results["api"]["passed"] += 1
            elif (
                response.status_code == 200
            ):  # Also accept 200 for invalid transactions
                print("✅ SMS logging endpoint working (invalid transaction)")
                result = response.json()
                print(f"📊 Response: {result['success']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ SMS logging endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ SMS logging endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_parser_endpoint(self):
        """Test parser test endpoint."""
        print("\n🔍 Testing parser test endpoint...")

        test_payload = {
            "text": "INR 1500 debited from A/c no. XX1234 on 10-03-23 at AMAZON. Avl Bal: INR 5000"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json=test_payload,
                headers=self.auth_headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ Parser test endpoint working")
                result = response.json()
                print(
                    f"📊 Valid transaction: {result['data']['is_valid_transaction']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Parser test endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Parser test endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_sheet_info_endpoint(self):
        """Test sheet info endpoint."""
        print("\n🔍 Testing sheet info endpoint...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/sheets?month_year=July-2025",
                headers=self.auth_headers,
                timeout=5,
            )

            if response.status_code == 200:
                print("✅ Sheet info endpoint working")
                result = response.json()
                print(f"📊 Sheet exists: {result['data']['exists']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"❌ Sheet info endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Sheet info endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_stats_endpoints(self):
        """Test stats endpoints."""
        print("\n🔍 Testing stats endpoints...")

        # Test specific month stats only (current month stats endpoint removed)
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats?month_year=July-2025",
                headers=self.auth_headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ Specific month stats endpoint working")
                result = response.json()
                if result["success"]:
                    print(
                        f"� July 2025 total spend: ₹{result['data']['total_spend']:.2f}"
                    )
                self.test_results["api"]["passed"] += 1
            elif response.status_code == 404:
                print("✅ Specific month stats endpoint working (sheet not found)")
                result = response.json()
                if "Sheet not found" in result.get("error", ""):
                    print("📊 Expected 404 for non-existent sheet")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"❌ Specific month stats endpoint failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Specific month stats endpoint connection error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_transaction_management(self):
        """Test transaction management endpoints (PATCH/DELETE)."""
        print("\n🔍 Testing transaction management endpoints...")

        # Test date and sheet name
        test_date = "2025-09-25"
        sheet_name = "September-2025"
        test_row = None

        try:
            # Step 1: Insert test transaction using log endpoint
            print("\n  ↳ 1. Inserting test transaction...")
            unique_amount = "50.99"  # Use unique amount for easier identification
            sms_text = f"HDFC Bank: Rs.{unique_amount} debited from A/c **999 on 25-Sep-25 at API Test Store. Avl Bal: Rs.1000.00"
            log_data = {"text": sms_text, "date": f"{test_date}T10:30:00.000Z"}

            response = requests.post(
                f"{self.base_url}/api/v1/log-sms",
                headers=self.auth_headers,
                json=log_data,
                timeout=15,
            )

            if response.status_code in [200, 201]:
                print("    ✅ Test transaction logged successfully")
            else:
                print(
                    f"    ❌ Failed to log test transaction: {response.status_code}")
                self.test_results["api"]["failed"] += 1
                return

            import time

            time.sleep(2)  # Rate limiting delay

            # Step 2: Get transactions to find our test transaction
            print("  ↳ 2. Getting transactions to find test transaction...")
            response = requests.get(
                f"{self.base_url}/api/v1/transactions?date={test_date}",
                headers={"X-API-KEY": self.api_key},
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                transactions = data["data"]["transactions"]

                # Find our test transaction by unique amount and date
                test_transactions = [
                    t
                    for t in transactions
                    if (t.get("Amount") == unique_amount and t.get("Date") == test_date)
                ]
                if test_transactions:
                    test_row = test_transactions[0]["row_index"]
                    print(f"    ✅ Found test transaction at row {test_row}")
                    print(
                        f"       Amount: {test_transactions[0].get('Amount')}")
                    print(
                        f"       Description: {test_transactions[0].get('Description', 'N/A')}"
                    )
                else:
                    print("    ❌ Could not find test transaction")
                    print(
                        f"       Looking for: Amount={unique_amount}, Date={test_date}"
                    )
                    if transactions:
                        print(
                            f"       Available transactions: {len(transactions)}")
                        # Show last few transactions for debugging
                        for i, t in enumerate(transactions[-3:], 1):
                            print(
                                f"         {i}. Amount={t.get('Amount')}, Date={t.get('Date')}, Row={t.get('row_index')}"
                            )
                    self.test_results["api"]["failed"] += 1
                    return
            else:
                print(
                    f"    ❌ Failed to get transactions: {response.status_code}")
                self.test_results["api"]["failed"] += 1
                return

            time.sleep(2)  # Rate limiting delay

            # Step 3: Update transaction using PATCH endpoint
            print("  ↳ 3. Testing PATCH endpoint...")
            update_data = {
                "sheet_name": sheet_name,
                "row_index": test_row,
                "updates": {
                    "Type": "API Test",
                    "Notes": "Updated via API integration test",
                    "Friend Split": "10.00",
                },
            }

            response = requests.patch(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json=update_data,
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ PATCH endpoint working")
                print(f"       Response: {data['message']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"    ❌ PATCH endpoint failed: {response.status_code}")
                print(f"       Response: {response.text}")
                self.test_results["api"]["failed"] += 1
                return

            time.sleep(2)  # Rate limiting delay

            # Step 4: Verify update
            print("  ↳ 4. Verifying update...")
            response = requests.get(
                f"{self.base_url}/api/v1/transactions?date={test_date}",
                headers={"X-API-KEY": self.api_key},
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                transactions = data["data"]["transactions"]

                # Find the updated transaction
                updated_transaction = None
                for t in transactions:
                    if t["row_index"] == test_row:
                        updated_transaction = t
                        break

                if (
                    updated_transaction
                    and updated_transaction.get("Type") == "API Test"
                    and "Updated via API integration test"
                    in updated_transaction.get("Notes", "")
                ):
                    print("    ✅ Update verified successfully")
                    self.test_results["api"]["passed"] += 1
                else:
                    print("    ❌ Update verification failed")
                    self.test_results["api"]["failed"] += 1
            else:
                print(f"    ❌ Failed to verify update: {response.status_code}")
                self.test_results["api"]["failed"] += 1

            time.sleep(2)  # Rate limiting delay

            # Step 5: Test DELETE endpoint
            print("  ↳ 5. Testing DELETE endpoint...")
            delete_data = {"sheet_name": sheet_name, "row_index": test_row}

            response = requests.delete(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json=delete_data,
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                print("    ✅ DELETE endpoint working")
                print(
                    f"       Deleted row: {data['data']['deleted_row_index']}")
                self.test_results["api"]["passed"] += 1
            else:
                print(f"    ❌ DELETE endpoint failed: {response.status_code}")
                self.test_results["api"]["failed"] += 1

            print("✅ Transaction management endpoints tested successfully")

        except requests.exceptions.ConnectionError:
            print("    ❌ Connection error: Is the Flask server running?")
            self.test_results["api"]["failed"] += 1
        except requests.exceptions.Timeout:
            print("    ❌ Request timeout")
            self.test_results["api"]["failed"] += 1
        except Exception as e:
            print(f"    ❌ Transaction management test error: {e}")
            self.test_results["api"]["failed"] += 1

    def _test_endpoint_validation(self):
        """Test endpoint validation for PATCH and DELETE operations."""
        print("\n🔍 Testing endpoint validation...")

        try:
            # Test PATCH endpoint validation
            print("  ↳ Testing PATCH validation...")

            # Test missing sheet_name
            response = requests.patch(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json={"row_index": 2, "updates": {"Type": "Test"}},
                timeout=10,
            )
            if response.status_code == 400 and "sheet_name" in response.json().get(
                "error", ""
            ):
                print("    ✅ Missing sheet_name validation working")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"    ❌ Missing sheet_name validation failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

            # Test missing row_index
            response = requests.patch(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json={"sheet_name": "September-2025",
                      "updates": {"Type": "Test"}},
                timeout=10,
            )
            if response.status_code == 400 and "row_index" in response.json().get(
                "error", ""
            ):
                print("    ✅ Missing row_index validation working")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"    ❌ Missing row_index validation failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

            # Test missing updates
            response = requests.patch(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json={"sheet_name": "September-2025", "row_index": 2},
                timeout=10,
            )
            if response.status_code == 400 and "updates" in response.json().get(
                "error", ""
            ):
                print("    ✅ Missing updates validation working")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"    ❌ Missing updates validation failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

            # Test DELETE endpoint validation
            print("  ↳ Testing DELETE validation...")

            # Test missing sheet_name
            response = requests.delete(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json={"row_index": 2},
                timeout=10,
            )
            if response.status_code == 400 and "sheet_name" in response.json().get(
                "error", ""
            ):
                print("    ✅ DELETE missing sheet_name validation working")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"    ❌ DELETE missing sheet_name validation failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

            # Test missing row_index
            response = requests.delete(
                f"{self.base_url}/api/v1/transactions",
                headers=self.auth_headers,
                json={"sheet_name": "September-2025"},
                timeout=10,
            )
            if response.status_code == 400 and "row_index" in response.json().get(
                "error", ""
            ):
                print("    ✅ DELETE missing row_index validation working")
                self.test_results["api"]["passed"] += 1
            else:
                print(
                    f"    ❌ DELETE missing row_index validation failed: {response.status_code}"
                )
                self.test_results["api"]["failed"] += 1

            print("✅ Endpoint validation tests completed")

        except requests.exceptions.ConnectionError:
            print("    ❌ Connection error during validation tests")
            self.test_results["api"]["failed"] += 1
        except Exception as e:
            print(f"    ❌ Validation test error: {e}")
            self.test_results["api"]["failed"] += 1

    def test_performance_and_caching(self):
        """Test performance and caching behavior."""
        print("⚡ TESTING PERFORMANCE AND CACHING")
        print("=" * 60)

        if not self.sheet_manager:
            print("❌ Sheet manager not initialized, skipping performance tests")
            return

        # Test multiple API calls to same endpoint
        print("\n🔍 Testing API endpoint caching...")

        endpoint = f"{self.base_url}/api/v1/stats?month_year=July-2025"
        times = []

        for i in range(3):
            try:
                start_time = time.time()
                response = requests.get(
                    endpoint, headers=self.auth_headers, timeout=10)
                end_time = time.time()

                # Both are valid responses
                if response.status_code in [200, 404]:
                    times.append(end_time - start_time)
                    print(
                        f"   Call {i+1}: {end_time - start_time:.3f} seconds")
                else:
                    print(f"   Call {i+1}: Failed ({response.status_code})")

            except requests.exceptions.RequestException as e:
                print(f"   Call {i+1}: Connection error")

        if len(times) >= 2:
            print(f"\n📈 Performance analysis:")
            print(f"   First call: {times[0]:.3f} seconds")
            print(
                f"   Subsequent calls: {sum(times[1:])/len(times[1:]):.3f} seconds average"
            )

            if times[1] < times[0]:
                print("✅ Caching appears to be working")
                self.test_results["cache"]["passed"] += 1
            else:
                print("⚠️  Caching might not be working as expected")
                self.test_results["cache"]["failed"] += 1

    def test_csv_data(self):
        """Test with actual CSV data if available."""
        print("📄 TESTING WITH CSV DATA")
        print("=" * 60)

        csv_file = "sms-20250713002830.csv"

        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return

        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                messages = [(row[1], row[-1]) for row in reader]

            print(f"📊 Found {len(messages)} messages in CSV")

            # Test first 5 messages
            for i, (date, sms) in enumerate(messages[:5], 1):
                print(f"\n🔍 CSV Test {i}:")
                print(f"Date: {date}")
                print(f"SMS: {sms}")

                try:
                    transaction_info = get_transaction_info(sms)
                    if transaction_info:
                        transaction_data = transaction_info.to_dict()
                        print("✅ Parsed successfully")
                        print(
                            f"   Amount: {transaction_data.get('transaction', {}).get('amount', 'N/A')}"
                        )
                        print(
                            f"   Account: {transaction_data.get('account', {}).get('number', 'N/A')}"
                        )
                        self.test_results["parser"]["passed"] += 1
                    else:
                        print("❌ Failed to parse")
                        self.test_results["parser"]["failed"] += 1

                except Exception as e:
                    print(f"❌ Error: {e}")
                    self.test_results["parser"]["failed"] += 1

                print("-" * 30)

        except Exception as e:
            print(f"❌ Error reading CSV: {e}")

    def test_error_scenarios(self):
        """Test various error scenarios."""
        print("❌ TESTING ERROR SCENARIOS")
        print("=" * 50)

        # Test 1: Missing required fields
        print("🔍 Testing missing required fields...")

        # Parse SMS without text field
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 400:
                result = response.json()
                if "'text' field is required" in result.get("error", ""):
                    print("✅ Missing text field correctly handled")
                    self.test_results["extended"]["passed"] += 1
                else:
                    print(f"❌ Wrong error message: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Missing text field test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Log SMS without text field
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/log-sms",
                json={"date": "2025-07-19T10:30:00"},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 400:
                result = response.json()
                if "'text' field is required" in result.get("error", ""):
                    print("✅ Missing text field in log correctly handled")
                    self.test_results["extended"]["passed"] += 1
                else:
                    print(f"❌ Wrong error message: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Missing text in log test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 2: Invalid date format
        print("\n🔍 Testing invalid date format...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/log-sms",
                json={
                    "text": "This is a longer test SMS message to meet minimum length requirements",
                    "date": "invalid-date",
                },
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 400:
                result = response.json()
                if "Invalid date format" in result.get("error", ""):
                    print("✅ Invalid date format correctly handled")
                    self.test_results["extended"]["passed"] += 1
                else:
                    print(f"❌ Wrong error message: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Invalid date format test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 3: Invalid month-year format in stats
        print("\n🔍 Testing invalid month-year format...")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats?month_year=invalid-format",
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 400:
                result = response.json()
                if "Invalid month-year format" in result.get("error", ""):
                    print("✅ Invalid month-year format correctly handled")
                    self.test_results["extended"]["passed"] += 1
                else:
                    print(f"❌ Wrong error message: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Invalid month-year test error: {e}")
            self.test_results["extended"]["failed"] += 1

    def test_edge_cases(self):
        """Test edge cases."""
        print("🔄 TESTING EDGE CASES")
        print("=" * 50)

        # Test 1: Very short SMS
        print("🔍 Testing very short SMS...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={"text": "Hi"},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ Short SMS handled: Valid transaction = {result['data']['is_valid_transaction']}"
                )
                self.test_results["extended"]["passed"] += 1
            else:
                print(f"❌ Short SMS failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Short SMS test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 2: Very long SMS
        print("\n🔍 Testing very long SMS...")
        try:
            long_text = "A" * 1000  # 1000 character SMS
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={"text": long_text},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ Long SMS handled: Valid transaction = {result['data']['is_valid_transaction']}"
                )
                self.test_results["extended"]["passed"] += 1
            else:
                print(f"❌ Long SMS failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Long SMS test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 3: Non-English characters
        print("\n🔍 Testing non-English characters...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={"text": "आपका खाता ₹1000 से डेबिट किया गया"},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ Non-English SMS handled: Valid transaction = {result['data']['is_valid_transaction']}"
                )
                self.test_results["extended"]["passed"] += 1
            else:
                print(f"❌ Non-English SMS failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Non-English SMS test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 4: Special characters and symbols
        print("\n🔍 Testing special characters...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={"text": "Transaction: $100.50 @merchant #ref123 &payment!"},
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ Special characters handled: Valid transaction = {result['data']['is_valid_transaction']}"
                )
                self.test_results["extended"]["passed"] += 1
            else:
                print(f"❌ Special characters failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Special characters test error: {e}")
            self.test_results["extended"]["failed"] += 1

    def test_response_formats(self):
        """Test response formats."""
        print("📋 TESTING RESPONSE FORMATS")
        print("=" * 50)

        # Test 1: Health endpoint response format
        print("🔍 Testing health endpoint response format...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                # Check if response has the expected structure
                if "data" in result:
                    data = result["data"]
                    required_fields = ["status", "timestamp", "version"]
                    if all(field in data for field in required_fields):
                        print("✅ Health endpoint has correct format")
                        print(f"   Status: {data['status']}")
                        print(f"   Version: {data['version']}")
                        self.test_results["extended"]["passed"] += 1
                    else:
                        print(
                            f"❌ Missing fields in health response data: {data}")
                        print(f"   Expected fields: {required_fields}")
                        print(f"   Actual fields: {list(data.keys())}")
                        self.test_results["extended"]["failed"] += 1
                else:
                    print(f"❌ Health response missing 'data' field: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Health endpoint format test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 2: Parse SMS success response format
        print("\n🔍 Testing parse SMS response format...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/parse-sms",
                json={
                    "text": "INR 1500 debited from A/c no. XX1234 on 10-03-23 at AMAZON. Avl Bal: INR 5000"
                },
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code == 200:
                result = response.json()
                required_fields = ["success", "data"]
                data_fields = ["parsed_data",
                               "is_valid_transaction", "original_text"]

                if all(field in result for field in required_fields) and all(
                    field in result["data"] for field in data_fields
                ):
                    print("✅ Parse SMS response has correct format")
                    print(f"   Success: {result['success']}")
                    print(
                        f"   Valid transaction: {result['data']['is_valid_transaction']}"
                    )
                    self.test_results["extended"]["passed"] += 1
                else:
                    print(f"❌ Incorrect parse SMS response format: {result}")
                    self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Parse SMS failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Parse SMS format test error: {e}")
            self.test_results["extended"]["failed"] += 1

        # Test 3: Stats endpoint response format
        print("\n🔍 Testing stats endpoint response format...")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/stats?month_year=July-2025",
                headers=self.auth_headers,
                timeout=5,
            )
            if response.status_code in [200, 404]:
                result = response.json()
                required_fields = ["success"]

                if response.status_code == 200:
                    data_fields = [
                        "month_year",
                        "total_spend",
                        "transaction_count",
                        "categories",
                        "generated_at",
                    ]
                    if (
                        result.get("success")
                        and "data" in result
                        and all(field in result["data"] for field in data_fields)
                    ):
                        print("✅ Stats success response has correct format")
                        print(f"   Month: {result['data']['month_year']}")
                        print(
                            f"   Total spend: ₹{result['data']['total_spend']:.2f}")
                        print(
                            f"   Transaction count: {result['data']['transaction_count']}"
                        )
                        self.test_results["extended"]["passed"] += 1
                    else:
                        print(
                            f"❌ Incorrect stats success response format: {result}")
                        self.test_results["extended"]["failed"] += 1
                else:  # 404
                    if not result.get("success") and "error" in result:
                        print("✅ Stats error response has correct format")
                        print(f"   Error: {result['error']}")
                        self.test_results["extended"]["passed"] += 1
                    else:
                        print(
                            f"❌ Incorrect stats error response format: {result}")
                        self.test_results["extended"]["failed"] += 1
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")
                self.test_results["extended"]["failed"] += 1
        except Exception as e:
            print(f"❌ Stats format test error: {e}")
            self.test_results["extended"]["failed"] += 1

    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)

        total_passed = sum(result["passed"]
                           for result in self.test_results.values())
        total_failed = sum(result["failed"]
                           for result in self.test_results.values())
        total_tests = total_passed + total_failed

        print(f"📈 Overall Results:")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   📊 Total: {total_tests}")

        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"   🎯 Success Rate: {success_rate:.1f}%")

        print(f"\n📋 Category Breakdown:")
        for category, results in self.test_results.items():
            total = results["passed"] + results["failed"]
            if total > 0:
                rate = (results["passed"] / total) * 100
                print(
                    f"   {category.title()}: {results['passed']}/{total} ({rate:.1f}%)"
                )

        print("\n" + "=" * 80)
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total_failed} TESTS FAILED - CHECK LOGS ABOVE")
        print("=" * 80)


def main():
    """Run the test suite with command-line options."""
    parser = argparse.ArgumentParser(
        description="Finance SMS Logger API Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --api-only         # Run only API endpoint tests  
  python run_tests.py --local            # Run tests against local server
  python run_tests.py --extended         # Run extended tests with edge cases
  python run_tests.py --quick            # Run quick tests (no network)
  python run_tests.py --local --api-only # Run API tests against local server
        """,
    )

    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run only API endpoint tests (skip SMS parser and Google Sheets tests)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run tests against local server (http://127.0.0.1:5000)",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Run extended tests with error scenarios and edge cases",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests without network dependencies",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://finance-backend-api.onrender.com",
        help="Base URL for API tests (default: production server)",
    )

    args = parser.parse_args()

    # Determine base URL
    if args.local:
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = args.url

    # Create test suite
    test_suite = ComprehensiveTestSuite(base_url=base_url)

    # Run appropriate tests based on arguments
    if args.quick:
        test_suite.run_quick_tests()
    elif args.extended:
        test_suite.run_extended_tests()
    elif args.api_only:
        test_suite.run_api_only_tests()
    else:
        # Run CSV test first for comprehensive tests
        test_suite.test_csv_data()
        print()
        test_suite.run_all_tests()


if __name__ == "__main__":
    main()
