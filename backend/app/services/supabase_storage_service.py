import os
import uuid
import requests
from supabase import create_client, Client
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseStorage(Storage):
    """
    Custom Django storage backend for Supabase Storage.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 21/09/2025
    """

    def __init__(self):
        """
        Create an instance of the Supabase Storage Service.
        """
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def _open(self, name, mode='rb'):
        """
        Open and return a file-like object for the given file name.
        
        :param name: File path/name
        :param mode: File open mode
        :return: File-like object
        """
        try:
            # Get the public URL
            url = self.url(name)
            
            # Download the file content
            response = requests.get(url)
            response.raise_for_status()
            
            # Return as ContentFile
            return ContentFile(response.content, name=name)
            
        except Exception as e:
            raise Exception(f"Failed to open file {name}: {e}")
    
    def _save(self, name: str, content: ContentFile) -> str:
        """
        Save file to Supabase storage.
        """
        try:
            # Read file content
            content.seek(0)
            file_data = content.read()
            
            # Try to upload with upsert=True to overwrite if exists
            try:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                            path=name,
                            file=file_data,
                            file_options={
                                "content-type": self._get_content_type(name),
                                "upsert": "true"  # Use string "true" in file_options
                            }
                        )
                return name
                
            except Exception as upload_error:
                # If upsert fails, try update instead
                if "already exists" in str(upload_error).lower() or "409" in str(upload_error):
                    try:
                        result = self.supabase.storage.from_(self.bucket_name).update(
                            path=name,
                            file=file_data,
                            file_options={"content-type": self._get_content_type(name)}
                        )
                        return name
                    except Exception as update_error:
                        # If update also fails, generate unique name
                        unique_name = self._get_unique_name(name)
                        result = self.supabase.storage.from_(self.bucket_name).upload(
                            path=unique_name,
                            file=file_data,
                            file_options={"content-type": self._get_content_type(unique_name)}
                        )
                        return unique_name
                else:
                    raise upload_error
                
        except Exception as e:
            raise Exception(f"Failed to save file to Supabase: {e}")
        
    def url(self, name):
        """
        Return public URL for the file.
        
        :param name: File path/name
        :return: Public URL string
        """
        if not name:
            return ""
            
        # Get public URL from Supabase
        try:
            result = self.supabase.storage.from_(self.bucket_name).get_public_url(name)
            return result
        except Exception as e:
            # Fallback to manual URL construction
            return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{name}"
        
    def delete(self, name: str) -> None:
        """
        Delete file from Supabase storage.
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([name])
        except Exception:
            pass
        
    def exists(self, name: str) -> bool:
        """
        Check if file exists in Supabase storage.
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).list(
                path=os.path.dirname(name) if os.path.dirname(name) else "",
                limit=1000 # type: ignore
            )
            
            if not result:
                return False
                
            # Check if the specific file exists in the result
            filename = os.path.basename(name)
            return any(file.get('name') == filename for file in result)
        except Exception:
            return False
        
    def size(self, name: str) -> int:
        """
        Get file size.
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).list(
                path=os.path.dirname(name) if os.path.dirname(name) else ""
            )
            
            # Get the images size 
            filename = os.path.basename(name)
            for file in result:
                if isinstance(file, dict) and file.get('name') == filename:
                    metadata = file.get('metadata', {})
                    if isinstance(metadata, dict):
                        return metadata.get('size', 0)
            return 0
        except Exception:
            return 0
        
    def _get_unique_name(self, name: str) -> str:
        """
        Generate unique filename if file already exists.
        """
        base_name, ext = os.path.splitext(name)
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}_{unique_id}{ext}"
        
    def _get_content_type(self, name: str) -> str:
        """
        Get content type based on file extension.
        """
        ext = os.path.splitext(name)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return content_types.get(ext, 'application/octet-stream')
    
class SupabaseStorageService:
    """
    Service class for direct Supabase storage operations.
    """
    
    def __init__(self):
        """
        Create an instance of the Supabase storage client.
        """
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
    
    def upload_image(self, file_path: str, storage_path: str) -> str:
        """
        Upload image file to Supabase storage.
        
        :param file_path: Local file path
        :param storage_path: Storage path in bucket
        :return: Public URL of uploaded file
        """
        try:
            with open(file_path, 'rb') as f:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": self._get_content_type(file_path)}
                )
            
            # Check if upload was successful
            if not result:
                raise Exception("Upload failed: No response received")
            
            return self.get_public_url(storage_path)
            
        except Exception as e:
            raise Exception(f"Failed to upload image: {e}")
    
    def get_public_url(self, storage_path: str) -> str:
        """
        Get public URL for stored file.
        """
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([storage_path])
            return result is not None
        except Exception:
            return False
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Get content type based on file extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return content_types.get(ext, 'application/octet-stream')