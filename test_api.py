#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Simple test script to verify CESSDA API integration."""

import asyncio
import json
from src.mcp_cessda_datasets.tools import search_datasets, get_filters_info


async def test_search():
    """Test basic dataset search."""
    print("=" * 80)
    print("TEST 1: Basic search for 'climate change'")
    print("=" * 80)

    try:
        result = await search_datasets(
            query="climate change",
            limit=3
        )

        print(f"\n✓ Search successful!")
        print(f"  Total results available: {result.get('resultsCount', {}).get('total', 0)}")
        print(f"  Results returned: {len(result.get('results', []))}")

        if result.get('results'):
            print(f"\n  First result:")
            first = result['results'][0]
            print(f"    Title: {first.get('title', {}).get('en', 'N/A')}")
            print(f"    Publisher: {first.get('publisher', {}).get('abbr', 'N/A')}")

        return True

    except Exception as e:
        print(f"\n✗ Search failed: {e}")
        return False


async def test_filtered_search():
    """Test filtered search."""
    print("\n" + "=" * 80)
    print("TEST 2: Search political science datasets from Sweden")
    print("=" * 80)

    try:
        result = await search_datasets(
            classifications=["Political science"],
            study_area_countries=["Sweden"],
            limit=2
        )

        print(f"\n✓ Filtered search successful!")
        print(f"  Total results available: {result.get('resultsCount', {}).get('total', 0)}")
        print(f"  Results returned: {len(result.get('results', []))}")

        return True

    except Exception as e:
        print(f"\n✗ Filtered search failed: {e}")
        return False


def test_get_filters():
    """Test getting filter information."""
    print("\n" + "=" * 80)
    print("TEST 3: Get available classifications")
    print("=" * 80)

    try:
        result = get_filters_info("classifications")

        print(f"\n✓ Filter info retrieved!")
        print(f"  Filter type: {result['filter_type']}")
        print(f"  Available values: {result['count']}")
        print(f"  First 5 classifications:")
        for classification in result['values'][:5]:
            print(f"    - {classification}")

        return True

    except Exception as e:
        print(f"\n✗ Get filters failed: {e}")
        return False


def test_invalid_filter():
    """Test invalid filter type handling."""
    print("\n" + "=" * 80)
    print("TEST 4: Invalid filter type (should fail gracefully)")
    print("=" * 80)

    try:
        result = get_filters_info("invalid_type")
        print(f"\n✗ Should have raised ValueError!")
        return False

    except ValueError as e:
        print(f"\n✓ Correctly raised ValueError: {e}")
        return True

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CESSDA MCP Server API Tests" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")

    results = []

    # Run async tests
    results.append(await test_search())
    results.append(await test_filtered_search())

    # Run sync tests
    results.append(test_get_filters())
    results.append(test_invalid_filter())

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed! The MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Configure Claude Desktop (see claude_desktop_config.example.json)")
        print("2. Restart Claude Desktop")
        print("3. Test with prompts like 'Find datasets about climate change'")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
