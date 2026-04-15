import requests
import sys
import os


def test_api():
    url = "http://localhost:8000/detect"

    test_image = os.path.join(os.path.dirname(__file__), "test_image.jpg")

    if not os.path.exists(test_image):
        print(f"Test image not found: {test_image}")
        print("Please place a test image named 'test_image.jpg' in the backend folder")

        sample_url = (
            "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400"
        )
        print(f"Downloading sample road image...")

        try:
            response = requests.get(sample_url)
            if response.status_code == 200:
                with open(test_image, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded sample image to {test_image}")
            else:
                return
        except Exception as e:
            print(f"Could not download sample image: {e}")
            return

    if not os.path.exists(test_image):
        print("No test image available")
        return

    print(f"Testing API with {test_image}...")

    with open(test_image, "rb") as f:
        files = {"file": ("test_image.jpg", f, "image/jpeg")}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(f"Total potholes: {data['total_potholes']}")
        print(f"Total cost: ${data['total_cost']}")
        print(f"Severity distribution: {data['severity_distribution']}")
        print("\nDetections:")
        for det in data["detections"]:
            print(f"  - Bbox: {det['bbox']}")
            print(f"    Area: {det['area']} sq m")
            print(f"    Severity: {det['severity']}")
            print(f"    Workers: {det['workers']}")
            print(f"    Cost: ${det['cost']}")
            print(f"    Time: {det['time']} hours")
            print()
        print("Test PASSED!")
    else:
        print(f"Test FAILED! Status: {response.status_code}")
        print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            test_api()
        else:
            print("API not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Is the server running?")
        print("Run: python run.py")
        sys.exit(1)
