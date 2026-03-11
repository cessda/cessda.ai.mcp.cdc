# SPDX-License-Identifier: Apache-2.0
"""CESSDA API integration tools for searching research datasets."""

from typing import Any, Dict, List, Optional
import httpx
from .config import config
from .logging_config import logger, log_with_context


# Valid filter values based on CESSDA API documentation
VALID_FILTERS = {
    "classifications": [
        "Agricultural Science",
        "Accidents and injuries",
        "Business and finance",
        "Crime and justice",
        "Demography",
        "Economics",
        "Education",
        "Employment",
        "Environment",
        "Family",
        "Health",
        "Housing",
        "Information and communication",
        "International relations",
        "Labour",
        "Law",
        "Leisure and sport",
        "Mass media",
        "Migration",
        "Natural resources",
        "Political science",
        "Production",
        "Public health",
        "Religion",
        "Science and technology",
        "Social conditions and indicators",
        "Social policy",
        "Sociology",
        "Time use",
        "Transport",
        "Values and attitudes",
    ],
    "publishers": [
        "ADP - Slovenian Social Science Data Archives",
        "AUSSDA - The Austrian Social Science Data Archive",
        "CSDA - Czech Social Science Data Archive",
        "DCS - Data Centre for the Social Sciences",
        "DNA - Danish National Archives",
        "EKKE - National Centre for Social Research",
        "FSD - Finnish Social Science Data Archive",
        "GESIS - Leibniz Institute for the Social Sciences",
        "LiDA - Lithuanian Data Archive",
        "NSD - Norwegian Centre for Research Data",
        "SASD - Slovak Archive of Social Data",
        "SND - Swedish National Data Service",
        "SODHA - Slovenian Social Science Data Archive",
        "TARKI - Social Research Institute",
        "UKDS - UK Data Service",
        "UniData - University of Milan",
    ],
    "countries": [
        "Albania", "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
        "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia",
        "Lithuania", "Luxembourg", "Malta", "Netherlands", "Norway", "Poland",
        "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
        "Switzerland", "United Kingdom",
    ],
    "languages": [
        "en",  # English
        "de",  # German
        "fr",  # French
        "fi",  # Finnish
        "sv",  # Swedish
        "no",  # Norwegian
        "da",  # Danish
        "cs",  # Czech
        "sl",  # Slovenian
        "el",  # Greek
    ],
}


async def search_datasets(
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
    """Search CESSDA research datasets.

    Args:
        query: Free-text search across dataset titles, abstracts, keywords
        classifications: Topic classifications filter
        study_area_countries: Countries where research was conducted
        publishers: Specific data archives/publishers
        keywords: Subject keywords within studies
        year_min: Earliest data collection year
        year_max: Latest data collection year
        language: Metadata language (ISO 639-1 code, defaults to 'en')
        limit: Maximum results to return (1-200, defaults to 10)
        offset: Pagination offset (defaults to 0)

    Returns:
        Dictionary containing search results with metadata

    Raises:
        httpx.HTTPError: If API request fails
    """
    # Set defaults
    language = language or config.default_metadata_language
    limit = limit or config.default_search_limit

    # Validate limit
    if limit > config.max_search_limit:
        log_with_context(
            logger,
            "WARN",
            "Search limit exceeds maximum",
            requested_limit=limit,
            max_limit=config.max_search_limit,
        )
        limit = config.max_search_limit

    # Build query parameters
    params: Dict[str, Any] = {
        "metadataLanguage": language,
        "limit": limit,
        "offset": offset,
    }

    if query:
        params["q"] = query

    if classifications:
        params["classifications"] = classifications

    if study_area_countries:
        params["studyAreaCountries"] = study_area_countries

    if publishers:
        params["publishers"] = publishers

    if keywords:
        params["keywords"] = keywords

    if year_min is not None:
        params["dataCollectionYearMin"] = year_min

    if year_max is not None:
        params["dataCollectionYearMax"] = year_max

    # Make API request
    url = f"{config.api_base_url}/DataSets/v2/search"

    try:
        async with httpx.AsyncClient(timeout=config.api_timeout) as client:
            log_with_context(
                logger,
                "INFO",
                "Making API request to CESSDA",
                url=url,
                params=params,
            )

            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            log_with_context(
                logger,
                "INFO",
                "API request successful",
                results_count=len(data.get("results", [])),
                total_available=data.get("resultsCount", {}).get("total", 0),
            )

            return data

    except httpx.TimeoutException as e:
        log_with_context(
            logger,
            "ERROR",
            "API request timeout",
            url=url,
            timeout=config.api_timeout,
            error=str(e),
        )
        raise

    except httpx.HTTPStatusError as e:
        log_with_context(
            logger,
            "ERROR",
            "API request failed",
            url=url,
            status_code=e.response.status_code,
            error=str(e),
        )
        raise

    except Exception as e:
        log_with_context(
            logger,
            "ERROR",
            "Unexpected error during API request",
            url=url,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


def get_filters_info(filter_type: str) -> Dict[str, Any]:
    """Get available values for a specific filter type.

    Args:
        filter_type: Type of filter (classifications, publishers, countries, languages)

    Returns:
        Dictionary containing filter information

    Raises:
        ValueError: If filter_type is invalid
    """
    if filter_type not in VALID_FILTERS:
        valid_types = ", ".join(VALID_FILTERS.keys())
        log_with_context(
            logger,
            "WARN",
            "Invalid filter type requested",
            requested_type=filter_type,
            valid_types=valid_types,
        )
        raise ValueError(
            f"Invalid filter type '{filter_type}'. "
            f"Valid types are: {valid_types}"
        )

    values = VALID_FILTERS[filter_type]

    log_with_context(
        logger,
        "INFO",
        "Filter info retrieved",
        filter_type=filter_type,
        count=len(values),
    )

    return {
        "filter_type": filter_type,
        "values": values,
        "count": len(values),
    }
