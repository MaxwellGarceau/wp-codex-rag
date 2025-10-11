#!/usr/bin/env python3
"""
Test script for logging configuration
"""
import os
import sys

# Set environment variables
os.environ['ENV'] = 'local'
os.environ['DEBUG'] = 'True'

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logging_config import setup_logging, get_logger

def test_logging():
    print("Setting up logging configuration...")
    setup_logging()
    
    logger = get_logger('test')
    
    print("\nTesting different log levels:")
    logger.info('INFO message - should be visible')
    logger.debug('DEBUG message - should be visible in debug mode')
    logger.warning('WARNING message - should be visible')
    logger.error('ERROR message - should be visible')
    
    print("\nTesting RAG service logger:")
    rag_logger = get_logger('app.rag.application.service.rag')
    rag_logger.info('RAG service logger test - INFO level')
    rag_logger.debug('RAG service logger test - DEBUG level')

if __name__ == "__main__":
    test_logging()
