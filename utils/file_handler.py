"""
File handling utilities for Graph Anything Over Time application.
Handles file upload, validation, and parsing for multiple formats.
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import json
import config
import io
from pathlib import Path


class FileHandler:
    """Handles file upload and processing operations."""
    
    # Maximum file size in MB
    MAX_FILE_SIZE = config.MAX_FILE_SIZE
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = config.SUPPORTED_EXTENSIONS  # type: ignore
    # The original literal dict has been moved to config.py
    
    def __init__(self):
        """Initialize FileHandler."""
        self.uploaded_files: Dict[str, pd.DataFrame] = {}
        self.file_metadata: Dict[str, Dict] = {}
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file for size and format.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file selected"
        
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({self.MAX_FILE_SIZE}MB)"
        
        # Check file extension
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            supported = ", ".join(self.SUPPORTED_EXTENSIONS.keys())
            return False, f"Unsupported file format. Supported formats: {supported}"
        
        return True, ""
    
    def read_file(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Read and parse uploaded file into DataFrame.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (dataframe, error_message)
        """
        try:
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            if file_extension == '.csv':
                return self._read_csv(uploaded_file)
            elif file_extension in ['.xlsx', '.xls']:
                return self._read_excel(uploaded_file)
            elif file_extension == '.json':
                return self._read_json(uploaded_file)
            elif file_extension == '.tsv':
                return self._read_tsv(uploaded_file)
            else:
                return None, f"Unsupported file format: {file_extension}"
                
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
    
    def _read_csv(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Read CSV file with encoding detection."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    return df, ""
                except UnicodeDecodeError:
                    continue
            
            return None, "Could not read file with any supported encoding"
            
        except Exception as e:
            return None, f"Error reading CSV file: {str(e)}"
    
    def _read_excel(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Read Excel file."""
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            return df, ""
        except Exception as e:
            try:
                # Try with xlrd for older Excel files
                df = pd.read_excel(uploaded_file, engine='xlrd')
                return df, ""
            except Exception as e2:
                return None, f"Error reading Excel file: {str(e2)}"
    
    def _read_json(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Read JSON file."""
        try:
            uploaded_file.seek(0)
            json_data = json.load(uploaded_file)
            
            # Handle different JSON structures
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if 'data' in json_data:
                    df = pd.DataFrame(json_data['data'])
                else:
                    df = pd.DataFrame([json_data])
            else:
                df = pd.DataFrame(json_data)
            
            return df, ""
            
        except Exception as e:
            return None, f"Error reading JSON file: {str(e)}"
    
    def _read_tsv(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Read TSV file."""
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep='\t')
            return df, ""
        except Exception as e:
            return None, f"Error reading TSV file: {str(e)}"
    
    def add_dataset(self, name: str, dataframe: pd.DataFrame, file_info: Dict) -> None:
        """
        Add a dataset to the handler.
        
        Args:
            name: Dataset name
            dataframe: Pandas DataFrame
            file_info: File metadata dictionary
        """
        self.uploaded_files[name] = dataframe
        self.file_metadata[name] = file_info
    
    def remove_dataset(self, name: str) -> bool:
        """
        Remove a dataset from the handler.
        
        Args:
            name: Dataset name to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        if name in self.uploaded_files:
            del self.uploaded_files[name]
            del self.file_metadata[name]
            return True
        return False
    
    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """Get a dataset by name."""
        return self.uploaded_files.get(name)
    
    def get_dataset_names(self) -> List[str]:
        """Get list of all dataset names."""
        return list(self.uploaded_files.keys())
    
    def get_dataset_info(self, name: str) -> Dict:
        """Get metadata for a specific dataset."""
        return self.file_metadata.get(name, {})
    
    def get_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Get all datasets."""
        return self.uploaded_files.copy()
    
    def clear_all_datasets(self) -> None:
        """Clear all datasets."""
        self.uploaded_files.clear()
        self.file_metadata.clear()
    
    def get_dataset_preview(self, name: str, rows: int = 5) -> Optional[pd.DataFrame]:
        """
        Get a preview of the dataset.
        
        Args:
            name: Dataset name
            rows: Number of rows to preview
            
        Returns:
            Preview DataFrame or None if dataset not found
        """
        if name in self.uploaded_files:
            return self.uploaded_files[name].head(rows)
        return None
    
    def get_dataset_stats(self, name: str) -> Optional[Dict]:
        """
        Get basic statistics for a dataset.
        
        Args:
            name: Dataset name
            
        Returns:
            Dictionary with basic stats or None if dataset not found
        """
        if name not in self.uploaded_files:
            return None
        
        df = self.uploaded_files[name]
        
        stats = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
            'missing_values': df.isnull().sum().sum()
        }
        
        return stats
