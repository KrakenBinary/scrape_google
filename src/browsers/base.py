"""
Base browser interface for Selenium-based scraping in TryloByte.
This abstraction layer makes it easier to swap or rewrite browser implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List


class BaseBrowser(ABC):
    """Abstract base class for browser implementations"""
    
    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """Initialize the browser with given options"""
        pass
    
    @abstractmethod
    def navigate(self, url: str) -> bool:
        """Navigate to a URL"""
        pass
    
    @abstractmethod
    def find_element(self, selector: str, by_type: str = "css") -> Optional[Any]:
        """Find a single element"""
        pass
    
    @abstractmethod
    def find_elements(self, selector: str, by_type: str = "css") -> List[Any]:
        """Find multiple elements"""
        pass
    
    @abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10, by_type: str = "css") -> Optional[Any]:
        """Wait for an element to be available"""
        pass
    
    @abstractmethod
    def click(self, element_or_selector: Any) -> bool:
        """Click on an element"""
        pass
    
    @abstractmethod
    def send_keys(self, element_or_selector: Any, text: str) -> bool:
        """Type text into an element"""
        pass
    
    @abstractmethod
    def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """Scroll the page"""
        pass
    
    @abstractmethod
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        pass
    
    @abstractmethod
    def get_text(self, element_or_selector: Any) -> str:
        """Get text from an element"""
        pass
    
    @abstractmethod
    def get_attribute(self, element_or_selector: Any, attribute: str) -> str:
        """Get attribute from an element"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the browser"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
