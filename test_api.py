import requests
import json

def test_faq_bot_api():
    """Test FAQ Bot API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testing FAQ Bot API ===\n")
    
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("2. Testing Questions...")
    test_questions = [
        "apa itu stunting?",
        "bagaimana cara mencegah stunting?",
        "apa saja gejala stunting?",
        "asi eksklusif berapa lama?",
        "pertanyaan aneh yang tidak ada jawabannya"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n2.{i}. Question: {question}")
        try:
            response = requests.post(f"{base_url}/ask", 
            json={"question": question})
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Answer: {result['answer'][:100]}...")
            print(f"Confidence: {result.get('confidence', 0):.3f}")
            print(f"Category: {result.get('category', 'unknown')}")
            print(f"Status: {result.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("3. Testing Categories...")
    try:
        response = requests.get(f"{base_url}/categories")
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print("Categories:")
        for cat in result.get('categories', []):
            print(f"  - {cat['category']}: {cat['description']}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("4. Testing Stats...")
    try:
        response = requests.get(f"{base_url}/stats")
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Total FAQs: {result.get('total_faqs', 0)}")
        print(f"Total Questions: {result.get('total_questions', 0)}")
        print(f"Categories: {result.get('categories', 0)}")
        print(f"Status: {result.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("5. Testing Error Handling...")
    
    try:
        response = requests.post(f"{base_url}/ask", json={"question": ""})
        print(f"Empty question - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        response = requests.post(f"{base_url}/ask", json={})
        print(f"No question field - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Make sure Flask app is running on http://127.0.0.1:5000")
    print("Run: python app.py")
    print("\nPress Enter to continue with testing...")
    input()
    
    test_faq_bot_api()