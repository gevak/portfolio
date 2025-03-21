import os
import logging

from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection details
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = None

def get_db_client():
    """Returns the Supabase client or creates a new one if needed"""
    global supabase
    if not supabase:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase URL and key must be provided. Check your environment variables.")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def is_valid_page_id(page_id: str) -> bool:
    """Check if a page ID is valid."""
    return len(page_id) == len('YYYYMMDD') and page_id.isdigit()

def get_like_count(page_id="default"):
    """Get current like count from Supabase for a specific page"""
    if not is_valid_page_id(page_id):
        return 0
    try:
        # Query the likes table for the specific page
        client = get_db_client()
        response = (
            client
            .table('likes')
            .select('count')
            .eq('page_id', page_id)
            .single()
            .execute()
        )
        
        # If the page exists in the database, return its count
        if response.data:
            return response.data.get('count', 0)
        # If the page doesn't exist yet, return 0
        return 0
        
    except Exception as e:
        print(f"Error getting like count: {e}")
        return 0
    
def save_like_count(
        count: int, page_id: str = '', title: str = 'Missing title') -> bool:
    """Save like count to Supabase"""
    if not is_valid_page_id(page_id):
        print(f"Invalid page_id format: {page_id}. Ignoring save request.")
        return False
    try:
        client = get_db_client()
        
        # First check if the page already exists
        response = (
            client
            .table('likes')
            .select('id')
            .eq('page_id', page_id)
            .execute()
        )
        
        if response.data:
            # Update existing record
            client.table('likes').update({'count': count}).eq('page_id', page_id).execute()
        else:
            # Insert new record
            client.table('likes').insert({'page_id': page_id, 'count': count, 'title': title}).execute()
            
        return True
    except Exception as e:
        print(f"Error saving like count: {e}")
        return False
    
def get_archive_list():
    """Get the list of pages with like counts from Supabase"""
    try:
        client = get_db_client()
        response = (
            client
            .table('likes')
            .select('page_id', 'count', 'title')
            .order('page_id', desc=True)
            .range(0, 1000)  # Limit to 365 records
            .execute()
        )
        # Covert to expected format:
        # [{ page_id: "20241210", title: "Reflections on Winter", count: 42 },
        # { page_id: "20241205", title: "My Favorite Books of 2024", count: 78 }...]
        archive_list = [{"page_id": item.get('page_id'),
                    "count": item.get('count'),
                    "title": item.get('title')} for item in response.data]
        archive_page_ids = [item['page_id'] for item in archive_list]

        # Add entries missing from DB based on filesystem
        for archive_dir in os.listdir("static/archive"):
            if archive_dir not in archive_page_ids:
                archive_list.append({"page_id": archive_dir, "count": 0, "title": "Missing Title"})

        # Sort the archive by page_id
        archive_list.sort(key=lambda x: x['page_id'], reverse=True)
        logging.info(f"Got archive: {archive_list}")
        return archive_list

    except Exception as e:
        logging.error(f"Error getting archive list: {e}")
        return []