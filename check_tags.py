#!/usr/bin/env python3
from database import get_database

db = get_database()
tags = db.get_all_tags()
print(f'Total tags: {len(tags)}')
print('\nRecent tags:')
for t in tags[-10:]:
    tag_id = t.get('tag_id', 'N/A')
    status = t.get('status', 'N/A')
    rf_id = t.get('rf_id', 'N/A')
    name = t.get('name', 'N/A')
    description = t.get('description', 'N/A')
    
    print(f'ID: {tag_id[:20]}... | Status: {status} | RFID: {rf_id} | Name: {name}')
    if description and description != 'N/A':
        print(f'    Description: {description}')