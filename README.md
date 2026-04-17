# Contactless Attendance System

Facial recognition attendance using AWS Rekognition, SAM, and DynamoDB.

## Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.9+

## Deployment

1. **Deploy Infrastructure:**
   ```bash
   sam build
   sam deploy --guided
   ```
   *Note: Note down the `ApiUrl` from the outputs.*

2. **Setup Rekognition:**
   ```bash
   python scripts/setup_rekognition.py
   ```

3. **Configure Frontend:**
   - Open `frontend/app.js` and `frontend/admin.js`.
   - Replace `PASTE_YOUR_API_URL_HERE` with the `ApiUrl` from Step 1.

4. **Run Locally:**
   - You can open `frontend/index.html` directly in a browser or host it on S3/Vercel.

## Architecture
- **Webcam:** Captures image -> Uploads to S3 via Presigned URL.
- **Trigger:** S3 upload triggers `ProcessAttendanceFunction`.
- **Recognition:** Calls AWS Rekognition `SearchFacesByImage`.
- **Database:** Stores records in DynamoDB (Employee ID, Date, In/Out times, Status).
- **Scheduled Job:** Runs at 11:59 PM daily to mark unrecorded employees as `absent`.

## Security
- S3 Lifecycle rules delete capture images after 24 hours.
- IAM roles follow least privilege principles.
- DynamoDB data is encrypted at rest by default.
