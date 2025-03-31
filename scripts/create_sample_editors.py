#!/usr/bin/env python
"""
Script to create sample editors in the database for the masthead.
"""
import sys
import os

# Add the parent directory to the path so we can import the data modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data.people as ppl
import data.roles as rls

# Sample editors data
EDITORS = [
    {
        "name": "John Smith",
        "email": "john.smith@gmail.com",
        "affiliation": "NYU",
        "role": rls.ED_CODE,
        "bio": "Professor of Computer Science with expertise in distributed systems and cloud computing."
    },
    {
        "name": "Emily Johnson",
        "email": "emily.johnson@gmail.com",
        "affiliation": "NYU",
        "role": rls.ED_CODE,
        "bio": "Associate Professor specializing in artificial intelligence and machine learning algorithms."
    },
    {
        "name": "Michael Chen",
        "email": "michael.chen@gmail.com",
        "affiliation": "NYU",
        "role": rls.ED_CODE,
        "bio": "Assistant Professor focusing on cybersecurity and privacy-preserving computation."
    },
    {
        "name": "Sarah Williams",
        "email": "sarah.williams@gmail.com",
        "affiliation": "NYU",
        "role": rls.ED_CODE,
        "bio": "Professor with research interests in human-computer interaction and user experience design."
    },
    {
        "name": "David Rodriguez",
        "email": "david.rodriguez@gmail.com",
        "affiliation": "NYU",
        "role": rls.ED_CODE,
        "bio": "Distinguished Professor specializing in programming languages and compiler optimization."
    }
]

def create_editors():
    """Create sample editors in the database."""
    created_count = 0
    skipped_count = 0
    
    for editor in EDITORS:
        try:
            ppl.create(
                name=editor["name"],
                affiliation=editor["affiliation"],
                email=editor["email"],
                role=editor["role"],
                bio=editor["bio"]
            )
            print(f"Created editor: {editor['name']} ({editor['email']})")
            created_count += 1
        except ValueError as e:
            if "duplicate" in str(e):
                print(f"Skipped existing editor: {editor['email']}")
                skipped_count += 1
            else:
                print(f"Error creating editor {editor['email']}: {e}")
    
    print(f"\nSummary: Created {created_count} editors, skipped {skipped_count} existing editors.")

if __name__ == "__main__":
    create_editors() 