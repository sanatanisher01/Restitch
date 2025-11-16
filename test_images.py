#!/usr/bin/env python3
"""
Test image URLs directly
"""

import requests

def test_images():
    images = [
        'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014112/img1_gfaqjk.jpg',
        'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014118/img2_g01qu2.jpg',
        'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014124/img3_bssdv3.jpg',
        'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014132/img4_rgsaky.jpg',
        'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014139/img5_mbbwdg.jpg'
    ]
    
    for i, url in enumerate(images, 1):
        try:
            response = requests.head(url, timeout=5)
            print(f"Image {i}: {response.status_code} - {url}")
        except Exception as e:
            print(f"Image {i}: ERROR - {e}")

if __name__ == '__main__':
    test_images()