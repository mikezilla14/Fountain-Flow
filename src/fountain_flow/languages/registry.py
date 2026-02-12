"""
Language registry system for fountain-flow.

This module provides a central registry for discovering and accessing language definitions.
Languages are auto-discovered from the languages/ directory and can be retrieved by name
or file extension.
"""

from typing import Dict, List, Optional, Type
import importlib
import inspect
from .base import LanguageDefinition


class LanguageRegistry:
    """
    Central registry for language definitions.
    
    Automatically discovers and registers language definitions from the languages/ package.
    Provides lookup by name or file extension.
    """
    
    def __init__(self):
        self._languages: Dict[str, LanguageDefinition] = {}
        self._extension_map: Dict[str, LanguageDefinition] = {}
        self._discover_languages()
    
    def _discover_languages(self):
        """Auto-discover language definitions from the languages/ directory."""
        # Get the directory containing this file
        languages_dir = os.path.dirname(__file__)
        
        # Find all Python files in the languages directory
        for filename in os.listdir(languages_dir):
            if not filename.endswith('.py'):
                continue
            if filename.startswith('_'):
                continue
            if filename == 'base.py':
                continue
            if filename == 'registry.py':
                continue
            
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'.{module_name}', package=__package__)
                
                # Find all LanguageDefinition subclasses in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, LanguageDefinition) and obj != LanguageDefinition:
                        # Instantiate the language definition
                        try:
                            lang_def = obj()
                            self.register(lang_def)
                        except Exception as e:
                            print(f"Warning: Failed to instantiate {name}: {e}")
            
            except Exception as e:
                print(f"Warning: Failed to load language module {module_name}: {e}")
    
    def register(self, language: LanguageDefinition):
        """
        Register a language definition.
        
        Args:
            language: The language definition to register
        """
        self._languages[language.name] = language
        
        # Register all file extensions
        for ext in language.file_extensions:
            self._extension_map[ext.lower()] = language
    
    def get_language(self, name: str) -> Optional[LanguageDefinition]:
        """
        Get a language definition by name.
        
        Args:
            name: The language name (e.g., 'fflow', 'twee', 'renpy')
            
        Returns:
            The language definition, or None if not found
        """
        return self._languages.get(name.lower())
    
    def get_language_by_extension(self, extension: str) -> Optional[LanguageDefinition]:
        """
        Get a language definition by file extension.
        
        Args:
            extension: The file extension (e.g., '.fflow', '.twee', '.rpy')
            
        Returns:
            The language definition, or None if not found
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        return self._extension_map.get(extension.lower())
    
    def list_languages(self) -> List[str]:
        """
        Get a list of all registered language names.
        
        Returns:
            List of language names
        """
        return list(self._languages.keys())
    
    def list_extensions(self) -> List[str]:
        """
        Get a list of all supported file extensions.
        
        Returns:
            List of file extensions
        """
        return list(self._extension_map.keys())


# Global registry instance
_registry = None


def get_registry() -> LanguageRegistry:
    """
    Get the global language registry instance.
    
    Returns:
        The global LanguageRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = LanguageRegistry()
    return _registry


# Convenience functions

def get_language(name: str) -> Optional[LanguageDefinition]:
    """Get a language definition by name."""
    return get_registry().get_language(name)


def get_language_by_extension(extension: str) -> Optional[LanguageDefinition]:
    """Get a language definition by file extension."""
    return get_registry().get_language_by_extension(extension)


def list_languages() -> List[str]:
    """Get a list of all registered language names."""
    return get_registry().list_languages()
