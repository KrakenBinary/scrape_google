"""
Base scraper interface for TryloByte.
This provides a common structure for all scrapers to implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class BaseScraper(ABC):
    """Abstract base class for all scrapers in TryloByte"""
    
    def __init__(self, output_dir: str = "../data"):
        """
        Initialize the base scraper.
        
        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def setup(self, **kwargs) -> bool:
        """
        Set up the scraper with necessary resources.
        
        Args:
            **kwargs: Configuration options
            
        Returns:
            True if setup was successful
        """
        pass
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Tuple[List[Dict[str, Any]], str]:
        """
        Run the scraper with provided arguments.
        
        Args:
            *args, **kwargs: Scraper-specific arguments
            
        Returns:
            Tuple containing a list of scraped items and output filename
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the scraper.
        """
        pass
    
    def __enter__(self):
        """Support for context manager entry"""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager exit"""
        self.cleanup()
