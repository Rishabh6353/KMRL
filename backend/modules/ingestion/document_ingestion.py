import os
import uuid
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient
import shutil

class DocumentIngestionService:
    def __init__(self, config):
        self.config = config
        self.upload_folder = config.get('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'})
        self.storage_type = config.get('STORAGE_TYPE', 'local')  # local, s3, gcs, azure
        
        # Initialize cloud storage clients
        self._init_cloud_storage()
    
    def _init_cloud_storage(self):
        """Initialize cloud storage clients based on configuration"""
        try:
            if self.storage_type == 's3':
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.config.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=self.config.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=self.config.get('AWS_REGION', 'us-east-1')
                )
            elif self.storage_type == 'gcs':
                self.gcs_client = gcs.Client(project=self.config.get('GOOGLE_CLOUD_PROJECT_ID'))
            elif self.storage_type == 'azure':
                self.azure_client = BlobServiceClient.from_connection_string(
                    self.config.get('AZURE_STORAGE_CONNECTION_STRING')
                )
        except Exception as e:
            print(f"Cloud storage initialization error: {e}")
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_unique_filename(self, original_filename):
        """Generate unique filename to prevent conflicts"""
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{unique_id}.{file_extension}"
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of file for integrity checking"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def upload_file(self, file, metadata=None):
        """
        Upload file to configured storage
        Returns: dict with file information
        """
        if not file or not self.allowed_file(file.filename):
            return {'error': 'Invalid file type or no file provided'}
        
        try:
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            unique_filename = self.generate_unique_filename(original_filename)
            
            # Get file info
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer
            file_type = file.content_type or 'application/octet-stream'
            
            # Upload based on storage type
            if self.storage_type == 'local':
                file_path = self._upload_local(file, unique_filename)
            elif self.storage_type == 's3':
                file_path = self._upload_s3(file, unique_filename)
            elif self.storage_type == 'gcs':
                file_path = self._upload_gcs(file, unique_filename)
            elif self.storage_type == 'azure':
                file_path = self._upload_azure(file, unique_filename)
            else:
                return {'error': 'Invalid storage type configured'}
            
            # Calculate file hash for local files
            file_hash = None
            if self.storage_type == 'local':
                file_hash = self.calculate_file_hash(file_path)
            
            return {
                'success': True,
                'filename': unique_filename,
                'original_filename': original_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file_type,
                'file_hash': file_hash,
                'storage_type': self.storage_type,
                'metadata': metadata or {}
            }
            
        except Exception as e:
            return {'error': f'Upload failed: {str(e)}'}
    
    def _upload_local(self, file, filename):
        """Upload file to local storage"""
        os.makedirs(self.upload_folder, exist_ok=True)
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path
    
    def _upload_s3(self, file, filename):
        """Upload file to AWS S3"""
        bucket_name = self.config.get('AWS_BUCKET_NAME')
        if not bucket_name:
            raise Exception("S3 bucket name not configured")
        
        self.s3_client.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        return f"s3://{bucket_name}/{filename}"
    
    def _upload_gcs(self, file, filename):
        """Upload file to Google Cloud Storage"""
        bucket_name = self.config.get('GOOGLE_CLOUD_BUCKET_NAME')
        if not bucket_name:
            raise Exception("GCS bucket name not configured")
        
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)
        return f"gcs://{bucket_name}/{filename}"
    
    def _upload_azure(self, file, filename):
        """Upload file to Azure Blob Storage"""
        container_name = self.config.get('AZURE_CONTAINER_NAME')
        if not container_name:
            raise Exception("Azure container name not configured")
        
        blob_client = self.azure_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        blob_client.upload_blob(file, content_type=file.content_type, overwrite=True)
        return f"azure://{container_name}/{filename}"
    
    def download_file(self, file_path, local_path=None):
        """Download file from storage to local path"""
        try:
            if self.storage_type == 'local':
                if local_path:
                    shutil.copy2(file_path, local_path)
                    return local_path
                return file_path
            
            elif self.storage_type == 's3':
                return self._download_s3(file_path, local_path)
            elif self.storage_type == 'gcs':
                return self._download_gcs(file_path, local_path)
            elif self.storage_type == 'azure':
                return self._download_azure(file_path, local_path)
            
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def _download_s3(self, s3_path, local_path):
        """Download file from S3"""
        bucket_name = self.config.get('AWS_BUCKET_NAME')
        filename = s3_path.replace(f"s3://{bucket_name}/", "")
        
        if not local_path:
            local_path = os.path.join(self.upload_folder, f"temp_{filename}")
        
        self.s3_client.download_file(bucket_name, filename, local_path)
        return local_path
    
    def _download_gcs(self, gcs_path, local_path):
        """Download file from Google Cloud Storage"""
        bucket_name = self.config.get('GOOGLE_CLOUD_BUCKET_NAME')
        filename = gcs_path.replace(f"gcs://{bucket_name}/", "")
        
        if not local_path:
            local_path = os.path.join(self.upload_folder, f"temp_{filename}")
        
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.download_to_filename(local_path)
        return local_path
    
    def _download_azure(self, azure_path, local_path):
        """Download file from Azure Blob Storage"""
        container_name = self.config.get('AZURE_CONTAINER_NAME')
        filename = azure_path.replace(f"azure://{container_name}/", "")
        
        if not local_path:
            local_path = os.path.join(self.upload_folder, f"temp_{filename}")
        
        blob_client = self.azure_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        return local_path
    
    def delete_file(self, file_path):
        """Delete file from storage"""
        try:
            if self.storage_type == 'local':
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            elif self.storage_type == 's3':
                return self._delete_s3(file_path)
            elif self.storage_type == 'gcs':
                return self._delete_gcs(file_path)
            elif self.storage_type == 'azure':
                return self._delete_azure(file_path)
            
            return False
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False
    
    def _delete_s3(self, s3_path):
        """Delete file from S3"""
        bucket_name = self.config.get('AWS_BUCKET_NAME')
        filename = s3_path.replace(f"s3://{bucket_name}/", "")
        self.s3_client.delete_object(Bucket=bucket_name, Key=filename)
        return True
    
    def _delete_gcs(self, gcs_path):
        """Delete file from Google Cloud Storage"""
        bucket_name = self.config.get('GOOGLE_CLOUD_BUCKET_NAME')
        filename = gcs_path.replace(f"gcs://{bucket_name}/", "")
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.delete()
        return True
    
    def _delete_azure(self, azure_path):
        """Delete file from Azure Blob Storage"""
        container_name = self.config.get('AZURE_CONTAINER_NAME')
        filename = azure_path.replace(f"azure://{container_name}/", "")
        blob_client = self.azure_client.get_blob_client(
            container=container_name,
            blob=filename
        )
        blob_client.delete_blob()
        return True