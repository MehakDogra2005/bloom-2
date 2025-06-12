#!/usr/bin/env python3
"""
Doctor Image Generator using Google Vertex AI Imagen
Generates professional portrait images for all specialists in doctors.json
"""

import json
import os
import base64
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests
from google.auth import default
from google.auth.transport.requests import Request
import google.auth

class DoctorImageGenerator:
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the image generator with Google Cloud credentials."""
        self.project_id = project_id
        self.location = location
        self.endpoint = f"https://{location}-aiplatform.googleapis.com"
        
        # Set up authentication
        self.credentials, _ = default()
        if hasattr(self.credentials, 'refresh'):
            self.credentials.refresh(Request())
        
        # Paths
        self.base_path = Path(__file__).parent
        self.static_path = self.base_path / "static"
        self.images_path = self.static_path / "Images"
        self.doctors_json_path = self.static_path / "data" / "doctors.json"
        
        # Create images directory if it doesn't exist
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Initialized Doctor Image Generator")
        print(f"Project ID: {project_id}")
        print(f"Location: {location}")
        print(f"Images will be saved to: {self.images_path}")

    def generate_prompt_for_doctor(self, doctor: Dict) -> str:
        """Generate a detailed prompt for creating a professional doctor image."""
        name = doctor.get('name', 'Doctor')
        specialty = doctor.get('specialty', 'Healthcare Professional')
        gender = doctor.get('gender', 'person')
        
        # Base professional prompt
        base_prompt = f"Professional headshot portrait of a {gender} {specialty.lower()}"
        
        # Add specialty-specific details
        specialty_details = {
            'Gynecologist': 'medical doctor, warm and reassuring expression, white coat, stethoscope',
            'Nutritionist': 'nutrition expert, friendly smile, professional attire, clean background',
            'Ayurvedic Expert': 'traditional medicine practitioner, serene expression, traditional Indian attire or white coat',
            'Therapist': 'mental health professional, compassionate expression, professional office setting',
            'Fitness Coach': 'fitness trainer, energetic and motivating expression, athletic wear or professional fitness attire'
        }
        
        detail = specialty_details.get(specialty, 'healthcare professional, confident expression, professional attire')
        
        # Add cultural context for Indian names
        indian_indicators = ['Dr.', 'Priya', 'Sharma', 'Ananya', 'Reddy', 'Ravi', 'Patel', 'Neha', 'Gupta', 
                           'Sneha', 'Joshi', 'Meera', 'Krishnan', 'Leela', 'Menon', 'Kumar', 'Singh', 'Bhatia']
        
        is_likely_indian = any(indicator in name for indicator in indian_indicators)
        ethnicity = "South Asian Indian" if is_likely_indian else "professional"
        
        full_prompt = f"{base_prompt}, {ethnicity} appearance, {detail}, professional lighting, high quality portrait, medical setting background, confident and trustworthy demeanor, shot with professional camera, 8K resolution, realistic, photorealistic"
        
        return full_prompt

    def generate_image(self, prompt: str, filename: str) -> Optional[str]:
        """Generate an image using Vertex AI Imagen API."""
        try:
            # Imagen API endpoint
            url = f"{self.endpoint}/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagegeneration@005:predict"
            
            headers = {
                "Authorization": f"Bearer {self.credentials.token}",
                "Content-Type": "application/json"
            }
            
            # Request payload for Imagen
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "1:1",  # Square format for profile images
                    "safetyFilterLevel": "block_some",
                    "personGeneration": "allow_adult"
                }
            }
            
            print(f"Generating image: {filename}")
            print(f"Prompt: {prompt}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'predictions' in result and len(result['predictions']) > 0:
                    # Get the base64 encoded image
                    image_data = result['predictions'][0]['bytesBase64Encoded']
                    
                    # Decode and save the image
                    image_bytes = base64.b64decode(image_data)
                    image_path = self.images_path / filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    print(f"✅ Successfully generated: {filename}")
                    return f"Images/{filename}"
                else:
                    print(f"❌ No image data in response for {filename}")
                    return None
            else:
                print(f"❌ Error generating {filename}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception generating {filename}: {str(e)}")
            return None

    def load_doctors_data(self) -> List[Dict]:
        """Load doctors data from JSON file."""
        try:
            with open(self.doctors_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('doctors', [])
        except Exception as e:
            print(f"❌ Error loading doctors data: {str(e)}")
            return []

    def save_doctors_data(self, doctors: List[Dict]):
        """Save updated doctors data back to JSON file."""
        try:
            data = {'doctors': doctors}
            with open(self.doctors_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("✅ Updated doctors.json with new image paths")
        except Exception as e:
            print(f"❌ Error saving doctors data: {str(e)}")

    def generate_filename(self, doctor: Dict) -> str:
        """Generate a filename for the doctor's image."""
        name = doctor.get('name', 'doctor').lower()
        # Remove special characters and spaces
        clean_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
        return f"ai_generated_{clean_name}.jpg"

    def generate_all_images(self, batch_size: int = 5, delay: float = 2.0):
        """Generate images for all doctors in the JSON file."""
        doctors = self.load_doctors_data()
        
        if not doctors:
            print("❌ No doctors data found!")
            return
        
        print(f"🚀 Starting image generation for {len(doctors)} doctors...")
        
        updated_doctors = []
        generated_count = 0
        
        for i, doctor in enumerate(doctors):
            try:
                print(f"\n--- Processing {i+1}/{len(doctors)}: {doctor.get('name')} ---")
                
                # Generate filename
                filename = self.generate_filename(doctor)
                
                # Check if image already exists
                existing_path = self.images_path / filename
                if existing_path.exists():
                    print(f"⏭️  Image already exists: {filename}")
                    doctor['image'] = f"Images/{filename}"
                    updated_doctors.append(doctor)
                    continue
                
                # Generate prompt
                prompt = self.generate_prompt_for_doctor(doctor)
                
                # Generate image
                image_path = self.generate_image(prompt, filename)
                
                if image_path:
                    # Update doctor data with new image path
                    doctor['image'] = image_path
                    generated_count += 1
                    print(f"✅ Generated image {generated_count}: {filename}")
                else:
                    print(f"⚠️  Failed to generate image for {doctor.get('name')}, keeping original")
                
                updated_doctors.append(doctor)
                
                # Rate limiting
                if (i + 1) % batch_size == 0 and i + 1 < len(doctors):
                    print(f"⏸️  Rate limiting: sleeping for {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Error processing {doctor.get('name')}: {str(e)}")
                updated_doctors.append(doctor)
                continue
        
        # Save updated data
        self.save_doctors_data(updated_doctors)
        
        print(f"\n🎉 Image generation complete!")
        print(f"📊 Generated {generated_count} new images out of {len(doctors)} doctors")
        print(f"📁 Images saved to: {self.images_path}")

def main():
    """Main function to run the image generator."""
    import sys
    
    # Get project ID from environment or command line
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    if not project_id and len(sys.argv) > 1:
        project_id = sys.argv[1]
    
    if not project_id:
        print("❌ Error: Google Cloud Project ID is required!")
        print("Set the GOOGLE_CLOUD_PROJECT environment variable or pass it as an argument:")
        print("python generate_doctor_images.py YOUR_PROJECT_ID")
        sys.exit(1)
    
    # Initialize generator
    generator = DoctorImageGenerator(project_id)
    
    # Generate all images
    generator.generate_all_images()

if __name__ == "__main__":
    main()
