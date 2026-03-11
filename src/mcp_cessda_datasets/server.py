# SPDX-License-Identifier: Apache-2.0
"""MCP server for CESSDA research datasets using FastMCP with STDIO transport."""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from .tools import search_datasets, get_filters_info
from .logging_config import logger, log_with_context


# Initialize FastMCP server
mcp = FastMCP("CESSDA Datasets")


@mcp.tool()
async def search_cessda_datasets(
    query: Optional[str] = None,
    classifications: Optional[List[str]] = None,
    study_area_countries: Optional[List[str]] = None,
    publishers: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    language: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Dict[str, Any]:
    """Search CESSDA research datasets across European social science data archives.

    This tool searches the CESSDA Data Catalogue, which provides access to research
    datasets from 22 European social science data archives. You can search by free text,
    filter by topic classifications, countries, publishers, and date ranges.

    Args:
        query: Free-text search query across dataset titles, abstracts, and keywords.
               Example: "climate change", "unemployment", "voting behavior"
        classifications: Filter by topic classifications. Use get_cessda_filters with
                        filter_type="classifications" to see available options.
                        Example: ["Political science", "Sociology"]
        study_area_countries: Filter by countries where research was conducted.
                             Use get_cessda_filters with filter_type="countries" for options.
                             Example: ["Sweden", "Norway", "Denmark"]
        publishers: Filter by specific data archives/publishers.
                   Use get_cessda_filters with filter_type="publishers" for options.
                   Example: ["NSD - Norwegian Centre for Research Data"]
        keywords: Search for specific subject keywords within studies.
                 Example: ["health", "education"]
        year_min: Earliest data collection year (inclusive).
                 Example: 2010
        year_max: Latest data collection year (inclusive).
                 Example: 2020
        language: Metadata language (ISO 639-1 code). Defaults to "en" (English).
                 Use get_cessda_filters with filter_type="languages" for options.
                 Example: "de" (German), "sv" (Swedish)
        limit: Maximum number of results to return (1-200). Defaults to 10.
        offset: Pagination offset for retrieving additional results. Defaults to 0.

    Returns:
        Dictionary containing:
        - searchTerms: Echo of search parameters used
        - resultsCount: Pagination info (items retrieved vs total available)
        - results: Array of dataset objects with:
          - id: Unique dataset identifier
          - title: Dataset title
          - abstract: Description of the dataset
          - creators: Authors/researchers
          - publicationYear: Year published
          - dataCollectionPeriod: When data was collected
          - studyAreaCountries: Countries covered
          - classifications: Topic categories
          - keywords: Subject terms
          - publisher: Data archive name
          - dataAccessUrl: Link to dataset
          - pidStudies: Persistent identifiers

    Raises:
        Error if API request fails or parameters are invalid

    Examples:
        Search for climate datasets:
        {"query": "climate change", "limit": 5}

        Find political science datasets from Nordic countries 2010-2020:
        {
            "classifications": ["Political science"],
            "study_area_countries": ["Sweden", "Norway", "Denmark"],
            "year_min": 2010,
            "year_max": 2020
        }
    """
    try:
        log_with_context(
            logger,
            "INFO",
            "Processing search request",
            query=query,
            classifications=classifications,
            countries=study_area_countries,
        )

        result = await search_datasets(
            query=query,
            classifications=classifications,
            study_area_countries=study_area_countries,
            publishers=publishers,
            keywords=keywords,
            year_min=year_min,
            year_max=year_max,
            language=language,
            limit=limit,
            offset=offset,
        )

        return result

    except Exception as e:
        error_msg = f"Failed to search datasets: {str(e)}"
        log_with_context(
            logger,
            "ERROR",
            "Search request failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise Exception(error_msg)


@mcp.tool()
def get_cessda_filters(filter_type: str) -> Dict[str, Any]:
    """Get available filter values for CESSDA dataset searches.

    Use this tool to discover what filter values are available for the
    search_cessda_datasets tool. This helps you understand what topics,
    publishers, countries, and languages you can filter by.

    Args:
        filter_type: Type of filter to get information about. Must be one of:
            - "classifications": Topic/subject classifications (e.g., "Political Science")
            - "publishers": Data archive publishers (e.g., "UKDS - UK Data Service")
            - "countries": Study area countries (e.g., "Sweden", "Germany")
            - "languages": Available metadata languages (e.g., "en", "de", "sv")

    Returns:
        Dictionary containing:
        - filter_type: The requested filter type
        - values: List of valid values for this filter
        - count: Number of available values

    Raises:
        ValueError if filter_type is not recognized

    Examples:
        Get available topic classifications:
        {"filter_type": "classifications"}

        Get list of data publishers:
        {"filter_type": "publishers"}

        Get supported countries:
        {"filter_type": "countries"}

        Get available metadata languages:
        {"filter_type": "languages"}
    """
    try:
        log_with_context(
            logger,
            "INFO",
            "Processing filter info request",
            filter_type=filter_type,
        )

        result = get_filters_info(filter_type)
        return result

    except ValueError as e:
        error_msg = str(e)
        log_with_context(
            logger,
            "WARN",
            "Invalid filter type requested",
            filter_type=filter_type,
            error=error_msg,
        )
        raise ValueError(error_msg)

    except Exception as e:
        error_msg = f"Failed to get filter info: {str(e)}"
        log_with_context(
            logger,
            "ERROR",
            "Filter info request failed",
            filter_type=filter_type,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise Exception(error_msg)


def main():
    """Main entry point for MCP server using STDIO transport."""
    log_with_context(
        logger,
        "INFO",
        "Starting CESSDA MCP server",
        transport="stdio",
    )

    # Run server with STDIO transport (default for FastMCP)
    mcp.run()


if __name__ == "__main__":
    main()
